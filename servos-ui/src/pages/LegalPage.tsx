import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import PageTransition from '@/components/PageTransition'
import {
    Scale, BookOpen, CheckCircle2, AlertTriangle, Copy, ChevronDown,
    Shield, FileText, Gavel, ClipboardCheck, Loader2, Check
} from 'lucide-react'

interface Section {
    title: string
    summary: string
    punishment: string
    relevance: string
    certificate_requirements?: string[]
}

interface Precedent {
    case: string
    summary: string
    relevance: string
}

export default function LegalPage() {
    const [sections, setSections] = useState<Record<string, Section>>({})
    const [checklist, setChecklist] = useState<string[]>([])
    const [tips, setTips] = useState<string[]>([])
    const [handling, setHandling] = useState<string[]>([])
    const [precedents, setPrecedents] = useState<Precedent[]>([])
    const [selectedSection, setSelectedSection] = useState<string>('')
    const [loading, setLoading] = useState(true)
    const [copied, setCopied] = useState(false)
    const [checkedItems, setCheckedItems] = useState<Set<number>>(new Set())
    const [activeTab, setActiveTab] = useState<'checklist' | 'sections' | 'tips' | 'precedents'>('checklist')

    useEffect(() => {
        Promise.all([
            fetch('/api/legal/full').then(r => r.json()).catch(() => ({})),
        ]).then(([full]) => {
            setSections(full.sections || {})
            setChecklist(full.checklist || [])
            setTips(full.admissibility_tips || [])
            setHandling(full.evidence_handling || [])
            setPrecedents(full.precedents || [])
            const keys = Object.keys(full.sections || {})
            if (keys.length > 0) setSelectedSection(keys[0])
            setLoading(false)
        })
    }, [])

    const toggleCheck = (idx: number) => {
        setCheckedItems(prev => {
            const next = new Set(prev)
            next.has(idx) ? next.delete(idx) : next.add(idx)
            return next
        })
    }

    const copyChecklist = () => {
        const text = checklist.map((item, i) =>
            `${checkedItems.has(i) ? '☑' : '☐'} ${item}`
        ).join('\n')
        navigator.clipboard.writeText(text)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
    }

    const sel = selectedSection ? sections[selectedSection] : null

    const tabs = [
        { id: 'checklist' as const, label: 'Chain of Custody', icon: ClipboardCheck },
        { id: 'sections' as const, label: 'IT Act Sections', icon: BookOpen },
        { id: 'tips' as const, label: 'Evidence Guide', icon: Shield },
        { id: 'precedents' as const, label: 'Case Law', icon: Gavel },
    ]

    if (loading) {
        return (
            <PageTransition>
                <div className="flex items-center justify-center h-full">
                    <Loader2 size={32} className="text-accent animate-spin" />
                </div>
            </PageTransition>
        )
    }

    return (
        <PageTransition>
            <div className="h-full overflow-y-auto">
                {/* Header */}
                <div className="px-6 pt-6 pb-4 border-b border-servos-border-dim">
                    <h1 className="text-xl font-bold text-cream-bright flex items-center gap-2">
                        <Scale size={20} className="text-accent" />
                        Legal & Procedure
                    </h1>
                    <p className="text-xs text-cream-dim mt-1">
                        Indian IT Act reference, chain-of-custody checklist, and evidence handling (offline)
                    </p>

                    {/* Tab Bar */}
                    <div className="flex gap-1 mt-4">
                        {tabs.map(({ id, label, icon: Icon }) => (
                            <button
                                key={id}
                                onClick={() => setActiveTab(id)}
                                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${activeTab === id
                                        ? 'bg-accent/20 text-accent border border-accent/30'
                                        : 'text-cream-dim hover:bg-white/[0.04] border border-transparent'
                                    }`}
                            >
                                <Icon size={12} />
                                {label}
                            </button>
                        ))}
                    </div>
                </div>

                <div className="px-6 py-4">
                    {/* Chain of Custody Checklist */}
                    {activeTab === 'checklist' && (
                        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                            <div className="flex items-center justify-between mb-3">
                                <h2 className="text-sm font-semibold text-cream-bright flex items-center gap-2">
                                    <ClipboardCheck size={14} className="text-green-400" />
                                    Chain of Custody Checklist
                                    <span className="text-[10px] text-cream-dim font-normal">
                                        ({checkedItems.size}/{checklist.length} completed)
                                    </span>
                                </h2>
                                <button
                                    onClick={copyChecklist}
                                    className="flex items-center gap-1.5 px-3 py-1 bg-servos-surface border border-servos-border rounded-lg text-xs text-cream-dim hover:text-cream transition-colors"
                                >
                                    {copied ? <Check size={12} className="text-green-400" /> : <Copy size={12} />}
                                    {copied ? 'Copied!' : 'Copy to Clipboard'}
                                </button>
                            </div>

                            {/* Progress bar */}
                            <div className="w-full h-1.5 bg-servos-surface rounded-full mb-4 overflow-hidden">
                                <motion.div
                                    className="h-full bg-accent rounded-full"
                                    initial={{ width: 0 }}
                                    animate={{ width: `${(checkedItems.size / checklist.length) * 100}%` }}
                                    transition={{ duration: 0.3 }}
                                />
                            </div>

                            <div className="space-y-1.5">
                                {checklist.map((item, i) => (
                                    <motion.button
                                        key={i}
                                        initial={{ opacity: 0, x: -10 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: i * 0.05 }}
                                        onClick={() => toggleCheck(i)}
                                        className={`w-full flex items-start gap-3 p-3 rounded-lg text-left transition-colors ${checkedItems.has(i)
                                                ? 'bg-green-500/10 border border-green-500/20'
                                                : 'bg-servos-surface border border-servos-border hover:border-accent/30'
                                            }`}
                                    >
                                        <div className={`mt-0.5 w-4 h-4 rounded border flex items-center justify-center shrink-0 ${checkedItems.has(i)
                                                ? 'bg-green-500 border-green-500'
                                                : 'border-cream-dim/30'
                                            }`}>
                                            {checkedItems.has(i) && <Check size={10} className="text-white" />}
                                        </div>
                                        <span className={`text-xs ${checkedItems.has(i) ? 'text-cream line-through opacity-60' : 'text-cream'}`}>
                                            {item}
                                        </span>
                                    </motion.button>
                                ))}
                            </div>
                        </motion.div>
                    )}

                    {/* IT Act Sections */}
                    {activeTab === 'sections' && (
                        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                            <div className="flex gap-4">
                                {/* Section List */}
                                <div className="w-48 shrink-0 space-y-1">
                                    {Object.entries(sections).map(([id, sec]) => (
                                        <button
                                            key={id}
                                            onClick={() => setSelectedSection(id)}
                                            className={`w-full text-left px-3 py-2 rounded-lg text-xs transition-colors ${selectedSection === id
                                                    ? 'bg-accent/20 text-accent border border-accent/30'
                                                    : 'text-cream-dim hover:bg-white/[0.04] border border-transparent'
                                                }`}
                                        >
                                            <div className="font-medium">Section {id}</div>
                                            <div className="text-[10px] opacity-60 truncate">{sec.title}</div>
                                        </button>
                                    ))}
                                </div>

                                {/* Section Detail */}
                                {sel && (
                                    <div className="flex-1 bg-servos-surface border border-servos-border rounded-lg p-4">
                                        <h3 className="text-sm font-bold text-accent mb-1">
                                            Section {selectedSection}: {sel.title}
                                        </h3>
                                        <p className="text-xs text-cream leading-relaxed mb-3">{sel.summary}</p>

                                        <div className="space-y-2">
                                            <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-2.5">
                                                <p className="text-[10px] text-red-400 uppercase tracking-wider font-semibold mb-0.5">Punishment</p>
                                                <p className="text-xs text-cream">{sel.punishment}</p>
                                            </div>
                                            <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-2.5">
                                                <p className="text-[10px] text-blue-400 uppercase tracking-wider font-semibold mb-0.5">Forensic Relevance</p>
                                                <p className="text-xs text-cream">{sel.relevance}</p>
                                            </div>
                                            {sel.certificate_requirements && (
                                                <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-2.5">
                                                    <p className="text-[10px] text-yellow-400 uppercase tracking-wider font-semibold mb-1">65B Certificate Requirements</p>
                                                    <ul className="space-y-0.5">
                                                        {sel.certificate_requirements.map((req, i) => (
                                                            <li key={i} className="text-xs text-cream flex items-start gap-1.5">
                                                                <span className="text-yellow-400 mt-0.5">•</span> {req}
                                                            </li>
                                                        ))}
                                                    </ul>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                )}
                            </div>
                        </motion.div>
                    )}

                    {/* Evidence Handling Tips */}
                    {activeTab === 'tips' && (
                        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
                            <section>
                                <h2 className="text-sm font-semibold text-cream-bright mb-2 flex items-center gap-2">
                                    <Shield size={14} className="text-blue-400" />
                                    Admissibility Tips
                                </h2>
                                <div className="space-y-1.5">
                                    {tips.map((tip, i) => (
                                        <div key={i} className="flex items-start gap-2 bg-blue-500/10 border border-blue-500/20 rounded-lg p-2.5">
                                            <CheckCircle2 size={12} className="text-blue-400 mt-0.5 shrink-0" />
                                            <span className="text-xs text-cream">{tip}</span>
                                        </div>
                                    ))}
                                </div>
                            </section>

                            <section>
                                <h2 className="text-sm font-semibold text-cream-bright mb-2 flex items-center gap-2">
                                    <FileText size={14} className="text-yellow-400" />
                                    Evidence Handling Do's & Don'ts
                                </h2>
                                <div className="space-y-1.5">
                                    {handling.map((item, i) => {
                                        const isDo = item.startsWith('DO:')
                                        const isDont = item.startsWith("DON'T:")
                                        return (
                                            <div key={i} className={`flex items-start gap-2 rounded-lg p-2.5 border ${isDo ? 'bg-green-500/10 border-green-500/20' :
                                                    isDont ? 'bg-red-500/10 border-red-500/20' :
                                                        'bg-servos-surface border-servos-border'
                                                }`}>
                                                {isDo ? (
                                                    <CheckCircle2 size={12} className="text-green-400 mt-0.5 shrink-0" />
                                                ) : (
                                                    <AlertTriangle size={12} className="text-red-400 mt-0.5 shrink-0" />
                                                )}
                                                <span className="text-xs text-cream">{item}</span>
                                            </div>
                                        )
                                    })}
                                </div>
                            </section>
                        </motion.div>
                    )}

                    {/* Case Law Precedents */}
                    {activeTab === 'precedents' && (
                        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                            <h2 className="text-sm font-semibold text-cream-bright mb-3 flex items-center gap-2">
                                <Gavel size={14} className="text-purple-400" />
                                Key Legal Precedents
                            </h2>
                            <div className="space-y-2">
                                {precedents.map((p, i) => (
                                    <motion.div
                                        key={i}
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{ delay: i * 0.1 }}
                                        className="bg-servos-surface border border-servos-border rounded-lg p-3"
                                    >
                                        <h3 className="text-xs font-bold text-accent mb-1">{p.case}</h3>
                                        <p className="text-xs text-cream mb-2">{p.summary}</p>
                                        <div className="flex items-center gap-1.5">
                                            <span className="text-[10px] text-purple-400 uppercase tracking-wider font-semibold">Relevance:</span>
                                            <span className="text-[10px] text-cream-dim">{p.relevance}</span>
                                        </div>
                                    </motion.div>
                                ))}
                            </div>
                        </motion.div>
                    )}
                </div>
            </div>
        </PageTransition>
    )
}
