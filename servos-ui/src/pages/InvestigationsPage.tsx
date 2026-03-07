import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAppStore } from '@/store/appStore'
import { useAuthStore } from '@/store/authStore'
import { startInvestigation } from '@/api/client'
import PageTransition from '@/components/PageTransition'
import { FolderOpen, Plus, Loader2, HardDrive, ShieldAlert, Cpu } from 'lucide-react'

export default function InvestigationsPage() {
    const navigate = useNavigate()
    const { username } = useAuthStore()
    const { cases, devices, fetchCases, fetchDevices, casesLoading } = useAppStore()
    const [starting, setStarting] = useState(false)
    const [selectedDevice, setSelectedDevice] = useState<string>('')

    useEffect(() => {
        fetchCases()
        fetchDevices()
    }, [])

    const handleStartInvestigation = async (devicePath: string) => {
        const device = devices.find(d => d.path === devicePath)
        if (!device) return

        setStarting(true)
        setSelectedDevice(device.path)
        try {
            const res = await startInvestigation({
                device_path: device.path,
                mount_point: device.mount_point,
                device_name: device.name,
                investigator: username
            })
            if (res.case_id) {
                navigate(`/chat?case=${res.case_id}`)
            }
        } catch (error) {
            console.error('Failed to start investigation:', error)
            alert('Failed to start investigation.')
        } finally {
            setStarting(false)
        }
    }

    return (
        <PageTransition>
            <div className="h-full flex flex-col p-6 space-y-6 overflow-y-auto w-full max-w-7xl mx-auto">
                <div className="flex items-center justify-between border-b border-white/5 pb-4">
                    <div>
                        <h1 className="text-2xl font-bold text-cream-bright flex items-center gap-3">
                            <FolderOpen size={24} className="text-accent" />
                            Investigations
                        </h1>
                        <p className="text-sm text-cream-dim mt-1">
                            Manage active cases and start new forensic investigations.
                        </p>
                    </div>
                </div>

                {/* New Investigation Section */}
                <section className="bg-servos-surface border border-servos-border rounded-xl p-6 shadow-2xl">
                    <h2 className="text-lg font-semibold text-cream mb-4 flex items-center gap-2">
                        <Plus className="text-success" size={20} />
                        Start New Investigation
                    </h2>

                    {devices.length === 0 ? (
                        <div className="bg-black/20 rounded-lg p-8 text-center border border-dashed border-white/10">
                            <HardDrive size={32} className="text-cream-dim mx-auto mb-3 opacity-50" />
                            <p className="text-sm text-cream-dim">No USB or external storage devices detected.</p>
                            <p className="text-xs text-cream-dim/60 mt-1 mb-4">Connect a drive to begin a new investigation.</p>
                            <button className="px-5 py-2.5 bg-servos-elevated hover:bg-servos-hover text-sm font-semibold rounded-md transition-colors" onClick={() => fetchDevices()}>Refresh Devices</button>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {devices.map(device => (
                                <div key={device.path} className="bg-black/20 border border-white/5 p-5 rounded-lg flex flex-col justify-between hover:border-accent shadow-lg transition-all group">
                                    <div>
                                        <div className="flex items-center gap-2 text-cream-bright font-bold mb-2">
                                            <HardDrive size={18} className="text-accent" />
                                            {device.name || 'Unknown Drive'}
                                        </div>
                                        <div className="text-xs text-cream-dim space-y-1.5 mt-4 font-mono bg-black/40 p-3 rounded-md">
                                            <p>Path: <span className="text-cream">{device.path}</span></p>
                                            <p>Mount: <span className="text-cream">{device.mount_point}</span></p>
                                            <p>FS: <span className="text-cream uppercase">{device.filesystem}</span></p>
                                        </div>
                                    </div>
                                    <button
                                        onClick={() => handleStartInvestigation(device.path)}
                                        disabled={starting}
                                        className="mt-5 w-full py-2.5 bg-accent hover:bg-accent-dark text-white rounded-md text-sm font-bold flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
                                    >
                                        {starting && selectedDevice === device.path ? <Loader2 size={16} className="animate-spin" /> : <Cpu size={16} />}
                                        Analyze Drive
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}
                </section>

                {/* Active Cases Section */}
                <section>
                    <h2 className="text-lg font-semibold text-cream mb-4 flex items-center gap-2">
                        <ShieldAlert className="text-warning" size={20} />
                        Case History
                    </h2>

                    {casesLoading ? (
                        <div className="text-sm text-cream-dim py-12 flex justify-center items-center gap-3">
                            <Loader2 size={24} className="animate-spin text-accent" /> Loading cases...
                        </div>
                    ) : cases.length === 0 ? (
                        <div className="bg-servos-surface border border-servos-border rounded-xl p-16 text-center shadow-lg">
                            <FolderOpen size={40} className="text-cream-dim mx-auto mb-4 opacity-40" />
                            <p className="text-sm text-cream-dim">No historical cases found.</p>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
                            {cases.map((c: any) => (
                                <div
                                    key={c.id}
                                    onClick={() => navigate(`/workspace/${c.id}`)}
                                    className="bg-servos-surface border border-servos-border hover:border-accent p-6 rounded-xl cursor-pointer transition-all hover:bg-servos-hover/30 hover:-translate-y-1 shadow-xl group"
                                >
                                    <div className="flex items-start justify-between mb-4">
                                        <div className="font-mono text-xs font-bold text-accent bg-accent/10 px-2.5 py-1 rounded">
                                            {c.id.split('-')[0].toUpperCase()}
                                        </div>
                                        <div className={`text-[10px] uppercase font-bold px-2.5 py-1 rounded-full ${c.status === 'completed' ? 'bg-success/20 text-success border border-success/30' : 'bg-warning/20 text-warning border border-warning/30'}`}>
                                            {c.status}
                                        </div>
                                    </div>

                                    <h3 className="text-lg font-bold text-cream-bright mb-1 truncate">
                                        {c.device_info?.name || 'Unnamed Investigation'}
                                    </h3>

                                    <div className="text-xs text-cream-dim space-y-2 mt-5">
                                        <p className="flex justify-between border-b border-white/5 pb-1"><span>Investigator:</span> <span className="text-cream font-medium">{c.investigator}</span></p>
                                        <p className="flex justify-between border-b border-white/5 pb-1"><span>Mode:</span> <span className="text-cream capitalize font-medium">{c.mode}</span></p>
                                        <p className="flex justify-between"><span>Date:</span> <span className="text-cream font-medium">{new Date(c.created_at).toLocaleDateString()}</span></p>
                                    </div>

                                    <div className="mt-6 pt-4 border-t border-white/10 text-xs text-accent font-bold group-hover:text-accent-light flex items-center justify-between uppercase tracking-wider">
                                        View Dashboard
                                        <span className="opacity-0 group-hover:opacity-100 transition-opacity transform group-hover:translate-x-1">→</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </section>
            </div>
        </PageTransition>
    )
}
