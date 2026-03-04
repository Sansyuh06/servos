import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getCaseDetail, getReportUrl } from '@/api/client'
import PageTransition from '@/components/PageTransition'
import {
    FileText, Download, Shield, HardDrive, Hash, Clock,
    AlertTriangle, CheckCircle2, ChevronLeft
} from 'lucide-react'

export default function ReportPage() {
    const { caseId } = useParams()
    const navigate = useNavigate()
    const [data, setData] = useState<any>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        if(caseId) {
            getCaseDetail(caseId)
                .then((d) => { setData(d); setLoading(false) })
                .catch(() => setLoading(false))
        }
    }, [caseId])

    if(loading) {
        return (
            <PageTransition>
                <div className="h-full flex items-center justify-center text-cream-dim">Loading report...</div>
            </PageTransition>
        )
    }

    const findings = data?.findings || {}
    const interpretation = data?.interpretation || {}
    const device = data?.device_info || {}

    return (
        <PageTransition>
            <div className="h-full overflow-y-auto">
                {/* Header */}
                <div className="sticky top-0 z-10 bg-servos-bg border-b border-servos-border-dim px-6 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <button
                            onClick={() => navigate(-1)}
                            className="p-1.5 rounded-md hover:bg-servos-hover text-cream-dim transition-colors"
                        >
                            <ChevronLeft size={16} />
                        </button>
                        <div>
                            <h1 className="text-lg font-bold text-cream-bright">Forensic Report</h1>
                            <p className="text-[10px] text-cream-dim font-mono">{caseId}</p>
                        </div>
                    </div>
                    <div className="flex gap-2">
                        <a
                            href={caseId ? getReportUrl(caseId, 'pdf') : '#'}
                            className="flex items-center gap-1.5 px-3 py-1.5 bg-accent hover:bg-accent-dark text-white text-[11px] font-semibold rounded-md transition-colors"
                        >
                            <Download size={12} /> Export PDF
                        </a>
                        <a
                            href={caseId ? getReportUrl(caseId, 'json') : '#'}
                            className="flex items-center gap-1.5 px-3 py-1.5 bg-servos-surface border border-servos-border text-cream-dim text-[11px] font-semibold rounded-md hover:text-cream transition-colors"
                        >
                            <Download size={12} /> Export JSON
                        </a>
                    </div>
                </div>

                <div className="p-6 max-w-4xl mx-auto space-y-6">
                    {/* Executive Summary */}
                    <section className="bg-servos-surface border border-servos-border rounded-lg p-5">
                        <h2 className="text-sm font-semibold text-cream-bright mb-3 flex items-center gap-2">
                            <Shield size={14} className="text-accent" /> Executive Summary
                        </h2>
                        <p className="text-xs text-cream leading-relaxed">
                            {interpretation?.summary || 'No summary available.'}
                        </p>
                        <div className="mt-3 flex items-center gap-2">
                            <span className="text-[10px] text-cream-dim uppercase tracking-wider">Risk Assessment:</span>
                            <span className={`px-2 py-0.5 rounded-md text-[10px] font-bold uppercase ${interpretation?.risk === 'CRITICAL' ? 'bg-danger-muted text-danger border border-danger/20'
                                    : interpretation?.risk === 'HIGH' ? 'bg-danger-muted text-danger border border-danger/20'
                                        : 'bg-success-muted text-success border border-success/20'
                                }`}>
                                {interpretation?.risk || 'Unknown'}
                            </span>
                        </div>
                    </section>

                    {/* Device Metadata */}
                    <section className="bg-servos-surface border border-servos-border rounded-lg p-5">
                        <h2 className="text-sm font-semibold text-cream-bright mb-3 flex items-center gap-2">
                            <HardDrive size={14} className="text-accent" /> Device Metadata
                        </h2>
                        <div className="grid grid-cols-2 gap-3 text-xs">
                            {Object.entries(device).map(([k, v]) => (
                                <div key={k} className="flex justify-between py-1 border-b border-servos-border-dim/50">
                                    <span className="text-cream-dim capitalize">{k.replace(/_/g, ' ')}</span>
                                    <span className="text-cream font-mono text-[11px]">{String(v)}</span>
                                </div>
                            ))}
                        </div>
                    </section>

                    {/* Hash Table */}
                    {findings?.integrity_hashes && (
                        <section className="bg-servos-surface border border-servos-border rounded-lg p-5">
                            <h2 className="text-sm font-semibold text-cream-bright mb-3 flex items-center gap-2">
                                <Hash size={14} className="text-accent" /> Evidence Integrity Hashes
                            </h2>
                            <p className="text-[10px] text-cream-dim mb-2">SHA-256 hashes for evidence preservation</p>
                            <div className="max-h-48 overflow-y-auto">
                                {Object.entries(findings.integrity_hashes).slice(0, 20).map(([file, hash]) => (
                                    <div key={file} className="flex gap-3 py-1 border-b border-servos-border-dim/30 text-[10px]">
                                        <span className="text-cream truncate max-w-[40%]">{file}</span>
                                        <span className="text-cream-dim font-mono">{String(hash).slice(0, 16)}...</span>
                                    </div>
                                ))}
                            </div>
                        </section>
                    )}

                    {/* Timeline */}
                    {findings?.timeline_events?.length > 0 && (
                        <section className="bg-servos-surface border border-servos-border rounded-lg p-5">
                            <h2 className="text-sm font-semibold text-cream-bright mb-3 flex items-center gap-2">
                                <Clock size={14} className="text-accent" /> Timeline
                            </h2>
                            <div className="space-y-2 max-h-64 overflow-y-auto">
                                {findings.timeline_events.map((e: any, i: number) => (
                                    <div key={i} className="flex items-start gap-3 text-xs">
                                        <span className="text-cream-dim font-mono text-[10px] shrink-0 w-32">{e.timestamp}</span>
                                        <span className="text-cream">{e.description}</span>
                                    </div>
                                ))}
                            </div>
                        </section>
                    )}

                    {/* Recommendations */}
                    {interpretation?.recommendations?.length > 0 && (
                        <section className="bg-servos-surface border border-servos-border rounded-lg p-5">
                            <h2 className="text-sm font-semibold text-cream-bright mb-3 flex items-center gap-2">
                                <AlertTriangle size={14} className="text-warning" /> Recommendations
                            </h2>
                            <ul className="space-y-2">
                                {interpretation.recommendations.map((r: string, i: number) => (
                                    <li key={i} className="flex items-start gap-2 text-xs text-cream">
                                        <CheckCircle2 size={12} className="text-accent shrink-0 mt-0.5" />
                                        {r}
                                    </li>
                                ))}
                            </ul>
                        </section>
                    )}
                </div>
            </div>
        </PageTransition>
    )
}
