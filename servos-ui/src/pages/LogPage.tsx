import { useState } from 'react'
import PageTransition from '@/components/PageTransition'

export default function LogPage() {
    const [path, setPath] = useState('')
    const [results, setResults] = useState<any>(null)

    const analyze = async () => {
        const resp = await fetch('/api/logs/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path }),
        })
        const data = await resp.json()
        setResults(data.results)
    }

    return (
        <PageTransition>
            <div className="p-6">
                <h1 className="text-xl font-bold text-cream-bright mb-4">Log File Analysis</h1>
                <input
                    type="text"
                    placeholder="Path to log or directory"
                    value={path}
                    onChange={e => setPath(e.target.value)}
                    className="w-full bg-servos-bg border border-servos-border rounded-lg px-3 py-2 text-cream"
                />
                <button onClick={analyze} className="mt-3 px-4 py-2 bg-accent text-white rounded-lg">
                    Analyze
                </button>
                {results && (
                    <pre className="mt-4 bg-servos-surface p-3 rounded-lg text-xs overflow-auto">
                        {JSON.stringify(results, null, 2)}
                    </pre>
                )}
            </div>
        </PageTransition>
    )
}
