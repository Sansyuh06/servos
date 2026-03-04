import { useState } from 'react'
import PageTransition from '@/components/PageTransition'

export default function MemoryPage() {
    const [dumpPath, setDumpPath] = useState('')
    const [output, setOutput] = useState<string[]>([])
    const [captured, setCaptured] = useState(false)

    const capture = async () => {
        const resp = await fetch('/api/memory/capture', { method: 'POST' })
        const data = await resp.json()
        if (data.success) {
            setDumpPath(data.path)
            setCaptured(true)
        }
    }

    const analyze = async () => {
        const resp = await fetch('/api/memory/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ dump_path: dumpPath, plugin: 'pslist' }),
        })
        const data = await resp.json()
        setOutput(data.output || [])
    }

    return (
        <PageTransition>
            <div className="p-6">
                <h1 className="text-xl font-bold text-cream-bright mb-4">Memory Forensics</h1>
                <button onClick={capture} className="px-4 py-2 bg-accent text-white rounded-lg">
                    Capture RAM
                </button>
                {captured && (
                    <div className="mt-4">
                        <p>Dump saved at {dumpPath}</p>
                        <button onClick={analyze} className="mt-2 px-4 py-2 bg-accent text-white rounded-lg">
                            Run pslist
                        </button>
                    </div>
                )}
                {output.length > 0 && (
                    <div className="mt-4 bg-servos-surface p-3 rounded-lg text-xs max-h-60 overflow-y-auto">
                        {output.map((l,i)=><div key={i}>{l}</div>)}
                    </div>
                )}
            </div>
        </PageTransition>
    )
}
