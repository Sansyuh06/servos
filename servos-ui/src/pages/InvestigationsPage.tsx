import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { startInvestigation } from '@/api/client'
import DoodleIcon from '@/components/DoodleIcon'
import PageTransition from '@/components/PageTransition'
import SpatialDeviceCard from '@/components/SpatialDeviceCard'
import { useAppStore } from '@/store/appStore'
import { useAuthStore } from '@/store/authStore'

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
        const device = devices.find((entry) => entry.path === devicePath)
        if(!device) return

        setStarting(true)
        setSelectedDevice(device.path)
        try {
            const response = await startInvestigation({
                device_path: device.path,
                mount_point: device.mount_point,
                device_name: device.name,
                investigator: username,
            })
            if(response.case_id) {
                navigate(`/chat?case=${response.case_id}`)
            }
        } catch(error) {
            console.error('Failed to start investigation:', error)
            alert('Failed to start investigation.')
        } finally {
            setStarting(false)
        }
    }

    return (
        <PageTransition>
            <div className="h-full w-full max-w-7xl space-y-6 overflow-y-auto p-6">
                <section className="doodle-panel p-6">
                    <div className="relative z-10 flex items-center gap-4">
                        <DoodleIcon name="dashboard" alt="Investigations doodle" size="lg" />
                        <div>
                            <h1 className="text-3xl font-black text-cream-bright font-heading">Investigations</h1>
                            <p className="mt-2 text-sm text-cream-dim">
                                Start new cases and review the recent investigation history.
                            </p>
                        </div>
                    </div>
                </section>

                <section className="doodle-panel p-6">
                    <div className="relative z-10">
                        <div className="mb-4 flex items-center gap-3">
                            <DoodleIcon name="usb-drive" alt="New investigation doodle" size="md" />
                            <div>
                                <h2 className="text-xl font-black text-cream-bright font-heading">Start New Investigation</h2>
                                <p className="text-sm text-cream-dim">Select a device and begin a fresh case.</p>
                            </div>
                        </div>

                        {devices.length === 0 ? (
                            <div className="rounded-[24px] border border-dashed border-white/12 bg-white/[0.03] px-5 py-12 text-center">
                                <DoodleIcon name="usb-drive" alt="No devices doodle" size="md" className="mx-auto mb-4" />
                                <p className="text-lg font-semibold text-cream-bright">No devices detected</p>
                                <p className="mt-2 text-sm text-cream-dim">Connect a drive to begin a new investigation.</p>
                                <button
                                    onClick={() => fetchDevices()}
                                    className="doodle-button mt-5 px-4 py-2 text-sm font-semibold"
                                >
                                    Refresh devices
                                </button>
                            </div>
                        ) : (
                            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                                {devices.map((device) => (
                                    <div key={device.path}>
                                        <SpatialDeviceCard
                                            device={device}
                                            onAnalyze={() => handleStartInvestigation(device.path)}
                                            onBackup={() => {}}
                                        />
                                        {starting && selectedDevice === device.path && (
                                            <p className="mt-2 text-xs text-cream-dim">Starting investigation...</p>
                                        )}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </section>

                <section className="doodle-panel p-6">
                    <div className="relative z-10">
                        <div className="mb-4 flex items-center gap-3">
                            <DoodleIcon name="legal" alt="Case history doodle" size="md" />
                            <div>
                                <h2 className="text-xl font-black text-cream-bright font-heading">Case History</h2>
                                <p className="text-sm text-cream-dim">Review recent cases and reopen investigation workspaces.</p>
                            </div>
                        </div>

                        {casesLoading ? (
                            <div className="rounded-[24px] border border-white/10 bg-white/[0.04] px-5 py-12 text-center text-sm text-cream-dim">
                                Loading cases...
                            </div>
                        ) : cases.length === 0 ? (
                            <div className="rounded-[24px] border border-dashed border-white/12 bg-white/[0.03] px-5 py-12 text-center text-sm text-cream-dim">
                                No historical cases found.
                            </div>
                        ) : (
                            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                                {cases.map((item: any) => (
                                    <button
                                        key={item.id}
                                        onClick={() => navigate(`/workspace/${item.id}`)}
                                        className="rounded-[24px] border border-white/10 bg-white/[0.04] p-5 text-left transition-transform duration-200 hover:-translate-y-1"
                                    >
                                        <div className="flex items-start justify-between gap-3">
                                            <DoodleIcon name="dashboard" alt="Case doodle" size="sm" />
                                            <span className="doodle-chip text-[10px] font-bold uppercase tracking-[0.18em]">
                                                {item.status}
                                            </span>
                                        </div>
                                        <h3 className="mt-4 text-lg font-bold text-cream-bright">
                                            {item.device_info?.name || 'Unnamed Investigation'}
                                        </h3>
                                        <div className="mt-4 space-y-2 text-xs text-cream-dim">
                                            <p>Investigator: {item.investigator}</p>
                                            <p>Mode: {item.mode}</p>
                                            <p>Date: {new Date(item.created_at).toLocaleDateString()}</p>
                                        </div>
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>
                </section>
            </div>
        </PageTransition>
    )
}
