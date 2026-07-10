import type {
  GraphData, ComplianceReport, DiagnoseJob, MaintenanceEvent,
  LinkedDocument, RiskAssessment, User, LoginResponse,
} from './types';

export const DEMO_USERS: Record<string, { password: string; user: User }> = {
  technician: {
    password: 'tech123',
    user: { id: 'u-1', username: 'technician', role: 'technician', display_name: 'Alex Rivera' },
  },
  engineer: {
    password: 'eng123',
    user: { id: 'u-2', username: 'engineer', role: 'engineer', display_name: 'Jordan Chen' },
  },
  compliance_officer: {
    password: 'comp123',
    user: { id: 'u-3', username: 'compliance_officer', role: 'compliance_officer', display_name: 'Morgan Hayes' },
  },
  admin: {
    password: 'admin123',
    user: { id: 'u-4', username: 'admin', role: 'admin', display_name: 'Casey Brooks' },
  },
};

export function mockLogin(username: string, password: string): LoginResponse | null {
  const entry = DEMO_USERS[username];
  if (!entry || entry.password !== password) return null;
  return {
    access_token: `mock-jwt-${username}-${Date.now()}`,
    token_type: 'bearer',
    user: entry.user,
  };
}

export const MOCK_GRAPH: GraphData = {
  center: 'P-101A',
  nodes: [
    { id: 'P-101A', tag: 'P-101A', label: 'Centrifugal Pump P-101A', type: 'equipment', properties: { manufacturer: 'Flowserve', installed: '2019-03-15' }, confidence: 1.0 },
    { id: 'P-101B', tag: 'P-101B', label: 'Centrifugal Pump P-101B', type: 'equipment', properties: { manufacturer: 'Flowserve', installed: '2019-03-15' }, confidence: 1.0 },
    { id: 'V-201', tag: 'V-201', label: 'Pressure Vessel V-201', type: 'equipment', properties: { capacity: '5000L', pressure_rating: '150 PSI' }, confidence: 0.95 },
    { id: 'HX-301', tag: 'HX-301', label: 'Heat Exchanger HX-301', type: 'equipment', properties: { type: 'Shell & Tube' }, confidence: 0.88 },
    { id: 'DOC-001', tag: 'DOC-001', label: 'Pump Maintenance Manual Rev.4', type: 'document', properties: { pages: 142, revision: 4 }, confidence: 1.0 },
    { id: 'DOC-002', tag: 'DOC-002', label: 'Vibration Analysis Report Q2', type: 'document', properties: { pages: 28, date: '2025-06-15' }, confidence: 0.92 },
    { id: 'DOC-003', tag: 'DOC-003', label: 'API 610 Compliance Checklist', type: 'document', properties: { standard: 'API 610' }, confidence: 1.0 },
    { id: 'PROC-001', tag: 'PROC-001', label: 'Pump Alignment Procedure', type: 'procedure', properties: { version: '3.1', approved: true }, confidence: 1.0 },
    { id: 'PROC-002', tag: 'PROC-002', label: 'Emergency Shutdown Procedure', type: 'procedure', properties: { version: '2.0', approved: true }, confidence: 1.0 },
    { id: 'SYS-CW', tag: 'SYS-CW', label: 'Cooling Water System', type: 'system', properties: { area: 'Unit 100' }, confidence: 0.97 },
    { id: 'SYS-FW', tag: 'SYS-FW', label: 'Feed Water System', type: 'system', properties: { area: 'Unit 100' }, confidence: 0.85 },
    { id: 'COMP-SEAL', tag: 'COMP-SEAL', label: 'Mechanical Seal Assembly', type: 'component', properties: { part_no: 'MS-4400' }, confidence: 0.93 },
    { id: 'COMP-IMP', tag: 'COMP-IMP', label: 'Impeller - 316SS', type: 'component', properties: { material: '316 Stainless Steel' }, confidence: 0.91 },
    { id: 'FM-001', tag: 'FM-001', label: 'Bearing Failure', type: 'failure_mode', properties: { mtbf_hours: 26000 }, confidence: 0.78 },
    { id: 'FM-002', tag: 'FM-002', label: 'Seal Leakage', type: 'failure_mode', properties: { mtbf_hours: 18000 }, confidence: 0.65 },
    { id: 'FM-003', tag: 'FM-003', label: 'Cavitation Damage', type: 'failure_mode', properties: { mtbf_hours: 35000 }, confidence: 0.72 },
    { id: 'C-401', tag: 'C-401', label: 'Compressor C-401', type: 'equipment', properties: { type: 'Centrifugal' }, confidence: 0.89 },
    { id: 'T-501', tag: 'T-501', label: 'Storage Tank T-501', type: 'equipment', properties: { capacity: '20000L' }, confidence: 0.94 },
  ],
  edges: [
    { id: 'e1', source: 'P-101A', target: 'V-201', relationship: 'feeds', confidence: 0.98 },
    { id: 'e2', source: 'P-101A', target: 'DOC-001', relationship: 'documented_by', confidence: 1.0 },
    { id: 'e3', source: 'P-101A', target: 'PROC-001', relationship: 'maintained_by', confidence: 0.95 },
    { id: 'e4', source: 'P-101A', target: 'SYS-CW', relationship: 'part_of', confidence: 0.97 },
    { id: 'e5', source: 'P-101A', target: 'COMP-SEAL', relationship: 'contains', confidence: 0.93 },
    { id: 'e6', source: 'P-101A', target: 'COMP-IMP', relationship: 'contains', confidence: 0.91 },
    { id: 'e7', source: 'P-101A', target: 'FM-001', relationship: 'susceptible_to', confidence: 0.78 },
    { id: 'e8', source: 'P-101A', target: 'FM-002', relationship: 'susceptible_to', confidence: 0.65 },
    { id: 'e9', source: 'P-101A', target: 'FM-003', relationship: 'susceptible_to', confidence: 0.72 },
    { id: 'e10', source: 'P-101A', target: 'P-101B', relationship: 'redundant_with', confidence: 1.0 },
    { id: 'e11', source: 'P-101B', target: 'SYS-CW', relationship: 'part_of', confidence: 0.97 },
    { id: 'e12', source: 'V-201', target: 'HX-301', relationship: 'feeds', confidence: 0.88 },
    { id: 'e13', source: 'V-201', target: 'DOC-003', relationship: 'documented_by', confidence: 1.0 },
    { id: 'e14', source: 'COMP-SEAL', target: 'FM-002', relationship: 'causes', confidence: 0.60 },
    { id: 'e15', source: 'DOC-002', target: 'P-101A', relationship: 'references', confidence: 0.92 },
    { id: 'e16', source: 'PROC-002', target: 'SYS-CW', relationship: 'applies_to', confidence: 0.90 },
    { id: 'e17', source: 'HX-301', target: 'SYS-FW', relationship: 'part_of', confidence: 0.85 },
    { id: 'e18', source: 'SYS-CW', target: 'C-401', relationship: 'supplies', confidence: 0.89 },
    { id: 'e19', source: 'SYS-FW', target: 'T-501', relationship: 'supplies', confidence: 0.94 },
    { id: 'e20', source: 'P-101A', target: 'DOC-002', relationship: 'analyzed_in', confidence: 0.92 },
  ],
};

