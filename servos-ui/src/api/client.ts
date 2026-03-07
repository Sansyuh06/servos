/* Servos API Client — talks to the Python FastAPI backend */

const BASE = '/api'

// ── Chat (RAG) ──

export interface ChatAction {
    tool_id: string
    tool_name: string
    icon: string
    status: string
    summary: string
}

export interface ChatResponse {
    response: string
    sources: { type: string; label: string; data: any }[]
    model: string
    actions?: ChatAction[]
}

export async function sendChatMessage(
    message: string,
    history?: { role: string; content: string }[]
): Promise<ChatResponse> {
    const res = await fetch(`${BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, history: history || [] }),
    })
    if (!res.ok) throw new Error(`Chat error: ${res.status}`)
    return res.json()
}

// ── Generic request helper ──

async function request<T>(path: string, opts?: RequestInit): Promise<T> {
    const res = await fetch(`${BASE}${path}`, {
        headers: { 'Content-Type': 'application/json' },
        ...opts,
    })
    if (!res.ok) {
        const err = await res.text().catch(() => res.statusText)
        throw new Error(`API ${res.status}: ${err}`)
    }
    return res.json()
}

/* ── Devices ── */
export interface Device {
    path: string
    name: string
    mount_point: string
    filesystem: string
    capacity_bytes: number
    used_bytes: number
    is_removable: boolean
    serial_number: string
}

export async function getDevices() {
    return request<{ devices: Device[] }>('/devices')
}

/* ── Scan ── */
export interface ScanResult {
    total_files: number
    total_dirs: number
    total_size: number
    hidden_files: number
    suspicious_files: { name: string; path: string; reason: string; size: number; entropy: number }[]
    file_types: Record<string, number>
    malware: {
        risk_level: string
        files_scanned: number
        suspicious_count: number
        indicators: {
            type: string; file: string; description: string
            severity: string; rule: string; confidence: number
        }[]
    }
}

export async function quickScan(targetPath: string) {
    return request<ScanResult>('/scan', {
        method: 'POST',
        body: JSON.stringify({ target_path: targetPath }),
    })
}

/* ── Investigation ── */
export interface InvestigateRequest {
    device_path: string
    mount_point: string
    device_name?: string
    mode?: string
    investigator?: string
}

export interface InvestigationStatus {
    status: string
    progress: number
    step: string
    result: any
    error: string | null
}

export async function startInvestigation(req: InvestigateRequest) {
    return request<{ case_id: string; status: string }>('/investigate', {
        method: 'POST',
        body: JSON.stringify(req),
    })
}

export async function getInvestigationStatus(caseId: string) {
    return request<InvestigationStatus>(`/investigate/${caseId}/status`)
}

/* ── Cases ── */
export interface CaseSummary {
    id: string
    created_at: string
    investigator: string
    mode: string
    status: string
    report_path: string
    device_info: Record<string, any>
}

export async function getCases() {
    return request<{ cases: CaseSummary[] }>('/cases')
}

export async function getCaseDetail(caseId: string) {
    return request<any>(`/cases/${caseId}`)
}

/* ── Reports ── */
export function getReportUrl(caseId: string, fmt: 'pdf' | 'json' | 'txt') {
    return `${BASE}/reports/${caseId}/${fmt}`
}

/* ── Settings ── */
export async function getSettings() {
    return request<{ settings: Record<string, any> }>('/settings')
}

export async function updateSettings(settings: Record<string, any>) {
    return request<{ settings: Record<string, any> }>('/settings', {
        method: 'PUT',
        body: JSON.stringify({ settings }),
    })
}

/* ── LLM ── */
export async function getLLMStatus() {
    return request<{ available: boolean; model: string; base_url: string }>('/llm/status')
}

/* ── Alerts / Monitoring ── */
export interface AlertItem {
    event_type: string
    risk: string
    message: string
    timestamp: string
    [key: string]: any
}

export async function getAlerts(limit: number = 50) {
    return request<{ alerts: AlertItem[] }>(`/alerts?limit=${limit}`)
}

/* ── Multi-scan Orchestrator ── */
export interface ScanJob {
    job_id: string
    status: string
}

export interface ScanStatus extends ScanJob {
    tools: string[]
    target: string
    progress: number
    results: any[]
    start_time?: string
    end_time?: string
}

export async function startScanJob(body: { tools: string[]; target: string }): Promise<ScanJob> {
    return request<ScanJob>('/multiscan', {
        method: 'POST',
        body: JSON.stringify(body),
    })
}

export async function getScanStatus(jobId: string): Promise<ScanStatus> {
    return request<ScanStatus>(`/multiscan/${jobId}/status`)
}

export async function cancelScan(jobId: string): Promise<{ status: string }> {
    return request<{ status: string }>(`/multiscan/${jobId}/cancel`, { method: 'POST' })
}

/* ── Playbooks ── */
export async function getPlaybooks() {
    return request<{ playbooks: { name: string; description: string; version: string; steps: number }[] }>('/playbooks')
}
