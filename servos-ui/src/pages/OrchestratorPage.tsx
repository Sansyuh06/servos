import { useState } from 'react'
import PageTransition from '@/components/PageTransition'
import { Wrench } from 'lucide-react'
import { startScanJob, getScanStatus, cancelScan } from '@/api/client'

export default function OrchestratorPage() {
    const [target, setTarget] = useState('')
    const [selected, setSelected] = useState<string[]>([])
    const [results, setResults] = useState<any[]>([])
    const [running, setRunning] = useState(false)
    const [jobId, setJobId] = useState<string | null>(null)

    const tools = [
        { id: 'fs-scan', label: 'File System' },
        { id: 'network-scan', label: 'Network' },
        { id: 'memory-scan', label: 'Memory' },
        { id: 'log-analysis', label: 'Logs' },
        { id: 'registry-analysis', label: 'Registry' },
        { id: 'deep-malware', label: 'Deep Malware' },
    ]

    const toggleTool = (id: string) => {
        setSelected((s) => s.includes(id) ? s.filter(x => x !== id) : [...s, id])
    }

    const pollInterval = 2000

    const run = async () => {
        setResults([])
        setRunning(true)
        try {
            const job = await startScanJob({ tools: selected, target })
            setJobId(job.job_id)
            // poll status
            const poll = async () => {
                try {
                    const st = await getScanStatus(job.job_id)
                    setResults(st.results || [])
                    if(st.status === 'running') {
                        setTimeout(poll, pollInterval)
                    } else {
                        setRunning(false)
                    }
                } catch (err) {
                    console.error(err)
                    setRunning(false)
                }
            }
            poll()
        } catch (e) {
            console.error(e)
            setRunning(false)
        }
    }

    return (
        <PageTransition>
            <div className="h-full overflow-y-auto p-6 max-w-2xl">
                <h1 className="text-xl font-bold text-cream-bright mb-6 flex items-center gap-2">
                    <Wrench size={20} className="text-accent" /> Scan Orchestrator
                </h1>
                <div className="space-y-4">
                    <div>
                        <label className="block text-[10px] font-semibold text-cream-dim uppercase tracking-wider mb-1">
                            Target path
                        </label>
                        <input
                            type="text"
                            value={target}
                            onChange={e => setTarget(e.target.value)}
                            className="w-full bg-servos-bg border border-servos-border rounded-lg py-2 px-3 text-xs text-cream font-mono focus:border-accent focus:outline-none"
                        />
                    </div>
                    <div className="space-y-1">
                        {tools.map(t => (
                            <label key={t.id} className="flex items-center gap-2 text-xs">
                                <input
                                    type="checkbox"
                                    checked={selected.includes(t.id)}
                                    onChange={() => toggleTool(t.id)}
                                    className="accent-accent"
                                />
                                {t.label}
                            </label>
                        ))}
                    </div>
                    <div className="flex items-center gap-2">
                        <button
                            disabled={running || selected.length === 0 || !target}
                            onClick={run}
                            className="px-4 py-2 bg-accent hover:bg-accent-dark text-white text-sm font-semibold rounded-lg transition-colors disabled:opacity-50"
                        >
                            {running ? 'Running...' : 'Run Scans'}
                        </button>
                        {running && jobId && (
                            <button
                                onClick={() => { cancelScan(jobId); setRunning(false); }}
                                className="px-2 py-1 bg-danger hover:bg-danger-dark text-white text-xs rounded-lg"
                            >
                                Cancel
                            </button>
                        )}
                    </div>
                    <div className="mt-6 space-y-2">
                        {results.map((r, idx) => (
                            <div key={idx} className="bg-servos-surface border border-servos-border rounded-lg p-3 text-xs">
                                <strong>{r.tool}</strong>: {JSON.stringify(r.result).slice(0,200)}
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </PageTransition>
    )
}
