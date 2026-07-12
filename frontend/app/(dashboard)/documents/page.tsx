'use client';

import { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FolderCog, CheckCircle2, CloudUpload, File, AlertCircle } from 'lucide-react';
import { FadeIn } from '@/components/animations/fade-in';
import { useAuth } from '@/lib/auth-context';
import { PageTransition } from '@/components/animations/page-transition';
import { uploadDocument } from '@/lib/api';
import { cn } from '@/lib/utils';

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  status: 'uploading' | 'processing' | 'complete' | 'error';
  progress: number;
  documentId?: string;
  error?: string;
}

export default function DocumentsPage() {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { hasPermission } = useAuth();

  const handleUpload = async (file: File) => {
    const id = `${file.name}-${Date.now()}`;
    const entry: UploadedFile = { id, name: file.name, size: file.size, status: 'uploading', progress: 50 };
    setFiles((prev) => [...prev, entry]);

    try {
      const result = await uploadDocument(file);
      setFiles((prev) =>
        prev.map((f) =>
          f.id === id ? { ...f, status: 'complete', progress: 100, documentId: result.document_id } : f,
        ),
      );
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Upload failed';
      const isConnectionError = message.includes('Failed to fetch') || message.includes('NetworkError');
      setFiles((prev) =>
        prev.map((f) =>
          f.id === id
            ? { ...f, status: 'error', progress: 0, error: isConnectionError ? 'Cannot reach the CORTEX API. Is the backend running and NEXT_PUBLIC_API_URL correct?' : message }
            : f,
        ),
      );
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    Array.from(e.dataTransfer.files).forEach(handleUpload);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    Array.from(e.target.files || []).forEach(handleUpload);
  };

  return (
    <PageTransition>
      <div className="p-6 space-y-6 max-w-4xl mx-auto">
        <FadeIn>
          <p className="eyebrow">Ingestion · index pipeline</p>
          <div className="flex items-center gap-3 mt-2">
            <div className="w-10 h-10 rounded-md border border-line bg-signal-soft flex items-center justify-center">
              <FolderCog className="w-5 h-5 text-signal" />
            </div>
            <div>
              <h1 className="font-display text-3xl font-medium text-ink">Document Library</h1>
              <p className="text-sm text-muted">Feed engineering documents into the Cortex knowledge graph</p>
            </div>
          </div>
        </FadeIn>

        {hasPermission('documents:upload') && (
          <FadeIn delay={0.1}>
            <div
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
              className={cn(
                'relative rounded-lg p-10 text-center transition-all overflow-hidden',
                dragOver ? 'border-2 border-signal bg-signal-soft' : 'border-2 border-dashed border-line hover:border-signal/50',
              )}
            >
              {dragOver && <div className="absolute inset-0 blueprint blueprint-drift pointer-events-none" />}
              <input
                ref={fileInputRef}
                type="file"
                multiple
                onChange={handleFileSelect}
                className="hidden"
                accept=".pdf,.doc,.docx,.txt,.csv,.xlsx"
              />
              <motion.div animate={dragOver ? { y: [-2, 2, -2] } : {}} transition={{ duration: 1, repeat: Infinity }}>
                <CloudUpload className={cn('w-11 h-11 mx-auto mb-3', dragOver ? 'text-signal' : 'text-faint')} />
              </motion.div>
              <p className="text-sm text-ink">
                Drop files here, or{' '}
                <button onClick={() => fileInputRef.current?.click()} className="text-signal font-medium hover:underline">
                  browse
                </button>
              </p>
              <p className="font-mono text-[0.62rem] text-faint mt-2 uppercase tracking-wider">pdf · doc · docx · txt · csv · xlsx</p>
            </div>
          </FadeIn>
        )}

        <AnimatePresence>
          {files.length > 0 && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-2">
              <p className="eyebrow">Queue</p>
              {files.map((file) => (
                <motion.div
                  key={file.id}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex items-center gap-3 p-3 panel rounded-md"
                >
                  <File className="w-4 h-4 text-faint shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-ink truncate">{file.name}</p>
                    {file.status === 'uploading' && (
                      <div className="mt-1.5 h-1 bg-base rounded-full overflow-hidden">
                        <motion.div className="h-full bg-signal rounded-full" animate={{ width: `${file.progress}%` }} />
                      </div>
                    )}
                    {file.status === 'error' && <p className="text-xs text-ember mt-0.5">{file.error}</p>}
                    {file.documentId && <p className="font-mono text-[0.62rem] text-faint mt-0.5">id · {file.documentId}</p>}
                  </div>
                  {file.status === 'complete' && <CheckCircle2 className="w-4 h-4 text-mint shrink-0" />}
                  {file.status === 'uploading' && <span className="data-num text-xs text-muted shrink-0">{Math.round(file.progress)}%</span>}
                  {file.status === 'error' && <AlertCircle className="w-4 h-4 text-ember shrink-0" />}
                </motion.div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>

        {files.length === 0 && (
          <FadeIn delay={0.2}>
            <div className="text-center py-12">
              <FolderCog className="w-12 h-12 mx-auto mb-3 text-line-strong" />
              <p className="text-sm text-muted">Upload documents above to start indexing.</p>
              <p className="font-mono text-[0.62rem] text-faint mt-1 uppercase tracking-wider">parsed → chunked → embedded → graphed</p>
            </div>
          </FadeIn>
        )}
      </div>
    </PageTransition>
  );
}