export const MOCK_MAINTENANCE_EVENTS: MaintenanceEvent[] = [
  { id: 'm1', date: '2026-07-08', type: 'inspection', description: 'Routine vibration analysis - all readings within spec', severity: 'low', technician: 'A. Rivera' },
  { id: 'm2', date: '2026-06-22', type: 'repair', description: 'Replaced mechanical seal due to minor leakage detected during walkdown', severity: 'medium', technician: 'A. Rivera' },
  { id: 'm3', date: '2026-05-15', type: 'calibration', description: 'Pressure transmitter PT-101 recalibrated - 0.2% drift corrected', severity: 'low', technician: 'B. Martinez' },
  { id: 'm4', date: '2026-04-01', type: 'inspection', description: 'Annual pump overhaul - bearings inspected, within tolerance', severity: 'low', technician: 'A. Rivera' },
  { id: 'm5', date: '2026-02-10', type: 'incident', description: 'Unexpected high vibration alarm - bearing race defect identified via spectrum analysis', severity: 'high', technician: 'J. Chen' },
  { id: 'm6', date: '2025-12-15', type: 'replacement', description: 'Both drive-end and non-drive-end bearings replaced (SKF 6310-2RS1)', severity: 'medium', technician: 'A. Rivera' },
  { id: 'm7', date: '2025-11-01', type: 'inspection', description: 'Quarterly thermographic survey - no abnormal heat patterns', severity: 'low', technician: 'C. Brooks' },
  { id: 'm8', date: '2025-09-20', type: 'calibration', description: 'Flow meter FT-101 calibration verification - passed', severity: 'low', technician: 'B. Martinez' },
];

export const MOCK_LINKED_DOCS: LinkedDocument[] = [
  { id: 'DOC-001', title: 'Pump Maintenance Manual Rev.4', type: 'manual', relevance: 0.98, pages: 142, last_updated: '2025-08-10' },
  { id: 'DOC-002', title: 'Vibration Analysis Report Q2 2026', type: 'report', relevance: 0.95, pages: 28, last_updated: '2026-06-15' },
  { id: 'DOC-003', title: 'API 610 Compliance Checklist', type: 'regulation', relevance: 0.90, pages: 12, last_updated: '2025-01-20' },
  { id: 'DOC-004', title: 'P&ID Drawing - Unit 100 Cooling Water', type: 'drawing', relevance: 0.85, pages: 3, last_updated: '2024-06-01' },
  { id: 'DOC-005', title: 'Seal Replacement Procedure SP-2200', type: 'procedure', relevance: 0.82, pages: 8, last_updated: '2025-04-12' },
  { id: 'DOC-006', title: 'Root Cause Analysis - Feb 2026 Vibration Event', type: 'report', relevance: 0.78, pages: 15, last_updated: '2026-03-01' },
];

