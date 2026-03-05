import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAppStore } from '@/store/appStore'
import { useAuthStore } from '@/store/authStore'
import PageTransition from '@/components/PageTransition'
import TopoBackground from '@/components/TopoBackground'
import GooeyTextMorph from '@/components/GooeyTextMorph'
import HalideTopoHero from '@/components/HalideTopoHero'
import SpatialDeviceCard from '@/components/SpatialDeviceCard'
import {
    Shield, FolderOpen, Clock, AlertTriangle,
    ChevronRight, FileText, Search
} from 'lucide-react'

export default function DashboardPage() {
    const navigate = useNavigate()
    const { username, role } = useAuthStore()
    const { devices, cases, alerts, fetchDevices, fetchCases, fetchAlerts, devicesLoading, casesLoading, alertsLoading } = useAppStore()
    const [prevCount, setPrevCount] = useState(0)
    const [newCaseId, setNewCaseId] = useState<string | null>(null)

    useEffect(() => {
        fetchDevices()
        fetchCases()
        fetchAlerts()
        const interval = setInterval(async () => {
            const before = cases.length
            await fetchCases()
            await fetchAlerts()
            if(cases.length > before) {
                // set latest added case id
                setNewCaseId(cases[0]?.id || null)
            }
        }, 5000) // refresh every 5s to show auto cases
        return () => clearInterval(interval)
    }, [])

    return (
        <PageTransition>
            <div className="h-full overflow-y-auto">
                {/* ── Hero Section (HalideTopoHero) ── */}
                <HalideTopoHero
                    title="SERVOS"
                    subtitle="Offline AI Forensic Platform"
                    statusBadge={
                        <span className={`px-2 py-1 text-xs rounded-md ${cases.filter(c => c.status === 'running').length > 0 ? 'bg-warning text-black' : 'bg-success text-white'}`}>
                            {cases.filter(c => c.status === 'running').length > 0 ? 'Active Investigations' : 'No Active Investigations'}
                        </span>
                    }
                />


                <div className="p-6 space-y-6">
                    {newCaseId && (
                        <div className="bg-success-muted border border-success rounded-lg p-3 text-success text-sm flex justify-between items-center">
                            <span>New investigation started: {newCaseId.slice(0,8)}</span>
                            <button onClick={()=>setNewCaseId(null)} className="text-success hover:text-success-dark">✖</button>
                        </div>
                    )}
                    {/* ── Top Bar Info ── */}
                    <div className="flex items-center justify-between">
                        <div>
                            <h2 className="text-lg font-semibold text-cream-bright">Welcome back, {username}</h2>
                            <p className="text-xs text-cream-dim mt-0.5">
                                {new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
                            </p>
                        </div>
                        <button
                            onClick={() => navigate('/investigate')}
                            className="flex items-center gap-2 px-4 py-2 bg-accent hover:bg-accent-dark text-white text-sm font-semibold rounded-lg transition-colors"
                        >
                            <Search size={14} />
                            New Investigation
                        </button>
                    </div>

                    {/* ── Quick Stats ── */}
                    <div className="grid grid-cols-4 gap-3">
                        {[
                            { label: 'Connected Devices', value: devices.length, icon: Shield, color: 'text-accent' },
                            { label: 'Active Cases', value: cases.filter(c => c.status === 'running').length, icon: FolderOpen, color: 'text-warning' },
                            { label: 'Completed', value: cases.filter(c => c.status === 'completed').length, icon: FileText, color: 'text-success' },
                            { label: 'Alerts', value: alerts.length, icon: AlertTriangle, color: 'text-danger' },
                        ].map(({ label, value, icon: Icon, color }) => (
                            <div key={label} className="bg-servos-surface border border-servos-border rounded-lg p-4">
                                <div className="flex items-center gap-2 mb-2">
                                    <Icon size={14} className={color} />
                                    <span className="text-[10px] font-semibold text-cream-dim uppercase tracking-wider">{label}</span>
                                </div>
                                <span className="text-2xl font-bold text-cream-bright">{value}</span>
                            </div>
                        ))}
                    </div>

                    {/* ── Connected Devices ── */}
                    <section>
                        <div className="flex items-center justify-between mb-3">
                            <h3 className="text-sm font-semibold text-cream">Connected Devices</h3>
                            <button
                                onClick={() => fetchDevices()}
                                className="text-[11px] text-accent hover:text-accent-light transition-colors"
                            >
                                Refresh
                            </button>
                        </div>

                        {devicesLoading ? (
                            <div className="text-sm text-cream-dim py-8 text-center">Scanning devices...</div>
                        ) : devices.length === 0 ? (
                            <div className="bg-servos-surface border border-servos-border rounded-lg p-8 text-center">
                                <Shield size={24} className="text-cream-dim mx-auto mb-2" />
                                <p className="text-sm text-cream-dim">No devices detected</p>
                                <p className="text-xs text-cream-dim/60 mt-1">Connect a USB device to begin investigation</p>
                            </div>
                        ) : (
                            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
                                {devices.map((device, i) => (
                                    <SpatialDeviceCard
                                        key={i}
                                        device={device}
                                        onAnalyze={() => navigate('/investigate')}
                                        onBackup={() => { }}
                                    />
                                ))}
                            </div>
                        )}
                    </section>

                    {/* ── Recent Investigations ── */}
                    <section>
                        <div className="flex items-center justify-between mb-3">
                            <h3 className="text-sm font-semibold text-cream">Recent Investigations</h3>
                            <button className="text-[11px] text-accent hover:text-accent-light transition-colors">
                                View All
                            </button>
                        </div>

                        {casesLoading ? (
                            <div className="text-sm text-cream-dim py-6 text-center">Loading cases...</div>
                        ) : cases.length === 0 ? (
                            <div className="bg-servos-surface border border-servos-border rounded-lg p-6 text-center">
                                <FolderOpen size={20} className="text-cream-dim mx-auto mb-2" />
                                <p className="text-sm text-cream-dim">No investigations yet</p>
                            </div>
                        ) : (
                            <div className="bg-servos-surface border border-servos-border rounded-lg overflow-hidden">
                                <table className="w-full">
                                    <thead>
                                        <tr className="border-b border-servos-border-dim">
                                            <th className="text-left px-4 py-2.5 text-[10px] font-semibold text-cream-dim uppercase tracking-wider">Case ID</th>
                                            <th className="text-left px-4 py-2.5 text-[10px] font-semibold text-cream-dim uppercase tracking-wider">Investigator</th>
                                            <th className="text-left px-4 py-2.5 text-[10px] font-semibold text-cream-dim uppercase tracking-wider">Mode</th>
                                            <th className="text-left px-4 py-2.5 text-[10px] font-semibold text-cream-dim uppercase tracking-wider">Status</th>
                                            <th className="text-left px-4 py-2.5 text-[10px] font-semibold text-cream-dim uppercase tracking-wider">Created</th>
                                            <th className="w-8"></th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {cases.slice(0, 8).map((c) => (
                                            <tr
                                                key={c.id}
                                                className="border-b border-servos-border-dim/50 hover:bg-servos-hover/50 cursor-pointer transition-colors"
                                                onClick={() => navigate(`/workspace/${c.id}`)}
                                            >
                                                <td className="px-4 py-3 text-xs font-mono text-cream">{c.id.slice(0, 8)}</td>
                                                <td className="px-4 py-3 text-xs text-cream">{c.investigator}</td>
                                                <td className="px-4 py-3 text-xs text-cream-dim capitalize">{c.mode}</td>
                                                <td className="px-4 py-3">
                                                    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider ${c.status === 'completed'
                                                            ? 'bg-success-muted text-success border border-success/20'
                                                            : c.status === 'error'
                                                                ? 'bg-danger-muted text-danger border border-danger/20'
                                                                : 'bg-warning-muted text-warning border border-warning/20'
                                                        }`}>
                                                        {c.status}
                                                    </span>
                                                </td>
                                                <td className="px-4 py-3 text-xs text-cream-dim">
                                                    {new Date(c.created_at).toLocaleDateString()}
                                                </td>
                                                <td className="px-2 py-3">
                                                    <ChevronRight size={14} className="text-cream-dim" />
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </section>
                </div>
            </div>
        </PageTransition>
    )
}
