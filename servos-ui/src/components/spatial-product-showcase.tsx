import { useMemo, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import DoodleIcon, { type DoodleName } from '@/components/DoodleIcon'

type ViewId = 'overview' | 'findings'

interface SpatialProductShowcaseProps {
    caseNumber: string
    investigator: string
    deviceInfo: string
    criticalFindings: string[]
}

interface ShowcaseView {
    id: ViewId
    label: string
    doodle: DoodleName
    title: string
    description: string
}

const SHOWCASE_VIEWS: ShowcaseView[] = [
    {
        id: 'overview',
        label: 'Overview',
        doodle: 'usb-drive',
        title: 'Evidence Source Snapshot',
        description: 'A quick front-door view of the mounted device, operator, and case metadata.',
    },
    {
        id: 'findings',
        label: 'Findings',
        doodle: 'threat',
        title: 'Critical Findings Preview',
        description: 'The fastest way to surface the most important suspicious indicators before deeper review.',
    },
]

export default function SpatialProductShowcase({
    caseNumber,
    investigator,
    deviceInfo,
    criticalFindings,
}: SpatialProductShowcaseProps) {
    const [activeView, setActiveView] = useState<ViewId>('overview')

    const activeConfig = useMemo(
        () => SHOWCASE_VIEWS.find((view) => view.id === activeView) || SHOWCASE_VIEWS[0],
        [activeView],
    )

    return (
        <div className="doodle-panel p-5">
            <div className="relative z-10 grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
                <div className="rounded-[30px] border border-white/10 bg-white/[0.04] p-6">
                    <AnimatePresence mode="wait">
                        <motion.div
                            key={activeView}
                            initial={{ opacity: 0, y: 10, scale: 0.98 }}
                            animate={{ opacity: 1, y: 0, scale: 1 }}
                            exit={{ opacity: 0, y: -10, scale: 0.98 }}
                            className="text-center"
                        >
                            <DoodleIcon
                                name={activeConfig.doodle}
                                alt={`${activeConfig.title} doodle`}
                                size="xl"
                                className="mx-auto h-40 w-40 rounded-[38px]"
                                imageClassName="p-5"
                            />
                            <h3 className="mt-5 text-2xl font-black text-cream-bright font-heading">
                                {activeConfig.title}
                            </h3>
                            <p className="mt-3 text-sm leading-7 text-cream-dim">
                                {activeConfig.description}
                            </p>
                        </motion.div>
                    </AnimatePresence>
                </div>

                <div>
                    <div className="flex flex-wrap gap-2">
                        {SHOWCASE_VIEWS.map((view) => (
                            <button
                                key={view.id}
                                onClick={() => setActiveView(view.id)}
                                className={[
                                    'doodle-button px-4 py-2 text-sm font-semibold',
                                    view.id === activeView ? 'doodle-button-primary' : '',
                                ].join(' ')}
                            >
                                {view.label}
                            </button>
                        ))}
                    </div>

                    <h2 className="mt-5 text-3xl font-black text-cream-bright font-heading">
                        Case {caseNumber.slice(0, 12)}
                    </h2>
                    <p className="mt-2 text-sm text-cream-dim">
                        Structured visual summary for the current investigation workspace.
                    </p>

                    <div className="mt-5 grid gap-3 sm:grid-cols-2">
                        <div className="rounded-[22px] border border-white/10 bg-white/[0.04] p-4">
                            <p className="text-[10px] uppercase tracking-[0.18em] text-cream-dim">Investigator</p>
                            <p className="mt-2 text-sm font-semibold text-cream-bright">
                                {investigator || 'Unassigned'}
                            </p>
                        </div>
                        <div className="rounded-[22px] border border-white/10 bg-white/[0.04] p-4">
                            <p className="text-[10px] uppercase tracking-[0.18em] text-cream-dim">Mounted source</p>
                            <p className="mt-2 truncate text-sm font-semibold text-cream-bright">
                                {deviceInfo || 'Unknown device'}
                            </p>
                        </div>
                        <div className="rounded-[22px] border border-white/10 bg-white/[0.04] p-4">
                            <p className="text-[10px] uppercase tracking-[0.18em] text-cream-dim">Critical findings</p>
                            <p className="mt-2 text-2xl font-black text-cream-bright font-heading">
                                {criticalFindings.length}
                            </p>
                        </div>
                        <div className="rounded-[22px] border border-white/10 bg-white/[0.04] p-4">
                            <p className="text-[10px] uppercase tracking-[0.18em] text-cream-dim">Workspace mode</p>
                            <p className="mt-2 text-sm font-semibold text-cream-bright">Analyst review</p>
                        </div>
                    </div>

                    <div className="mt-5 rounded-[24px] border border-white/10 bg-white/[0.04] p-5">
                        <p className="text-[10px] uppercase tracking-[0.18em] text-cream-dim">Highlighted indicators</p>
                        {criticalFindings.length === 0 ? (
                            <p className="mt-3 text-sm leading-7 text-cream-dim">
                                No critical findings were surfaced in the initial snapshot.
                            </p>
                        ) : (
                            <div className="mt-4 flex flex-wrap gap-2">
                                {criticalFindings.slice(0, 5).map((finding, index) => (
                                    <span
                                        key={`${finding}-${index}`}
                                        className="doodle-chip text-xs font-semibold"
                                    >
                                        {finding}
                                    </span>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    )
}
