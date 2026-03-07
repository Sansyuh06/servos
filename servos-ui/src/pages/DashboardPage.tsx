import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAppStore } from '@/store/appStore'
import { useAuthStore } from '@/store/authStore'
import PageTransition from '@/components/PageTransition'
import TopoBackground from '@/components/TopoBackground'
import GooeyTextMorph from '@/components/GooeyTextMorph'
import TopoHero from '@/components/ui/topo-hero'
import SpatialDeviceCard from '@/components/SpatialDeviceCard'
import {
    Shield, FolderOpen, AlertTriangle,
    ChevronRight, FileText, Search, Activity, Lock
} from 'lucide-react'
import { BentoGrid, BentoCard } from '@/components/ui/bento-grid'
import { RecentInvestigationsStacked } from '@/components/RecentInvestigationsStacked'
import EarbudShowcase from '@/components/spatial-product-showcase'
import { AnimatePresence, motion } from 'framer-motion'

export default function DashboardPage() {
    const navigate = useNavigate()
    const { username, role } = useAuthStore()
    const { devices, cases, alerts, fetchDevices, fetchCases, fetchAlerts, devicesLoading, casesLoading, alertsLoading } = useAppStore()
    const [prevCount, setPrevCount] = useState(0)
    const [newCaseId, setNewCaseId] = useState<string | null>(null)
    const [showcaseDevice, setShowcaseDevice] = useState<any>(null)

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
                {/* ── Hero Section (TopoHero) ── */}
                <div className="mb-6 -mx-6 -mt-6">
                    <TopoHero />
                </div>


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
                            className="col-span-4 md:col-span-2 lg:col-span-2 shadow-2xl"
                            background={<div className="absolute -right-4 -top-4 w-32 h-32 bg-accent/20 rounded-full blur-[40px] pointer-events-none" />}
                            Icon={Shield}
                            description="Active USB & Storage drives ready for scan."
                            href="/investigate"
                            cta="Scan Devices"
                        />
                        <BentoCard
                            name="Active Cases"
                            className="col-span-4 md:col-span-2 lg:col-span-2 shadow-2xl"
                            background={<div className="absolute right-0 bottom-0 w-40 h-40 bg-warning/20 rounded-full blur-[40px] pointer-events-none" />}
                            Icon={FolderOpen}
                            description="Investigations currently processing or awaiting review."
                            href="/workspace"
                            cta="View Cases"
                        />
                        <BentoCard
                            name="Completed Scans"
                            className="col-span-4 md:col-span-2 lg:col-span-1 shadow-2xl"
                            background={<div className="absolute -left-10 -bottom-10 w-40 h-40 bg-success/20 rounded-full blur-[40px] pointer-events-none" />}
                            Icon={FileText}
                            description="Analyzed disks with detailed forensic reports."
                            href="/"
                            cta="View Reports"
                        />
                        <BentoCard
                            name="Security Alerts"
                            className="col-span-4 md:col-span-2 lg:col-span-3 shadow-2xl"
                            background={<div className="absolute right-20 top-20 w-32 h-32 bg-danger/20 rounded-full blur-[40px] pointer-events-none" />}
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
                                        onAnalyze={() => setShowcaseDevice(device)}
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
                            <div className="bg-servos-surface border border-servos-border rounded-lg overflow-hidden flex justify-center py-8">
                                <RecentInvestigationsStacked cases={cases} onCaseClick={(c: any) => navigate(`/chat?case=${c.id}`)} />
                            </div>
                        )}
                    </section>
                </div>
            </div>

            <AnimatePresence>
                {showcaseDevice && (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 backdrop-blur-sm"
                    >
                        <button
                            className="absolute top-6 right-6 z-50 text-white/50 hover:text-white"
                            onClick={() => setShowcaseDevice(null)}
                        >
                            Close
                        </button>
                        <div className="w-[90vw] h-[90vh] overflow-hidden rounded-2xl border border-white/10 shadow-2xl">
                            <EarbudShowcase />
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </PageTransition>
    )
}
