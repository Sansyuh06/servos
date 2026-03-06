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
    Shield, FolderOpen, AlertTriangle,
    ChevronRight, FileText, Search, Activity, Lock
} from 'lucide-react'
import { BentoGrid, BentoCard } from '@/components/ui/bento-grid'

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
            if (cases.length > before) {
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
                            <span>New investigation started: {newCaseId.slice(0, 8)}</span>
                            <button onClick={() => setNewCaseId(null)} className="text-success hover:text-success-dark">✖</button>
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
                    <BentoGrid className="grid-cols-4 md:auto-rows-[16rem]">
                        <BentoCard
                            name="Connected Devices"
                            className="col-span-4 md:col-span-2 lg:col-span-1"
                            background={<div className="absolute -right-4 -top-4 w-32 h-32 bg-accent/10 rounded-full blur-2xl pointer-events-none" />}
                            Icon={Shield}
                            description="Active USB & Storage drives ready for scan."
                            href="/investigate"
                            cta="Scan Devices"
                        />
                        <BentoCard
                            name="Active Cases"
                            className="col-span-4 md:col-span-2 lg:col-span-1"
                            background={<div className="absolute right-0 bottom-0 w-40 h-40 bg-warning/10 rounded-full blur-2xl pointer-events-none" />}
                            Icon={FolderOpen}
                            description="Investigations currently processing or awaiting review."
                            href="/workspace"
                            cta="View Cases"
                        />
                        <BentoCard
                            name="Completed Scans"
                            className="col-span-4 md:col-span-2 lg:col-span-1"
                            background={<div className="absolute -left-10 -bottom-10 w-40 h-40 bg-success/10 rounded-full blur-3xl pointer-events-none" />}
                            Icon={FileText}
                            description="Analyzed disks with detailed forensic reports."
                            href="/"
                            cta="View Reports"
                        />
                        <BentoCard
                            name="Security Alerts"
                            className="col-span-4 md:col-span-2 lg:col-span-1"
                            background={<div className="absolute right-20 top-20 w-32 h-32 bg-danger/10 rounded-full blur-3xl pointer-events-none" />}
                            Icon={AlertTriangle}
                            description="Critical IOCs and malware detections."
                            href="/alerts"
                            cta="View Alerts"
                        />
                    </BentoGrid>

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
