import { useState, useEffect } from 'react'
import PageTransition from '@/components/PageTransition'

export default function NetworkScanPage() {
    const [interfaces, setInterfaces] = useState<any[]>([])
    const [selected, setSelected] = useState<string>('')
    const [connections, setConnections] = useState<any[]>([])
    const [ports, setPorts] = useState<any[]>([])
    const [arp, setArp] = useState<any[]>([])

    useEffect(() => {
        fetch('/api/network/interfaces')
            .then(r => r.json())
            .then(d => setInterfaces(d.interfaces || []))
    }, [])

    const runScan = async () => {
        const [con, p, a] = await Promise.all([
            fetch('/api/network/connections').then(r=>r.json()),
            fetch('/api/network/listen').then(r=>r.json()),
            fetch('/api/network/arp').then(r=>r.json()),
        ])
        setConnections(con.connections || [])
        setPorts(p.ports || [])
        setArp(a.arp || [])
    }

    return (
        <PageTransition>
            <div className="p-6">
                <h1 className="text-xl font-bold text-cream-bright mb-4">Network Scan</h1>
                <div className="mb-4">
                    <label className="text-cream-dim text-sm">Interface:</label>
                    <select
                        className="ml-2 bg-servos-bg border border-servos-border rounded-lg px-2 py-1 text-cream"
                        value={selected}
                        onChange={e => setSelected(e.target.value)}
                    >
                        <option value="">All</option>
                        {interfaces.map((i, idx) => (
                            <option key={idx} value={i.name}>{i.name} {i.address}</option>
                        ))}
                    </select>
                    <button
                        onClick={runScan}
                        className="ml-4 px-4 py-2 bg-accent text-white rounded-lg"
                    >Begin Scan</button>
                </div>
                <div className="space-y-6">
                    <section>
                        <h2 className="text-sm font-semibold text-cream">Active Connections</h2>
                        <div className="max-h-40 overflow-y-auto bg-servos-surface border border-servos-border rounded-lg mt-2 p-2 text-xs">
                            {connections.map((c,i)=>(<div key={i}>{c.laddr} → {c.raddr} ({c.status})</div>))}
                        </div>
                    </section>
                    <section>
                        <h2 className="text-sm font-semibold text-cream">Listening Ports</h2>
                        <div className="max-h-40 overflow-y-auto bg-servos-surface border border-servos-border rounded-lg mt-2 p-2 text-xs">
                            {ports.map((p,i)=>(<div key={i}>{p.laddr} {p.process}</div>))}
                        </div>
                    </section>
                    <section>
                        <h2 className="text-sm font-semibold text-cream">ARP Table</h2>
                        <div className="max-h-40 overflow-y-auto bg-servos-surface border border-servos-border rounded-lg mt-2 p-2 text-xs">
                            {arp.map((e,i)=>(<div key={i}>{e.ip} {e.mac}</div>))}
                        </div>
                    </section>
                </div>
            </div>
        </PageTransition>
    )
}
