import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { getCaseDetail, getReportUrl } from '@/api/client'
import DoodleIcon from '@/components/DoodleIcon'
import PageTransition from '@/components/PageTransition'

function riskClass(risk: string | undefined) {
    if(risk === 'CRITICAL' || risk === 'HIGH') return 'bg-danger-muted text-danger border-danger/30'
    if(risk === 'MEDIUM') return 'bg-warning-muted text-warning border-warning/30'
    return 'bg-success-muted text-success border-success/30'
}

export default function ReportPage() {
    const { caseId } = useParams()
    const navigate = useNavigate()
    const [data, setData] = useState<any>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        if(!caseId) {
            setLoading(false)
            return
        }

        getCaseDetail(caseId)
            .then((response) => {
                setData(response)
                setLoading(false)
            })
            .catch(() => setLoading(false))
    }, [caseId])

    if(loading) {
        return (
            <PageTransition>
                <div className="doodle-panel flex h-full items-center justify-center p-10 text-center">
                    <div className="relative z-10">
                        <DoodleIcon name="legal" alt="Loading report doodle" size="lg" className="mx-auto" />
                        <p className="mt-4 text-sm text-cream-dim">Loading report...</p>
                    </div>
                </div>
            </PageTransition>
        )
    }

    const findings = data?.findings || {}
    const interpretation = data?.interpretation || {}
    const device = data?.device_info || {}

    return (
        <PageTransition>
            <div className="h-full overflow-y-auto space-y-5">
                <section className="doodle-panel p-6">
                    <div className="relative z-10 flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
                        <div className="flex items-center gap-4">
                            <DoodleIcon name="legal" alt="Report doodle" size="lg" />
                            <div>
                                <h1 className="text-3xl font-black text-cream-bright font-heading">Forensic Report</h1>
                                <p className="mt-2 text-sm text-cream-dim">
                                    Structured case summary for review, export, and handoff.
                                </p>
                                <p className="mt-2 text-[10px] uppercase tracking-[0.18em] text-cream-dim">
                                    {caseId || 'No case selected'}
                                </p>
                            </div>
                        </div>

                        <div className="flex flex-wrap gap-2">
                            <button
                                onClick={() => navigate(-1)}
                                className="doodle-button px-4 py-2 text-sm font-semibold"
                            >
                                Back
                            </button>
                            <a
                                href={caseId ? getReportUrl(caseId, 'pdf') : '#'}
                                className="doodle-button doodle-button-primary px-4 py-2 text-sm font-semibold"
                            >
                                Export PDF
                            </a>
                            <a
                                href={caseId ? getReportUrl(caseId, 'json') : '#'}
                                className="doodle-button px-4 py-2 text-sm font-semibold"
                            >
                                Export JSON
                            </a>
                        </div>
                    </div>
                </section>

                <section className="doodle-panel p-6">
                    <div className="relative z-10">
                        <div className="flex items-center gap-3">
                            <DoodleIcon name="dashboard" alt="Summary doodle" size="md" />
                            <div>
                                <h2 className="text-xl font-black text-cream-bright font-heading">
                                    Executive Summary
                                </h2>
                                <p className="text-sm text-cream-dim">
                                    Analyst-ready synopsis and risk assessment.
                                </p>
                            </div>
                        </div>

                        <p className="mt-5 text-sm leading-7 text-cream-bright">
                            {interpretation?.summary || 'No summary available.'}
                        </p>

                        <div className="mt-5 flex flex-wrap items-center gap-3">
                            <span className="text-[10px] uppercase tracking-[0.18em] text-cream-dim">
                                Risk assessment
                            </span>
                            <span
                                className={`rounded-full border px-3 py-1 text-[10px] font-bold uppercase tracking-[0.16em] ${riskClass(
                                    interpretation?.risk,
                                )}`}
                            >
                                {interpretation?.risk || 'Unknown'}
                            </span>
                        </div>
                    </div>
                </section>

                <div className="grid gap-5 xl:grid-cols-[0.95fr_1.05fr]">
                    <section className="space-y-5">
                        <div className="doodle-panel p-5">
                            <div className="relative z-10">
                                <div className="flex items-center gap-3">
                                    <DoodleIcon name="hdd-drive" alt="Device metadata doodle" size="md" />
                                    <div>
                                        <h2 className="text-xl font-black text-cream-bright font-heading">
                                            Device Metadata
                                        </h2>
                                        <p className="text-sm text-cream-dim">
                                            Core evidence source details captured during investigation startup.
                                        </p>
                                    </div>
                                </div>

                                <div className="mt-5 grid gap-3">
                                    {Object.entries(device).length === 0 ? (
                                        <p className="text-sm text-cream-dim">No device metadata available.</p>
                                    ) : (
                                        Object.entries(device).map(([key, value]) => (
                                            <div
                                                key={key}
                                                className="rounded-[20px] border border-white/10 bg-white/[0.04] p-4"
                                            >
                                                <p className="text-[10px] uppercase tracking-[0.18em] text-cream-dim">
                                                    {key.replace(/_/g, ' ')}
                                                </p>
                                                <p className="mt-2 break-all font-mono text-sm text-cream-bright">
                                                    {String(value)}
                                                </p>
                                            </div>
                                        ))
                                    )}
                                </div>
                            </div>
                        </div>

                        {findings?.integrity_hashes && (
                            <div className="doodle-panel p-5">
                                <div className="relative z-10">
                                    <div className="flex items-center gap-3">
                                        <DoodleIcon name="settings" alt="Integrity doodle" size="md" />
                                        <div>
                                            <h2 className="text-xl font-black text-cream-bright font-heading">
                                                Evidence Integrity Hashes
                                            </h2>
                                            <p className="text-sm text-cream-dim">
                                                SHA-256 values for preserved evidence artifacts.
                                            </p>
                                        </div>
                                    </div>

                                    <div className="mt-5 max-h-80 space-y-2 overflow-y-auto">
                                        {Object.entries(findings.integrity_hashes)
                                            .slice(0, 20)
                                            .map(([file, hash]) => (
                                                <div
                                                    key={file}
                                                    className="rounded-[20px] border border-white/10 bg-white/[0.04] p-4"
                                                >
                                                    <p className="truncate text-sm text-cream-bright">{file}</p>
                                                    <p className="mt-2 break-all font-mono text-xs text-cream-dim">
                                                        {String(hash)}
                                                    </p>
                                                </div>
                                            ))}
                                    </div>
                                </div>
                            </div>
                        )}
                    </section>

                    <section className="space-y-5">
                        {findings?.timeline_events?.length > 0 && (
                            <div className="doodle-panel p-5">
                                <div className="relative z-10">
                                    <div className="flex items-center gap-3">
                                        <DoodleIcon name="alerts" alt="Timeline doodle" size="md" />
                                        <div>
                                            <h2 className="text-xl font-black text-cream-bright font-heading">
                                                Timeline
                                            </h2>
                                            <p className="text-sm text-cream-dim">
                                                Chronological activity extracted from the evidence set.
                                            </p>
                                        </div>
                                    </div>

                                    <div className="mt-5 space-y-3">
                                        {findings.timeline_events.map((event: any, index: number) => (
                                            <div
                                                key={`${event.timestamp}-${index}`}
                                                className="rounded-[20px] border border-white/10 bg-white/[0.04] p-4"
                                            >
                                                <p className="text-[10px] uppercase tracking-[0.18em] text-cream-dim">
                                                    {event.timestamp}
                                                </p>
                                                <p className="mt-2 text-sm leading-6 text-cream-bright">
                                                    {event.description}
                                                </p>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        )}

                        {interpretation?.recommendations?.length > 0 && (
                            <div className="doodle-panel p-5">
                                <div className="relative z-10">
                                    <div className="flex items-center gap-3">
                                        <DoodleIcon name="threat" alt="Recommendations doodle" size="md" />
                                        <div>
                                            <h2 className="text-xl font-black text-cream-bright font-heading">
                                                Recommendations
                                            </h2>
                                            <p className="text-sm text-cream-dim">
                                                Suggested next steps based on the investigation interpretation.
                                            </p>
                                        </div>
                                    </div>

                                    <div className="mt-5 space-y-3">
                                        {interpretation.recommendations.map((recommendation: string, index: number) => (
                                            <div
                                                key={`${recommendation}-${index}`}
                                                className="rounded-[20px] border border-white/10 bg-white/[0.04] p-4 text-sm leading-7 text-cream-bright"
                                            >
                                                {recommendation}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        )}
                    </section>
                </div>
            </div>
        </PageTransition>
    )
}
