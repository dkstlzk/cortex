import signal
import sys
import structlog
from rq import Worker

from backend.shared.config import settings
from backend.shared.logging import setup_logging
from backend.shared.redis_client import redis_conn
from backend.shared.constants import INGESTION_QUEUE_NAME
from backend.shared.database import engine
from backend.shared.neo4j_client import neo4j_driver
from backend.shared.qdrant_client import qdrant_client

logger = structlog.get_logger(__name__)

def cleanup():
    """
    Close all infrastructure connections gracefully.
    """
    try:
        neo4j_driver.close()
        redis_conn.close()
        engine.dispose()
        qdrant_client.close()
        logger.info("Infrastructure connections closed successfully.")
    except Exception as e:
        logger.error("Error during shutdown cleanup", error=str(e))

def shutdown_handler(signum, frame):
    """
    Handle graceful shutdown on SIGINT/SIGTERM.
    """
    logger.info("Shutdown signal received. Initiating graceful shutdown...", signal=signum)
    cleanup()
    sys.exit(0)

def main():
    """
    Bootstrap the ingestion worker.
    """
    setup_logging()
    logger.info("Starting CORTEX Ingestion Worker...", version=settings.VERSION)
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)
    
    try:
        # Verify redis connection is active before starting
        redis_conn.ping()
        logger.info("Connected to Redis successfully.")
        
        # Start a dummy HTTP server in a background thread to satisfy Render's Web Service port binding health checks
        import os
        import threading
        from http.server import HTTPServer, BaseHTTPRequestHandler
        
        port_str = os.environ.get("PORT")
        if port_str:
            class HealthCheckHandler(BaseHTTPRequestHandler):
                def do_GET(self):
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b"OK")
            
            def run_dummy_server():
                try:
                    server = HTTPServer(("0.0.0.0", int(port_str)), HealthCheckHandler)
                    logger.info("Started dummy health check server", port=port_str)
                    server.serve_forever()
                except Exception as e:
                    logger.warning("Failed to start dummy server", error=str(e))
                    
            threading.Thread(target=run_dummy_server, daemon=True).start()

        # Initialize and run the RQ Worker
        # We listen only to the designated ingestion queue
        worker = Worker(
            [INGESTION_QUEUE_NAME],
            connection=redis_conn,
            log_job_description=False # Handled by structlog
        )
        
        logger.info("Worker is ready and listening for jobs.", queue=INGESTION_QUEUE_NAME)
        worker.work(with_scheduler=False) # Scheduler not needed for P1
        
    except Exception as e:
        logger.error("Worker failed to start or crashed", error=str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
