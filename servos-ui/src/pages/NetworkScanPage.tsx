import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import PageTransition from '@/components/PageTransition'
import { Wifi, Activity, Radio, Globe, RefreshCw, Loader2, AlertTriangle, CheckCircle2 } from 'lucide-react'

interface Connection {
    laddr: string
    raddr: string
    status: string
    pid?: number
    process?: string
}

interface Port {
    laddr: string
    process: string
    pid?: number
}

interface ArpEntry {
    ip: string
    mac: string
}

interface NetInterface {
    name: string
    address: string
}

export default function NetworkScanPage() {
    const [interfaces, setInterfaces] = useState<NetInterface[]>([])
    const [connections, setConnections] = useState<Connection[]>([])
    const [ports, setPorts] = useState<Port[]>([])
    const [arp, setArp] = useState<ArpEntry[]>([])
    const [scanning, setScanning] = useState(false)
    const [scanned, setScanned] = useState(false)
    const [filter, setFilter] = useState('')

    // Auto-scan on mount
    useEffect(() => { runScan() }, [])

    const runScan = async () => {
        setScanning(true)
        try {
            const [ifRes, conRes, portRes, arpRes] = await Promise.all([
                fetch('/api/network/interfaces').then(r => r.json()).catch(() => ({ interfaces: [] })),
                fetch('/api/network/connections').then(r => r.json()).catch(() => ({ connections: [] })),
                fetch('/api/network/listen').then(r => r.json()).catch(() => ({ ports: [] })),
                fetch('/api/network/arp').then(r => r.json()).catch(() => ({ arp: [] })),
            ])
            setInterfaces(ifRes.interfaces || [])
            setConnections(conRes.connections || [])
            setPorts(portRes.ports || [])
            setArp(arpRes.arp || [])
            setScanned(true)
        } catch (e) {
            console.error('Network scan failed', e)
        }
        setScanning(false)
    }

    const statusColor = (status: string) => {
        const s = status?.toUpperCase()
        if (s === 'ESTABLISHED') return 'bg-green-500/20 text-green-400 border-green-500/30'
        if (s === 'LISTEN') return 'bg-blue-500/20 text-blue-400 border-blue-500/30'
        if (s === 'TIME_WAIT') return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
        if (s === 'CLOSE_WAIT') return 'bg-red-500/20 text-red-400 border-red-500/30'
        return 'bg-white/10 text-cream-dim border-white/10'
    }

    const filteredConnections = filter
        ? connections.filter(c =>
            c.laddr?.toLowerCase().includes(filter) ||
            c.raddr?.toLowerCase().includes(filter) ||
            c.status?.toLowerCase().includes(filter) ||
            c.process?.toLowerCase().includes(filter)
        )
        : connections

    const established = connections.filter(c => c.status === 'ESTABLISHED').length

    return (
        <PageTransition>
            <div className="h-full overflow-y-auto">
                {/* Header */}
                <div className="px-6 pt-6 pb-4 border-b border-servos-border-dim">
                    <div className="flex items-center justify-between mb-4">
                        <div>
                            <h1 className="text-xl font-bold text-cream-bright flex items-center gap-2">
                                <Wifi size={20} className="text-accent" />
                                Network Scanner
                            </h1>
                            <p className="text-xs text-cream-dim mt-1">Real-time network connections, ports, and ARP analysis</p>
                        </div>
                        <button
                            onClick={runScan}
                            disabled={scanning}
                            className="flex items-center gap-2 px-4 py-2 bg-accent hover:bg-accent/80 text-white rounded-lg text-sm font-medium disabled:opacity-50 transition-colors"
                        >
                            {scanning ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
                            {scanning ? 'Scanning...' : 'Re-scan'}
                        </button>
                    </div>

                    {/* Stats Cards */}
                    {scanned && (
                        <div className="grid grid-cols-4 gap-3">
                            {[
                                { icon: Activity, label: 'Active Connections', value: connections.length, color: 'text-green-400' },
                                { icon: CheckCircle2, label: 'Established', value: established, color: 'text-blue-400' },
                                { icon: Radio, label: 'Listening Ports', value: ports.length, color: 'text-yellow-400' },
                                { icon: Globe, label: 'ARP Entries', value: arp.length, color: 'text-purple-400' },
                            ].map(({ icon: Icon, label, value, color }, i) => (
                                <motion.div
                                    key={label}
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: i * 0.1 }}
                                    className="bg-servos-surface border border-servos-border rounded-lg p-3"
                                >
                                    <div className="flex items-center gap-2 mb-1">
                                        <Icon size={14} className={color} />
                                        <span className="text-[10px] text-cream-dim uppercase tracking-wider">{label}</span>
                                    </div>
                                    <p className={`text-xl font-bold font-mono ${color}`}>{value}</p>
                                </motion.div>
                            ))}
                        </div>
                    )}
                </div>

                {scanning && !scanned ? (
                    <div className="flex flex-col items-center justify-center py-20">
                        <Loader2 size={32} className="text-accent animate-spin mb-4" />
                        <p className="text-sm text-cream-dim">Scanning network interfaces...</p>
                    </div>
                ) : (
                    <div className="px-6 py-4 space-y-6">
                        {/* Search */}
                        <input
                            type="text"
                            placeholder="Filter connections by address, status, or process..."
                            value={filter}
                            onChange={e => setFilter(e.target.value.toLowerCase())}
                            className="w-full bg-servos-surface border border-servos-border rounded-lg px-3 py-2 text-sm text-cream placeholder:text-cream-dim/30 outline-none focus:border-accent/40 transition-colors"
                        />

                        {/* Active Connections Table */}
                        <section>
                            <h2 className="text-sm font-semibold text-cream-bright mb-2 flex items-center gap-2">
                                <Activity size={14} className="text-green-400" />
                                Active Connections
                                <span className="text-[10px] text-cream-dim font-normal">({filteredConnections.length})</span>
                            </h2>
                            <div className="bg-servos-surface border border-servos-border rounded-lg overflow-hidden">
                                <table className="w-full text-xs">
                                    <thead>
                                        <tr className="border-b border-servos-border-dim text-cream-dim uppercase tracking-wider text-[10px]">
                                            <th className="text-left px-3 py-2">Local Address</th>
                                            <th className="text-left px-3 py-2">Remote Address</th>
                                            <th className="text-left px-3 py-2">Status</th>
                                            <th className="text-left px-3 py-2">PID</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {filteredConnections.slice(0, 30).map((c, i) => (
                                            <tr key={i} className="border-b border-servos-border-dim/50 hover:bg-white/[0.02] transition-colors">
                                                <td className="px-3 py-1.5 font-mono text-cream">{c.laddr || '—'}</td>
                                                <td className="px-3 py-1.5 font-mono text-cream">{c.raddr || '—'}</td>
                                                <td className="px-3 py-1.5">
                                                    <span className={`inline-block px-1.5 py-0.5 rounded text-[10px] font-medium border ${statusColor(c.status)}`}>
                                                        {c.status || '—'}
                                                    </span>
                                                </td>
                                                <td className="px-3 py-1.5 text-cream-dim font-mono">{c.pid || '—'}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                                {filteredConnections.length === 0 && (
                                    <div className="text-center py-6 text-cream-dim text-xs">No connections found</div>
                                )}
                            </div>
                        </section>

                        {/* Listening Ports Table */}
                        <section>
                            <h2 className="text-sm font-semibold text-cream-bright mb-2 flex items-center gap-2">
                                <Radio size={14} className="text-yellow-400" />
                                Listening Ports
                                <span className="text-[10px] text-cream-dim font-normal">({ports.length})</span>
                            </h2>
                            <div className="bg-servos-surface border border-servos-border rounded-lg overflow-hidden">
                                <table className="w-full text-xs">
                                    <thead>
                                        <tr className="border-b border-servos-border-dim text-cream-dim uppercase tracking-wider text-[10px]">
                                            <th className="text-left px-3 py-2">Address</th>
                                            <th className="text-left px-3 py-2">Process</th>
                                            <th className="text-left px-3 py-2">PID</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {ports.slice(0, 20).map((p, i) => (
                                            <tr key={i} className="border-b border-servos-border-dim/50 hover:bg-white/[0.02] transition-colors">
                                                <td className="px-3 py-1.5 font-mono text-cream">{p.laddr}</td>
                                                <td className="px-3 py-1.5 text-cream">{p.process || '—'}</td>
                                                <td className="px-3 py-1.5 text-cream-dim font-mono">{p.pid || '—'}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                                {ports.length === 0 && (
                                    <div className="text-center py-6 text-cream-dim text-xs">No listening ports detected</div>
                                )}
                            </div>
                        </section>

                        {/* ARP + Interfaces */}
                        <div className="grid grid-cols-2 gap-4">
                            <section>
                                <h2 className="text-sm font-semibold text-cream-bright mb-2 flex items-center gap-2">
                                    <Globe size={14} className="text-purple-400" />
                                    ARP Table
                                </h2>
                                <div className="bg-servos-surface border border-servos-border rounded-lg overflow-hidden max-h-48 overflow-y-auto">
                                    <table className="w-full text-xs">
                                        <thead>
                                            <tr className="border-b border-servos-border-dim text-cream-dim uppercase tracking-wider text-[10px]">
                                                <th className="text-left px-3 py-2">IP Address</th>
                                                <th className="text-left px-3 py-2">MAC Address</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {arp.map((e, i) => (
                                                <tr key={i} className="border-b border-servos-border-dim/50">
                                                    <td className="px-3 py-1.5 font-mono text-cream">{e.ip}</td>
                                                    <td className="px-3 py-1.5 font-mono text-cream-dim">{e.mac}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                    {arp.length === 0 && (
                                        <div className="text-center py-4 text-cream-dim text-xs">No ARP entries</div>
                                    )}
                                </div>
                            </section>

                            <section>
                                <h2 className="text-sm font-semibold text-cream-bright mb-2 flex items-center gap-2">
                                    <Wifi size={14} className="text-accent" />
                                    Network Interfaces
                                </h2>
                                <div className="space-y-2">
                                    {interfaces.map((iface, i) => (
                                        <div key={i} className="bg-servos-surface border border-servos-border rounded-lg p-2.5 flex items-center gap-3">
                                            <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse shrink-0" />
                                            <div>
                                                <p className="text-xs font-medium text-cream">{iface.name}</p>
                                                <p className="text-[10px] font-mono text-cream-dim">{iface.address}</p>
                                            </div>
                                        </div>
                                    ))}
                                    {interfaces.length === 0 && (
                                        <div className="text-center py-4 text-cream-dim text-xs">No interfaces detected</div>
                                    )}
                                </div>
                            </section>
                        </div>
                    </div>
                )}
            </div>
        </PageTransition>
    )
}
