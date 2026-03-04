import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getCaseDetail } from '@/api/client'
import PageTransition from '@/components/PageTransition'
import {
    FolderTree, Shield, Bug, FileText, Clock, Cpu,
    AlertTriangle, CheckCircle2, LightbulbIcon, ThumbsUp, Pencil, Play,
    ChevronLeft, Download
} from 'lucide-react'

const TABS = [
    { id: 'files', label: 'Files', icon: FolderTree },
    { id: 'malware', label: 'Malware', icon: Bug },
    { id: 'artifacts', label: 'Artifacts', icon: FileText },
    { id: 'logs', label: 'Logs', icon: Clock },
    { id: 'memory', label: 'Memory', icon: Cpu },
]

type RecAction = 'approved' | 'modified' | 'executed' | null

export default function WorkspacePage() {
    const { caseId } = useParams()
    const navigate = useNavigate()
    const [caseData, setCaseData] = useState<any>(null)
    const [activeTab, setActiveTab] = useState('files')
    const [loading, setLoading] = useState(true)
    const [recActions, setRecActions] = useState<Record<number, RecAction>>({})
    const [auditLog, setAuditLog] = useState<string[]>([])

    useEffect(() => {
        if(caseId) {
            getCaseDetail(caseId)
                .then((d) => { setCaseData(d); setLoading(false) })
                .catch(() => setLoading(false))
        }
    }, [caseId])

    const addAudit = (msg: string) => {
        const ts = new Date().toLocaleTimeString()
        setAuditLog(prev => [`[${ts}] ${msg}`, ...prev])
    }

    const handleApprove = (idx: number, rec: string) => {
        setRecActions(prev => ({ ...prev, [idx]: 'approved' }))
        addAudit(`APPROVED: "${rec.slice(0, 50)}..."`)
    }

    const handleModify = (idx: number, rec: string) => {
        const modified = prompt('Modify this recommendation:', rec)
        if(modified) {
            setRecActions(prev => ({ ...prev, [idx]: 'modified' }))
            addAudit(`MODIFIED: "${rec.slice(0, 30)}..." → "${modified.slice(0, 30)}..."`)
        }
    }

    const handleExecute = (idx: number, rec: string) => {
        setRecActions(prev => ({ ...prev, [idx]: 'executed' }))
        addAudit(`EXECUTED: "${rec.slice(0, 50)}..."`)
    }

    if(loading) {
        return (
            <PageTransition>
                <div className="h-full flex items-center justify-center text-cream-dim">Loading investigation...</div>
            </PageTransition>
        )
    }

    const findings = caseData?.findings || {}
    const interpretation = caseData?.interpretation || {}

    return (
        <PageTransition>
            <div className="h-full flex flex-col overflow-hidden">
                {/* Top bar */}
                <div className="flex items-center gap-3 px-4 py-2.5 border-b border-servos-border-dim bg-servos-surface shrink-0">
                    <button
                        onClick={() => navigate('/')}
                        className="p-1 rounded-md hover:bg-servos-hover text-cream-dim transition-colors"
                    >
                        <ChevronLeft size={16} />
                    </button>
                    <div className="flex-1">
                        <h2 className="text-sm font-semibold text-cream-bright">Investigation Workspace</h2>
                        <p className="text-[10px] text-cream-dim font-mono">{caseId}</p>
                    </div>
                    <button
                        onClick={() => navigate(`/report/${caseId}`)}
                        className="flex items-center gap-1.5 px-3 py-1.5 bg-accent hover:bg-accent-dark text-white text-[11px] font-semibold rounded-md transition-colors"
                    >
                        <Download size={12} /> View Report
                    </button>
                </div>

                <div className="flex-1 flex overflow-hidden">
                    {/* ── Left: Evidence Tree ── */}
                    <div className="w-56 bg-servos-surface border-r border-servos-border overflow-y-auto shrink-0">
                        <div className="px-4 py-3 border-b border-servos-border-dim">
                            <p className="text-[10px] font-semibold text-cream-dim uppercase tracking-wider">Evidence Tree</p>
                        </div>
                        <div className="p-3 space-y-0.5">
                            {[
                                { label: 'File System', count: findings?.file_system?.total_files || 0, icon: FolderTree, tab: 'files' },
                                { label: 'Suspicious', count: findings?.suspicious_files?.length || 0, icon: AlertTriangle, danger: true, tab: 'files' },
                                { label: 'Malware Hits', count: findings?.malware_indicators?.length || 0, icon: Bug, danger: true, tab: 'malware' },
                                { label: 'Artifacts', count: Object.keys(findings?.artifacts || {}).length, icon: FileText, tab: 'artifacts' },
                                { label: 'Timeline', count: findings?.timeline_events?.length || 0, icon: Clock, tab: 'logs' },
                            ].map(({ label, count, icon: Icon, danger, tab }) => (
                                <button
                                    key={label}
                                    onClick={() => setActiveTab(tab)}
                                    className={`w-full flex items-center gap-2 px-2 py-2 rounded-md transition-colors text-xs ${activeTab === tab ? 'bg-accent-muted text-cream-bright' : 'hover:bg-servos-hover text-cream'
                                        }`}
                                >
                                    <Icon size={13} className={danger && count > 0 ? 'text-danger' : 'text-cream-dim'} />
                                    <span>{label}</span>
                                    <span className={`ml-auto text-[10px] font-bold ${danger && count > 0 ? 'text-danger' : 'text-cream-dim'}`}>{count}</span>
                                </button>
                            ))}
                        </div>

                        {/* Audit Log */}
                        {auditLog.length > 0 && (
                            <div className="border-t border-servos-border-dim mt-2">
                                <div className="px-4 py-2">
                                    <p className="text-[10px] font-semibold text-cream-dim uppercase tracking-wider">Audit Log</p>
                                </div>
                                <div className="px-3 pb-3 space-y-1 max-h-48 overflow-y-auto">
                                    {auditLog.map((log, i) => (
                                        <p key={i} className="text-[9px] text-cream-dim font-mono leading-relaxed">{log}</p>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>

                    {/* ── Center: Analysis Panel ── */}
                    <div className="flex-1 flex flex-col overflow-hidden">
                        {/* Tabs */}
                        <div className="flex border-b border-servos-border shrink-0">
                            {TABS.map(({ id, label, icon: Icon }) => (
                                <button
                                    key={id}
                                    onClick={() => setActiveTab(id)}
                                    className={`flex items-center gap-1.5 px-4 py-2.5 text-[11px] font-semibold uppercase tracking-wider border-b-2 transition-colors ${activeTab === id
                                            ? 'text-accent border-accent'
                                            : 'text-cream-dim border-transparent hover:text-cream hover:border-servos-border'
                                        }`}
                                >
                                    <Icon size={13} />
                                    {label}
                                </button>
                            ))}
                            <div className="ml-auto flex items-center gap-1.5 px-4 text-[10px] text-success">
                                <span className="w-1.5 h-1.5 rounded-full bg-success" />
                                Offline Mode Active
                            </div>
                        </div>

                        {/* Tab content */}
                        <div className="flex-1 overflow-y-auto p-5">
                            {activeTab === 'files' && (
                                <div>
                                    <h3 className="text-sm font-semibold text-cream mb-3">File System Analysis</h3>
                                    <div className="grid grid-cols-3 gap-3 mb-4">
                                        {[
                                            ['Total Files', findings?.file_system?.total_files || 0],
                                            ['Suspicious', findings?.file_system?.suspicious || 0],
                                            ['File Types', Object.keys(findings?.file_system?.types || {}).length],
                                        ].map(([label, val]) => (
                                            <div key={String(label)} className="bg-servos-surface border border-servos-border rounded-lg p-3">
                                                <p className="text-[10px] text-cream-dim uppercase tracking-wider">{label}</p>
                                                <p className="text-xl font-bold text-cream-bright mt-1">{val}</p>
                                            </div>
                                        ))}
                                    </div>
                                    {findings?.suspicious_files?.length > 0 && (
                                        <div className="bg-servos-surface border border-servos-border rounded-lg overflow-hidden">
                                            <div className="px-4 py-2 border-b border-servos-border-dim">
                                                <p className="text-[10px] font-semibold text-cream-dim uppercase tracking-wider">Suspicious Files</p>
                                            </div>
                                            {findings.suspicious_files.slice(0, 20).map((f: any, i: number) => (
                                                <div key={i} className="flex items-center px-4 py-2 border-b border-servos-border-dim/50 text-xs">
                                                    <AlertTriangle size={12} className="text-warning mr-2 shrink-0" />
                                                    <span className="text-cream font-mono">{f.name}</span>
                                                    <span className="ml-auto text-cream-dim text-[10px]">{f.reason}</span>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            )}

                            {activeTab === 'malware' && (
                                <div>
                                    <h3 className="text-sm font-semibold text-cream mb-3">Malware Detection</h3>
                                    <div className="mb-4">
                                        <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-bold uppercase ${findings?.malware?.risk_level === 'CRITICAL' || findings?.malware?.risk_level === 'HIGH'
                                                ? 'bg-danger-muted text-danger border border-danger/20'
                                                : 'bg-success-muted text-success border border-success/20'
                                            }`}>
                                            Risk Level: {findings?.malware?.risk_level || 'Unknown'}
                                        </span>
                                    </div>
                                    {findings?.malware_indicators?.map((ind: any, i: number) => (
                                        <div key={i} className="bg-servos-surface border border-servos-border rounded-lg p-3 mb-2">
                                            <div className="flex items-center gap-2 mb-1">
                                                <Bug size={12} className={ind.severity === 'critical' ? 'text-danger' : 'text-warning'} />
                                                <span className="text-xs font-semibold text-cream">{ind.rule}</span>
                                                <span className={`ml-auto px-1.5 py-0.5 rounded text-[9px] font-bold uppercase ${ind.severity === 'critical' ? 'bg-danger-muted text-danger' : 'bg-warning-muted text-warning'
                                                    }`}>{ind.severity}</span>
                                            </div>
                                            <p className="text-[11px] text-cream-dim">{ind.description}</p>
                                            <p className="text-[10px] text-cream-dim/70 mt-1 font-mono">{ind.file}</p>
                                        </div>
                                    ))}
                                    {(!findings?.malware_indicators || findings.malware_indicators.length === 0) && (
                                        <p className="text-xs text-cream-dim py-4">No malware indicators detected.</p>
                                    )}
                                </div>
                            )}

                            {activeTab === 'artifacts' && (
                                <div>
                                    <h3 className="text-sm font-semibold text-cream mb-3">Extracted Artifacts</h3>
                                    <div className="grid grid-cols-2 gap-3">
                                        {Object.entries(findings?.artifacts || {}).map(([key, val]) => (
                                            <div key={key} className="bg-servos-surface border border-servos-border rounded-lg p-3">
                                                <p className="text-[10px] text-cream-dim uppercase tracking-wider capitalize">{key.replace(/_/g, ' ')}</p>
                                                <p className="text-lg font-bold text-cream-bright mt-1">{String(val)}</p>
                                            </div>
                                        ))}
                                    </div>
                                    {Object.keys(findings?.artifacts || {}).length === 0 && (
                                        <p className="text-xs text-cream-dim py-4">No artifacts extracted.</p>
                                    )}
                                </div>
                            )}

                            {activeTab === 'logs' && (
                                <div>
                                    <h3 className="text-sm font-semibold text-cream mb-3">Timeline Events</h3>
                                    {(findings?.timeline_events || []).length === 0 ? (
                                        <p className="text-xs text-cream-dim py-4">No timeline events recorded.</p>
                                    ) : (
                                        <div className="space-y-1">
                                            {findings.timeline_events.map((e: any, i: number) => (
                                                <div key={i} className="flex items-start gap-3 px-3 py-2 bg-servos-surface border border-servos-border rounded-lg">
                                                    <Clock size={12} className="text-cream-dim mt-0.5 shrink-0" />
                                                    <div className="flex-1 min-w-0">
                                                        <p className="text-xs text-cream">{e.description}</p>
                                                        <p className="text-[10px] text-cream-dim mt-0.5 font-mono">{e.timestamp}</p>
                                                    </div>
                                                    {e.severity && (
                                                        <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold uppercase shrink-0 ${e.severity === 'high' ? 'bg-danger-muted text-danger' : 'bg-accent-muted text-accent'
                                                            }`}>{e.severity}</span>
                                                    )}
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            )}

                            {activeTab === 'memory' && (
                                <div className="py-8 text-center text-cream-dim">
                                    <Cpu size={24} className="mx-auto mb-2 opacity-40" />
                                    <p className="text-sm">Memory Analysis</p>
                                    <p className="text-[11px] mt-1 text-cream-dim/60">Volatility 3 integration — coming in v2.0</p>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* ── Right: AI Guidance Panel ── */}
                    <div className="w-72 bg-servos-surface border-l border-servos-border overflow-y-auto shrink-0">
                        <div className="px-4 py-3 border-b border-servos-border-dim">
                            <div className="flex items-center gap-2">
                                <LightbulbIcon size={14} className="text-accent" />
                                <p className="text-[10px] font-semibold text-cream-dim uppercase tracking-wider">AI Guidance</p>
                            </div>
                        </div>

                        <div className="p-4 space-y-4">
                            {/* Risk assessment */}
                            <div className="bg-servos-bg rounded-lg p-3 border border-servos-border-dim">
                                <p className="text-[10px] text-cream-dim uppercase tracking-wider mb-1">Risk Assessment</p>
                                <p className={`text-sm font-semibold ${interpretation?.risk === 'HIGH' || interpretation?.risk === 'CRITICAL' ? 'text-danger' :
                                        interpretation?.risk === 'MEDIUM' ? 'text-warning' : 'text-success'
                                    }`}>{interpretation?.risk || 'Pending'}</p>
                            </div>

                            {/* Summary */}
                            {interpretation?.summary && (
                                <div>
                                    <p className="text-[10px] text-cream-dim uppercase tracking-wider mb-2">Summary</p>
                                    <p className="text-xs text-cream leading-relaxed">{interpretation.summary}</p>
                                </div>
                            )}

                            {/* Recommendations with working buttons */}
                            {interpretation?.recommendations?.length > 0 && (
                                <div>
                                    <p className="text-[10px] text-cream-dim uppercase tracking-wider mb-2">Recommendations</p>
                                    <div className="space-y-2">
                                        {interpretation.recommendations.map((rec: string, i: number) => {
                                            const action = recActions[i]
                                            return (
                                                <div key={i} className={`rounded-lg p-2.5 border text-xs text-cream ${action === 'approved' ? 'bg-success-muted border-success/30' :
                                                        action === 'executed' ? 'bg-accent-muted border-accent/30' :
                                                            action === 'modified' ? 'bg-warning-muted border-warning/30' :
                                                                'bg-servos-bg border-servos-border-dim'
                                                    }`}>
                                                    <div className="flex items-start gap-2">
                                                        {action && (
                                                            <CheckCircle2 size={12} className={
                                                                action === 'approved' ? 'text-success mt-0.5 shrink-0' :
                                                                    action === 'executed' ? 'text-accent mt-0.5 shrink-0' :
                                                                        'text-warning mt-0.5 shrink-0'
                                                            } />
                                                        )}
                                                        <span>{rec}</span>
                                                    </div>

                                                    {action ? (
                                                        <p className={`text-[9px] font-bold uppercase mt-2 ${action === 'approved' ? 'text-success' :
                                                                action === 'executed' ? 'text-accent' : 'text-warning'
                                                            }`}>
                                                            ✓ {action}
                                                        </p>
                                                    ) : (
                                                        <div className="flex gap-1 mt-2">
                                                            <button
                                                                onClick={() => handleApprove(i, rec)}
                                                                className="flex items-center gap-1 px-2 py-1 bg-success-muted text-success rounded text-[10px] font-semibold hover:bg-success/20 active:scale-95 transition-all cursor-pointer"
                                                            >
                                                                <ThumbsUp size={10} /> Approve
                                                            </button>
                                                            <button
                                                                onClick={() => handleModify(i, rec)}
                                                                className="flex items-center gap-1 px-2 py-1 bg-accent-muted text-accent rounded text-[10px] font-semibold hover:bg-accent/20 active:scale-95 transition-all cursor-pointer"
                                                            >
                                                                <Pencil size={10} /> Modify
                                                            </button>
                                                            <button
                                                                onClick={() => handleExecute(i, rec)}
                                                                className="flex items-center gap-1 px-2 py-1 bg-servos-hover text-cream-dim rounded text-[10px] font-semibold hover:text-cream active:scale-95 transition-all cursor-pointer"
                                                            >
                                                                <Play size={10} /> Execute
                                                            </button>
                                                        </div>
                                                    )}
                                                </div>
                                            )
                                        })}
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </PageTransition>
    )
}
