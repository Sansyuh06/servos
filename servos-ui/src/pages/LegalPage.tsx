import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import DoodleIcon, { type DoodleName } from '@/components/DoodleIcon'
import PageTransition from '@/components/PageTransition'

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

const TABS = [
    { id: 'checklist', label: 'Chain of Custody', doodle: 'alerts' },
    { id: 'sections', label: 'IT Act Sections', doodle: 'legal' },
    { id: 'tips', label: 'Evidence Guide', doodle: 'settings' },
    { id: 'precedents', label: 'Case Law', doodle: 'dashboard' },
] satisfies { id: 'checklist' | 'sections' | 'tips' | 'precedents'; label: string; doodle: DoodleName }[]

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
        fetch('/api/legal/full')
            .then((response) => response.json())
            .catch(() => ({}))
            .then((full) => {
                setSections(full.sections || {})
                setChecklist(full.checklist || [])
                setTips(full.admissibility_tips || [])
                setHandling(full.evidence_handling || [])
                setPrecedents(full.precedents || [])
                const keys = Object.keys(full.sections || {})
                if(keys.length > 0) setSelectedSection(keys[0])
                setLoading(false)
            })
    }, [])

    const toggleCheck = (index: number) => {
        setCheckedItems((previous) => {
            const next = new Set(previous)
            if(next.has(index)) {
                next.delete(index)
            } else {
                next.add(index)
            }
            return next
        })
    }

    const copyChecklist = () => {
        const text = checklist.map((item, index) => `${checkedItems.has(index) ? '[x]' : '[ ]'} ${item}`).join('\n')
        navigator.clipboard.writeText(text)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
    }

    const selected = selectedSection ? sections[selectedSection] : null

    if(loading) {
        return (
            <PageTransition>
                <div className="doodle-panel flex h-full items-center justify-center p-10 text-center">
                    <div className="relative z-10">
                        <DoodleIcon name="legal" alt="Legal loading doodle" size="lg" className="mx-auto" />
                        <p className="mt-4 text-sm text-cream-dim">Loading legal reference...</p>
                    </div>
                </div>
            </PageTransition>
        )
    }

    return (
        <PageTransition>
            <div className="h-full overflow-y-auto space-y-5">
                <section className="doodle-panel p-6">
                    <div className="relative z-10">
                        <div className="flex items-center gap-4">
                            <DoodleIcon name="legal" alt="Legal doodle" size="lg" />
                            <div>
                                <h1 className="text-3xl font-black text-cream-bright font-heading">Legal & Procedure</h1>
                                <p className="mt-2 text-sm text-cream-dim">
                                    Offline legal reference, custody checklist, and evidence handling notes.
                                </p>
                            </div>
                        </div>

                        <div className="mt-6 flex flex-wrap gap-2">
                            {TABS.map((tab) => (
                                <button
                                    key={tab.id}
                                    onClick={() => setActiveTab(tab.id)}
                                    className={[
                                        'doodle-button flex items-center gap-2 px-4 py-2 text-sm font-semibold',
                                        activeTab === tab.id ? 'doodle-button-primary' : '',
                                    ].join(' ')}
                                >
                                    <DoodleIcon name={tab.doodle} alt={`${tab.label} doodle`} size="sm" className="h-8 w-8 rounded-[16px]" />
                                    {tab.label}
                                </button>
                            ))}
                        </div>
                    </div>
                </section>

                {activeTab === 'checklist' && (
                    <section className="doodle-panel p-6">
                        <div className="relative z-10">
                            <div className="flex flex-wrap items-center justify-between gap-3">
                                <div>
                                    <h2 className="text-xl font-black text-cream-bright font-heading">Chain of Custody Checklist</h2>
                                    <p className="text-sm text-cream-dim">
                                        {checkedItems.size}/{checklist.length} completed
                                    </p>
                                </div>
                                <button onClick={copyChecklist} className="doodle-button px-4 py-2 text-sm font-semibold">
                                    {copied ? 'Copied' : 'Copy checklist'}
                                </button>
                            </div>

                            <div className="mt-5 overflow-hidden rounded-full bg-black/15">
                                <motion.div
                                    className="h-3 rounded-full bg-accent"
                                    initial={{ width: 0 }}
                                    animate={{ width: `${checklist.length ? (checkedItems.size / checklist.length) * 100 : 0}%` }}
                                />
                            </div>

                            <div className="mt-5 space-y-3">
                                {checklist.map((item, index) => (
                                    <button
                                        key={`${item}-${index}`}
                                        onClick={() => toggleCheck(index)}
                                        className={[
                                            'flex w-full items-start gap-3 rounded-[22px] border p-4 text-left transition-colors',
                                            checkedItems.has(index)
                                                ? 'border-success/30 bg-success-muted'
                                                : 'border-white/10 bg-white/[0.04]',
                                        ].join(' ')}
                                    >
                                        <span className="doodle-chip text-[10px] font-bold uppercase tracking-[0.18em]">
                                            {checkedItems.has(index) ? 'Done' : 'Open'}
                                        </span>
                                        <span className="text-sm leading-7 text-cream-bright">{item}</span>
                                    </button>
                                ))}
                            </div>
                        </div>
                    </section>
                )}

                {activeTab === 'sections' && (
                    <div className="grid gap-5 xl:grid-cols-[260px_minmax(0,1fr)]">
                        <section className="doodle-panel p-4">
                            <div className="relative z-10 space-y-2">
                                {Object.entries(sections).map(([id, section]) => (
                                    <button
                                        key={id}
                                        onClick={() => setSelectedSection(id)}
                                        className={[
                                            'w-full rounded-[20px] border px-4 py-3 text-left transition-colors',
                                            selectedSection === id
                                                ? 'border-accent/35 bg-accent/18'
                                                : 'border-white/8 bg-white/[0.03]',
                                        ].join(' ')}
                                    >
                                        <p className="text-sm font-semibold text-cream-bright">Section {id}</p>
                                        <p className="mt-1 text-xs text-cream-dim">{section.title}</p>
                                    </button>
                                ))}
                            </div>
                        </section>

                        <section className="doodle-panel p-6">
                            <div className="relative z-10">
                                {selected ? (
                                    <>
                                        <h2 className="text-2xl font-black text-cream-bright font-heading">
                                            Section {selectedSection}: {selected.title}
                                        </h2>
                                        <p className="mt-4 text-sm leading-7 text-cream-bright">{selected.summary}</p>

                                        <div className="mt-5 grid gap-3">
                                            <div className="rounded-[22px] border border-danger/30 bg-danger-muted p-4">
                                                <p className="text-[10px] uppercase tracking-[0.18em] text-danger">Punishment</p>
                                                <p className="mt-2 text-sm text-cream-bright">{selected.punishment}</p>
                                            </div>
                                            <div className="rounded-[22px] border border-accent/30 bg-accent-muted p-4">
                                                <p className="text-[10px] uppercase tracking-[0.18em] text-accent-light">Forensic relevance</p>
                                                <p className="mt-2 text-sm text-cream-bright">{selected.relevance}</p>
                                            </div>
                                        </div>

                                        {selected.certificate_requirements && (
                                            <div className="mt-5 rounded-[22px] border border-warning/30 bg-warning-muted p-4">
                                                <p className="text-[10px] uppercase tracking-[0.18em] text-warning">Certificate requirements</p>
                                                <div className="mt-3 space-y-2">
                                                    {selected.certificate_requirements.map((requirement, index) => (
                                                        <p key={`${requirement}-${index}`} className="text-sm text-cream-bright">
                                                            {requirement}
                                                        </p>
                                                    ))}
                                                </div>
                                            </div>
                                        )}
                                    </>
                                ) : (
                                    <p className="text-sm text-cream-dim">No section selected.</p>
                                )}
                            </div>
                        </section>
                    </div>
                )}

                {activeTab === 'tips' && (
                    <div className="grid gap-5 xl:grid-cols-2">
                        <section className="doodle-panel p-6">
                            <div className="relative z-10">
                                <h2 className="text-xl font-black text-cream-bright font-heading">Admissibility Tips</h2>
                                <div className="mt-5 space-y-3">
                                    {tips.map((tip, index) => (
                                        <div key={`${tip}-${index}`} className="rounded-[22px] border border-white/10 bg-white/[0.04] p-4 text-sm text-cream-bright">
                                            {tip}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </section>

                        <section className="doodle-panel p-6">
                            <div className="relative z-10">
                                <h2 className="text-xl font-black text-cream-bright font-heading">Handling Guidance</h2>
                                <div className="mt-5 space-y-3">
                                    {handling.map((item, index) => (
                                        <div
                                            key={`${item}-${index}`}
                                            className={[
                                                'rounded-[22px] border p-4 text-sm',
                                                item.startsWith('DO:')
                                                    ? 'border-success/30 bg-success-muted'
                                                    : item.startsWith("DON'T:")
                                                        ? 'border-danger/30 bg-danger-muted'
                                                        : 'border-white/10 bg-white/[0.04]',
                                            ].join(' ')}
                                        >
                                            <p className="text-cream-bright">{item}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </section>
                    </div>
                )}

                {activeTab === 'precedents' && (
                    <section className="doodle-panel p-6">
                        <div className="relative z-10">
                            <h2 className="text-xl font-black text-cream-bright font-heading">Key Legal Precedents</h2>
                            <div className="mt-5 space-y-3">
                                {precedents.map((precedent, index) => (
                                    <motion.div
                                        key={`${precedent.case}-${index}`}
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{ delay: index * 0.05 }}
                                        className="rounded-[22px] border border-white/10 bg-white/[0.04] p-4"
                                    >
                                        <p className="text-sm font-semibold text-cream-bright">{precedent.case}</p>
                                        <p className="mt-2 text-sm leading-7 text-cream-dim">{precedent.summary}</p>
                                        <p className="mt-3 text-xs text-accent-light">Relevance: {precedent.relevance}</p>
                                    </motion.div>
                                ))}
                            </div>
                        </div>
                    </section>
                )}
            </div>
        </PageTransition>
    )
}