export const MOCK_COMPLIANCE: ComplianceReport = {
  score: 78,
  checked: 156,
  missing: 12,
  gaps: [
    { equipment_tag: 'P-101A', equipment_name: 'Centrifugal Pump P-101A', regulation: 'API 610 12th Ed.', status: 'amber', missing_evidence: ['Bearing clearance measurement record', 'Seal face flatness certificate'], last_checked: '2026-06-28' },
    { equipment_tag: 'V-201', equipment_name: 'Pressure Vessel V-201', regulation: 'ASME BPVC Sec. VIII', status: 'red', missing_evidence: ['Annual hydrostatic test report', 'Relief valve certification', 'NDE thickness survey'], last_checked: '2026-05-15' },
    { equipment_tag: 'HX-301', equipment_name: 'Heat Exchanger HX-301', regulation: 'TEMA Standards', status: 'amber', missing_evidence: ['Tube bundle inspection report'], last_checked: '2026-06-01' },
    { equipment_tag: 'C-401', equipment_name: 'Compressor C-401', regulation: 'API 617', status: 'red', missing_evidence: ['Rotor balance report', 'Alignment verification record', 'Oil analysis report Q2'], last_checked: '2026-04-20' },
    { equipment_tag: 'T-501', equipment_name: 'Storage Tank T-501', regulation: 'API 653', status: 'green', missing_evidence: [], last_checked: '2026-07-01' },
    { equipment_tag: 'P-101B', equipment_name: 'Centrifugal Pump P-101B', regulation: 'API 610 12th Ed.', status: 'green', missing_evidence: [], last_checked: '2026-07-05' },
    { equipment_tag: 'SYS-CW', equipment_name: 'Cooling Water System', regulation: 'Internal SOP-400', status: 'amber', missing_evidence: ['Water chemistry log June 2026'], last_checked: '2026-06-30' },
    { equipment_tag: 'PROC-002', equipment_name: 'Emergency Shutdown Procedure', regulation: 'OSHA 1910.119', status: 'green', missing_evidence: [], last_checked: '2026-07-02' },
  ],
};

export const MOCK_RISK: RiskAssessment = {
  tag: 'P-101A',
  equipment_name: 'Centrifugal Pump P-101A',
  overall_risk: 0.42,
  factors: [
    { name: 'Age & Condition', score: 0.35, weight: 0.25, description: 'Equipment is 7 years old, within expected service life' },
    { name: 'Failure History', score: 0.55, weight: 0.30, description: 'One significant vibration event in last 12 months' },
    { name: 'Maintenance Compliance', score: 0.30, weight: 0.20, description: 'Mostly up to date, minor documentation gaps' },
    { name: 'Operating Conditions', score: 0.45, weight: 0.15, description: 'Occasionally operates near cavitation margin' },
    { name: 'Criticality', score: 0.60, weight: 0.10, description: 'Has redundant backup (P-101B) but is primary unit' },
  ],
  trend: 'stable',
};

