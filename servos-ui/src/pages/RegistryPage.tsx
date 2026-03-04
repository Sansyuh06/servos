import { useState } from 'react'
import PageTransition from '@/components/PageTransition'

export default function RegistryPage() {
    const [path, setPath] = useState('')
    const [keys, setKeys] = useState<any>(null)

    const analyze = async () => {
        const resp = await fetch('/api/registry/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ hive_path: path }),
        })
        const data = await resp.json()
        setKeys(data.keys)
    }

    return (
        <PageTransition>
            <div className="p-6">
                <h1 className="text-xl font-bold text-cream-bright mb-4">Registry Analysis</h1>
                <input
                    type="text"
                    placeholder="Path to hive file"
                    value={path}
                    onChange={e => setPath(e.target.value)}
                    className="w-full bg-servos-bg border border-servos-border rounded-lg px-3 py-2 text-cream"
                />
                <button onClick={analyze} className="mt-3 px-4 py-2 bg-accent text-white rounded-lg">
                    Analyze
                </button>
                {keys && (
                    <pre className="mt-4 bg-servos-surface p-3 rounded-lg text-xs overflow-auto">
                        {JSON.stringify(keys, null, 2)}
                    </pre>
                )}
            </div>
        </PageTransition>
    )
}
