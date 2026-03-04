import React from 'react'

/**
 * Grid of tool cards with hover depth, gradient borders. Mimics the 21st.dev
 * ultra-quality-showcase-grid. The parent page should supply tools data.
 */
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

export default function UltraQualityShowcaseGrid({ tools, onRun }: Props) {
    return (
        <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 auto-rows-fr">
            {tools.map((tool) => (
                <div
                    key={tool.id}
                    className="relative bg-servos-surface border border-servos-border rounded-lg p-4 hover:shadow-lg transition-shadow group"
                >
                    <div className="flex items-center justify-between">
                        <span className="text-sm font-semibold text-cream">{tool.name}</span>
                        <span
                            className={`h-2 w-2 rounded-full ${
                                tool.status === 'available' ? 'bg-success' : 'bg-danger'
                            }`}
                        />
                    </div>
                    <p className="mt-2 text-xs text-cream-dim" title={tool.description}>
                        {tool.category}
                    </p>
                    <div className="absolute inset-0 opacity-0 group-hover:opacity-100 bg-black/40 flex items-center justify-center">
                        {onRun && (
                            <button
                                onClick={() => onRun(tool)}
                                className="px-3 py-1 bg-accent text-white text-xs rounded-md"
                            >
                                Run Now
                            </button>
                        )}
                    </div>
                </div>
            ))}
        </div>
    )
}
