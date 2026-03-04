import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAppStore } from '@/store/appStore'
import { useAuthStore } from '@/store/authStore'
import { startInvestigation, getInvestigationStatus } from '@/api/client'
import PageTransition from '@/components/PageTransition'
import SpatialDeviceCard from '@/components/SpatialDeviceCard'
import { ChevronRight, ChevronLeft, Play, CheckCircle2, Loader2 } from 'lucide-react'

const MODES = [
    { id: 'full_auto', label: 'Full Auto', desc: 'Complete automated analysis — file system, malware, artifacts, timeline, AI interpretation' },
    { id: 'hybrid', label: 'Hybrid', desc: 'Automated scan with manual review checkpoints' },
    { id: 'manual', label: 'Manual', desc: 'Step-by-step manual investigation with AI guidance' },
]

export default function InvestigatePage() {
    const navigate = useNavigate()
    const { devices, fetchDevices } = useAppStore()
    const { username } = useAuthStore()
    const [step, setStep] = useState(1)
    const [selectedDevice, setSelectedDevice] = useState<number | null>(null)
    const [selectedMode, setSelectedMode] = useState('full_auto')
    const [investigator, setInvestigator] = useState(username)
    const [isRunning, setIsRunning] = useState(false)
    const [progress, setProgress] = useState(0)
    const [progressStep, setProgressStep] = useState('')
    const [caseId, setCaseId] = useState<string | null>(null)

    useEffect(() => { fetchDevices() }, [])

    const handleStart = async () => {
        if(selectedDevice === null) return
        const device = devices[selectedDevice]
        setIsRunning(true)
        setProgressStep('Starting investigation...')

        try {
            const res = await startInvestigation({
                device_path: device.path,
                mount_point: device.mount_point,
                device_name: device.name,
                mode: selectedMode,
                investigator,
            })
            setCaseId(res.case_id)

            // Poll status
            const poll = setInterval(async () => {
                try {
                    const status = await getInvestigationStatus(res.case_id)
                    setProgress(status.progress)
                    setProgressStep(status.step)
                    if(status.status === 'completed' || status.status === 'error') {
                        clearInterval(poll)
                        setIsRunning(false)
                        if(status.status === 'completed') {
                            navigate(`/workspace/${res.case_id}`)
                        }
                    }
                } catch { clearInterval(poll); setIsRunning(false) }
            }, 1500)
        } catch(err: any) {
            setIsRunning(false)
            setProgressStep(`Error: ${err.message}`)
        }
    }

    return (
        <PageTransition>
            <div className="h-full overflow-y-auto p-6">
                {/* Header */}
                <div className="mb-6">
                    <h1 className="text-xl font-bold text-cream-bright">New Investigation</h1>
                    <p className="text-xs text-cream-dim mt-1">Step {step} of 4</p>
                </div>

                {/* Progress bar */}
                <div className="flex gap-1 mb-8">
                    {[1, 2, 3, 4].map((s) => (
                        <div key={s} className={`flex-1 h-1 rounded-full transition-colors duration-300 ${s <= step ? 'bg-accent' : 'bg-servos-border'
                            }`} />
                    ))}
                </div>

                {/* Running state */}
                {isRunning ? (
                    <div className="max-w-lg mx-auto text-center py-12">
                        <Loader2 size={32} className="text-accent mx-auto mb-4 animate-spin" />
                        <h2 className="text-lg font-semibold text-cream-bright mb-2">Investigation in Progress</h2>
                        <p className="text-sm text-cream-dim mb-6">{progressStep}</p>
                        <div className="w-full h-2 bg-servos-border rounded-full overflow-hidden">
                            <div className="h-full bg-accent rounded-full transition-all duration-500" style={{ width: `${progress}%` }} />
                        </div>
                        <p className="text-[11px] text-cream-dim mt-2">{progress}% complete</p>
                    </div>
                ) : (
                    <>
                        {/* Step 1: Select Device */}
                        {step === 1 && (
                            <div>
                                <h2 className="text-sm font-semibold text-cream mb-4">Select Target Device</h2>
                                {devices.length === 0 ? (
                                    <p className="text-sm text-cream-dim py-8 text-center">No devices found. Connect a device and refresh.</p>
                                ) : (
                                    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
                                        {devices.map((d, i) => (
                                            <div
                                                key={i}
                                                className={`cursor-pointer rounded-lg transition-all ${selectedDevice === i ? 'ring-2 ring-accent ring-offset-2 ring-offset-servos-bg' : ''
                                                    }`}
                                                onClick={() => setSelectedDevice(i)}
                                            >
                                                <SpatialDeviceCard device={d} />
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Step 2: Select Mode */}
                        {step === 2 && (
                            <div className="max-w-xl">
                                <h2 className="text-sm font-semibold text-cream mb-4">Select Investigation Mode</h2>
                                <div className="space-y-2">
                                    {MODES.map((m) => (
                                        <button
                                            key={m.id}
                                            onClick={() => setSelectedMode(m.id)}
                                            className={`w-full text-left p-4 rounded-lg border transition-colors ${selectedMode === m.id
                                                    ? 'bg-accent-muted border-accent text-cream-bright'
                                                    : 'bg-servos-surface border-servos-border text-cream hover:border-accent/30'
                                                }`}
                                        >
                                            <p className="text-sm font-semibold">{m.label}</p>
                                            <p className="text-[11px] text-cream-dim mt-1">{m.desc}</p>
                                        </button>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Step 3: Investigator Details */}
                        {step === 3 && (
                            <div className="max-w-md">
                                <h2 className="text-sm font-semibold text-cream mb-4">Investigator Details</h2>
                                <label className="block text-[11px] font-semibold text-cream-dim uppercase tracking-wider mb-1.5">
                                    Investigator Name
                                </label>
                                <input
                                    type="text"
                                    value={investigator}
                                    onChange={(e) => setInvestigator(e.target.value)}
                                    className="w-full bg-servos-bg border border-servos-border rounded-lg py-2.5 px-3 text-sm text-cream focus:border-accent focus:outline-none"
                                />
                            </div>
                        )}

                        {/* Step 4: Confirmation */}
                        {step === 4 && selectedDevice !== null && (
                            <div className="max-w-lg">
                                <h2 className="text-sm font-semibold text-cream mb-4">Confirm Investigation</h2>
                                <div className="bg-servos-surface border border-servos-border rounded-lg p-5 space-y-3">
                                    {[
                                        ['Device', devices[selectedDevice]?.name || devices[selectedDevice]?.mount_point],
                                        ['Mount Point', devices[selectedDevice]?.mount_point],
                                        ['Mode', MODES.find(m => m.id === selectedMode)?.label],
                                        ['Investigator', investigator],
                                    ].map(([k, v]) => (
                                        <div key={k} className="flex justify-between text-sm">
                                            <span className="text-cream-dim">{k}</span>
                                            <span className="text-cream font-medium">{v}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Navigation buttons */}
                        <div className="flex items-center justify-between mt-8">
                            <button
                                onClick={() => setStep(Math.max(1, step - 1))}
                                disabled={step === 1}
                                className="flex items-center gap-1 px-4 py-2 text-sm text-cream-dim hover:text-cream disabled:opacity-30 transition-colors"
                            >
                                <ChevronLeft size={14} /> Back
                            </button>

                            {step < 4 ? (
                                <button
                                    onClick={() => setStep(step + 1)}
                                    disabled={step === 1 && selectedDevice === null}
                                    className="flex items-center gap-1 px-5 py-2 bg-accent hover:bg-accent-dark text-white text-sm font-semibold rounded-lg disabled:opacity-40 transition-colors"
                                >
                                    Next <ChevronRight size={14} />
                                </button>
                            ) : (
                                <button
                                    onClick={handleStart}
                                    className="flex items-center gap-2 px-5 py-2 bg-accent hover:bg-accent-dark text-white text-sm font-semibold rounded-lg transition-colors"
                                >
                                    <Play size={14} /> Start Investigation
                                </button>
                            )}
                        </div>
                    </>
                )}
            </div>
        </PageTransition>
    )
}
