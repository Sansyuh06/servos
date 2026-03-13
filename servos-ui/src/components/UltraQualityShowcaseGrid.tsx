import DoodleIcon, { type DoodleName } from '@/components/DoodleIcon'

interface Tool {
    id: string
    name: string
    category: string
    status: 'available' | 'missing'
    lastRun?: string
    description?: string
}

interface Props {
    tools: Tool[]
    onRun?: (tool: Tool) => void
}

const DOODLE_BY_CATEGORY: Record<string, DoodleName> = {
    disk: 'hdd-drive',
    malware: 'threat',
    network: 'network',
    memory: 'dashboard',
    logs: 'legal',
    registry: 'settings',
}

function doodleForTool(tool: Tool): DoodleName {
    return DOODLE_BY_CATEGORY[tool.category.toLowerCase()] || 'dashboard'
}

export default function UltraQualityShowcaseGrid({ tools, onRun }: Props) {
    return (
        <div className="grid auto-rows-fr gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {tools.map((tool) => (
                <div key={tool.id} className="doodle-panel p-4">
                    <div className="relative z-10 flex h-full flex-col">
                        <div className="flex items-start gap-3">
                            <DoodleIcon
                                name={doodleForTool(tool)}
                                alt={`${tool.name} doodle`}
                                size="md"
                                className={tool.status === 'available' ? 'bg-accent/20' : 'bg-danger/15'}
                            />
                            <div className="min-w-0 flex-1">
                                <div className="flex items-center justify-between gap-3">
                                    <p className="text-sm font-bold text-cream-bright">{tool.name}</p>
                                    <span
                                        className={[
                                            'rounded-full px-2 py-1 text-[10px] font-bold uppercase tracking-[0.18em]',
                                            tool.status === 'available'
                                                ? 'bg-success-muted text-success'
                                                : 'bg-danger-muted text-danger',
                                        ].join(' ')}
                                    >
                                        {tool.status}
                                    </span>
                                </div>
                                <p className="mt-1 text-[11px] uppercase tracking-[0.18em] text-cream-dim">
                                    {tool.category}
                                </p>
                                {tool.description && (
                                    <p className="mt-3 text-xs leading-relaxed text-cream-dim">
                                        {tool.description}
                                    </p>
                                )}
                            </div>
                        </div>

                        <div className="mt-4 flex items-end justify-between gap-3 pt-3">
                            <p className="text-[11px] text-cream-dim">
                                {tool.lastRun ? `Last run: ${tool.lastRun}` : 'Ready to run'}
                            </p>
                            {onRun && (
                                <button
                                    onClick={() => onRun(tool)}
                                    className="doodle-button doodle-button-primary px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em]"
                                >
                                    Run now
                                </button>
                            )}
                        </div>
                    </div>
                </div>
            ))}
        </div>
    )
}