export const MOCK_DIAGNOSE_JOB: DiagnoseJob = {
  job_id: 'j-501',
  status: 'completed',
  equipment_tag: 'P-101A',
  steps: [
    { id: 's1', worker: 'retriever', action: 'Searching knowledge base', detail: 'Querying maintenance records and equipment specifications for P-101A', timestamp: Date.now() - 12000, status: 'completed', duration_ms: 1800 },
    { id: 's2', worker: 'retriever', action: 'Fetching vibration data', detail: 'Retrieved 24 vibration analysis reports spanning 2024-2026', timestamp: Date.now() - 10200, status: 'completed', duration_ms: 1200 },
    { id: 's3', worker: 'analyzer', action: 'Pattern analysis', detail: 'Analyzing vibration spectrum trends - identified 1x and 2x RPM peaks', timestamp: Date.now() - 9000, status: 'completed', duration_ms: 2500 },
    { id: 's4', worker: 'analyzer', action: 'Cross-referencing failure modes', detail: 'Comparing patterns against known failure signatures in OREDA database', timestamp: Date.now() - 6500, status: 'completed', duration_ms: 1800 },
    { id: 's5', worker: 'reasoner', action: 'Synthesizing diagnosis', detail: 'Combining equipment history, vibration patterns, and failure mode analysis', timestamp: Date.now() - 4700, status: 'completed', duration_ms: 2200 },
    { id: 's6', worker: 'recommender', action: 'Generating recommendations', detail: 'Formulating maintenance actions based on diagnosis and risk assessment', timestamp: Date.now() - 2500, status: 'completed', duration_ms: 1500 },
  ],
  result: {
    diagnosis: 'Early-stage bearing wear detected on drive-end bearing. Vibration spectrum shows increasing 2x RPM component consistent with inner race defect progression. Current severity: moderate. Estimated time to failure threshold: 60-90 days at current operating conditions.',
    confidence: 0.87,
    recommended_actions: [
      'Schedule bearing replacement within 45 days (before next quarterly shutdown)',
      'Increase vibration monitoring frequency to weekly',
      'Verify lubrication quality - obtain oil sample for analysis',
      'Prepare P-101B for potential switchover if degradation accelerates',
    ],
    supporting_evidence: [
      { doc_id: 'DOC-002', passage_id: 'p-12', page: 8, title: 'Vibration Analysis Report Q2', snippet: '2x RPM amplitude increased 40% compared to baseline' },
      { doc_id: 'DOC-006', passage_id: 'p-3', page: 4, title: 'RCA - Feb 2026 Event', snippet: 'Similar spectral pattern preceded the February bearing failure event' },
      { doc_id: 'DOC-001', passage_id: 'p-45', page: 67, title: 'Pump Maintenance Manual', snippet: 'Bearing replacement interval: 24,000 operating hours or upon detection of defect frequencies' },
    ],
  },
};

export const MOCK_SSE_RESPONSES: Record<string, Array<{ event: string; data: Record<string, unknown>; delay: number }>> = {
  default: [
    { event: 'token', data: { text: 'Pump ' }, delay: 50 },
    { event: 'token', data: { text: 'P-101A ' }, delay: 80 },
    { event: 'token', data: { text: 'is a ' }, delay: 60 },
    { event: 'token', data: { text: 'centrifugal ' }, delay: 70 },
    { event: 'token', data: { text: 'pump ' }, delay: 50 },
    { event: 'token', data: { text: 'installed ' }, delay: 60 },
    { event: 'token', data: { text: 'in the ' }, delay: 50 },
    { event: 'token', data: { text: 'Cooling Water ' }, delay: 70 },
    { event: 'token', data: { text: 'System. ' }, delay: 80 },
    { event: 'citation', data: { doc_id: 'DOC-001', passage_id: 'p-1', page: 3 }, delay: 30 },
    { event: 'token', data: { text: 'The most ' }, delay: 60 },
    { event: 'token', data: { text: 'recent vibration ' }, delay: 70 },
    { event: 'token', data: { text: 'analysis from ' }, delay: 60 },
    { event: 'token', data: { text: 'June 2026 ' }, delay: 80 },
    { event: 'token', data: { text: 'shows elevated ' }, delay: 70 },
    { event: 'token', data: { text: '2x RPM ' }, delay: 60 },
    { event: 'token', data: { text: 'components, ' }, delay: 50 },
    { event: 'token', data: { text: 'indicating ' }, delay: 60 },
    { event: 'token', data: { text: 'possible early-stage ' }, delay: 80 },
    { event: 'token', data: { text: 'bearing wear. ' }, delay: 70 },
    { event: 'citation', data: { doc_id: 'DOC-002', passage_id: 'p-12', page: 8 }, delay: 30 },
    { event: 'token', data: { text: 'The mechanical ' }, delay: 60 },
    { event: 'token', data: { text: 'seal was ' }, delay: 50 },
    { event: 'token', data: { text: 'replaced in ' }, delay: 60 },
    { event: 'token', data: { text: 'June 2026 ' }, delay: 70 },
    { event: 'token', data: { text: 'due to ' }, delay: 50 },
    { event: 'token', data: { text: 'minor leakage ' }, delay: 60 },
    { event: 'token', data: { text: 'detected during ' }, delay: 70 },
    { event: 'token', data: { text: 'routine walkdown.' }, delay: 80 },
    { event: 'citation', data: { doc_id: 'DOC-005', passage_id: 'p-2', page: 2 }, delay: 30 },
    { event: 'agent_trigger', data: { worker: 'diagnose', job_id: 'j-501' }, delay: 200 },
    { event: 'done', data: { answer_id: 'a-771' }, delay: 100 },
  ],
};

export const MORNING_ALERTS = [
  { id: 'alert-1', severity: 'high' as const, message: 'P-101A vibration trending upward — bearing inspection recommended within 45 days', tag: 'P-101A' },
  { id: 'alert-2', severity: 'medium' as const, message: 'V-201 hydrostatic test overdue — compliance gap flagged', tag: 'V-201' },
  { id: 'alert-3', severity: 'low' as const, message: 'C-401 oil analysis due next week', tag: 'C-401' },
];
