import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getInvestigationStatus, startInvestigation } from '@/api/client'
import DoodleIcon, { type DoodleName } from '@/components/DoodleIcon'
import PageTransition from '@/components/PageTransition'
import SpatialDeviceCard from '@/components/SpatialDeviceCard'
import { useAppStore } from '@/store/appStore'
import { useAuthStore } from '@/store/authStore'

const MODES = [
    {
        id: 'full_auto',
        label: 'Full Auto',
        desc: 'Complete automated analysis covering file system, malware, artifacts, timeline, and AI interpretation.',
        doodle: 'dashboard',
    },
    {
        id: 'hybrid',
        label: 'Hybrid',
        desc: 'Automated scan with analyst checkpoints before key evidence decisions.',
        doodle: 'alerts',
    },
    {
        id: 'manual',
        label: 'Manual',
        desc: 'Step-by-step investigator-led review with lighter automation support.',
        doodle: 'legal',
    },
] satisfies { id: string; label: string; desc: string; doodle: DoodleName }[]

const STEP_LABELS = ['Select device', 'Choose mode', 'Investigator', 'Confirm']

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

    useEffect(() => {
        fetchDevices()
    }, [])

    const handleStart = async () => {
        if(selectedDevice === null) return
        const device = devices[selectedDevice]
        setIsRunning(true)
        setProgressStep('Starting investigation...')

        try {
            const response = await startInvestigation({
                device_path: device.path,
                mount_point: device.mount_point,
                device_name: device.name,
                mode: selectedMode,
                investigator,
            })

            setCaseId(response.case_id)

            const poll = setInterval(async () => {
                try {
                    const status = await getInvestigationStatus(response.case_id)
                    setProgress(status.progress)
                    setProgressStep(status.step)
                    if(status.status === 'completed' || status.status === 'error') {
                        clearInterval(poll)
                        setIsRunning(false)
                        if(status.status === 'completed') {
                            navigate(`/workspace/${response.case_id}`)
                        }
                    }
                } catch {
                    clearInterval(poll)
                    setIsRunning(false)
                }
            }, 1500)
        } catch(error: any) {
            setIsRunning(false)
            setProgressStep(`Error: ${error.message}`)
        }
    }

    return (
        <PageTransition>
            <div className="h-full overflow-y-auto space-y-5">
                <section className="doodle-panel p-6">
                    <div className="relative z-10">
                        <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
                            <div className="flex items-center gap-4">
                                <DoodleIcon name="usb-drive" alt="Investigation doodle" size="lg" />
                                <div>
                                    <h1 className="text-3xl font-black text-cream-bright font-heading">
                                        New Investigation
                                    </h1>
                                    <p className="mt-2 text-sm text-cream-dim">
                                        Assemble a clean investigation workspace with the new doodle-led setup flow.
                                    </p>
                                </div>
                            </div>
                            <span className="doodle-chip self-start text-[10px] font-bold uppercase tracking-[0.18em]">
                                Step {step} of 4
                            </span>
                        </div>

                        <div className="mt-6 grid gap-3 md:grid-cols-4">
                            {STEP_LABELS.map((label, index) => {
                                const currentStep = index + 1
                                const isActive = currentStep === step
                                const isComplete = currentStep < step

                                return (
                                    <div
                                        key={label}
                                        className={[
                                            'rounded-[22px] border p-4 transition-colors',
                                            isActive
                                                ? 'border-accent/35 bg-accent/18'
                                                : isComplete
                                                    ? 'border-white/12 bg-white/[0.05]'
                                                    : 'border-white/8 bg-white/[0.03]',
                                        ].join(' ')}
                                    >
                                        <p className="text-[10px] uppercase tracking-[0.18em] text-cream-dim">
                                            Step {currentStep}
                                        </p>
                                        <p className="mt-2 text-sm font-semibold text-cream-bright">{label}</p>
                                        <p className="mt-2 text-xs text-cream-dim">
                                            {isComplete ? 'Ready' : isActive ? 'Current' : 'Pending'}
                                        </p>
                                    </div>
                                )
                            })}
                        </div>
                    </div>
                </section>

                <section className="doodle-panel p-6">
                    <div className="relative z-10">
                        {isRunning ? (
                            <div className="mx-auto max-w-2xl py-10 text-center">
                                <DoodleIcon
                                    name="dashboard"
                                    alt="Running investigation doodle"
                                    size="xl"
                                    className="mx-auto animate-pulse"
                                />
                                <h2 className="mt-5 text-3xl font-black text-cream-bright font-heading">
                                    Investigation in progress
                                </h2>
                                <p className="mt-3 text-sm text-cream-dim">{progressStep || 'Starting investigation...'}</p>
                                {caseId && (
                                    <p className="mt-2 text-[10px] uppercase tracking-[0.18em] text-cream-dim">
                                        Case ID: {caseId}
                                    </p>
                                )}

                                <div className="mt-8 overflow-hidden rounded-full bg-black/15">
                                    <div
                                        className="h-3 rounded-full bg-accent transition-all duration-500"
                                        style={{ width: `${progress}%` }}
                                    />
                                </div>
                                <p className="mt-3 text-sm font-semibold text-cream-bright">{progress}% complete</p>
                            </div>
                        ) : (
                            <>
                                {step === 1 && (
                                    <div>
                                        <div className="mb-5 flex items-center gap-3">
                                            <DoodleIcon name="usb-drive" alt="Device selection doodle" size="md" />
                                            <div>
                                                <h2 className="text-xl font-black text-cream-bright font-heading">
                                                    Select target device
                                                </h2>
                                                <p className="text-sm text-cream-dim">
                                                    Choose the attached source you want to inspect first.
                                                </p>
                                            </div>
                                        </div>

                                        {devices.length === 0 ? (
                                            <div className="rounded-[24px] border border-white/10 bg-white/[0.04] px-5 py-12 text-center">
                                                <DoodleIcon
                                                    name="usb-drive"
                                                    alt="No device doodle"
                                                    size="md"
                                                    className="mx-auto mb-4"
                                                />
                                                <p className="text-lg font-semibold text-cream-bright">
                                                    No devices detected
                                                </p>
                                                <p className="mt-2 text-sm text-cream-dim">
                                                    Connect a drive and refresh to begin a new case.
                                                </p>
                                                <button
                                                    onClick={() => fetchDevices()}
                                                    className="doodle-button mt-5 px-4 py-2 text-sm font-semibold"
                                                >
                                                    Refresh devices
                                                </button>
                                            </div>
                                        ) : (
                                            <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
                                                {devices.map((device, index) => (
                                                    <div
                                                        key={`${device.mount_point}-${index}`}
                                                        onClick={() => setSelectedDevice(index)}
                                                        className={[
                                                            'cursor-pointer rounded-[28px] transition-all duration-200',
                                                            selectedDevice === index
                                                                ? 'ring-2 ring-accent ring-offset-4 ring-offset-servos-bg'
                                                                : '',
                                                        ].join(' ')}
                                                    >
                                                        <SpatialDeviceCard device={device} />
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                )}

                                {step === 2 && (
                                    <div className="max-w-4xl">
                                        <div className="mb-5 flex items-center gap-3">
                                            <DoodleIcon name="dashboard" alt="Mode selection doodle" size="md" />
                                            <div>
                                                <h2 className="text-xl font-black text-cream-bright font-heading">
                                                    Choose investigation mode
                                                </h2>
                                                <p className="text-sm text-cream-dim">
                                                    Pick the level of automation and analyst control you want.
                                                </p>
                                            </div>
                                        </div>

                                        <div className="grid gap-4 lg:grid-cols-3">
                                            {MODES.map((mode) => (
                                                <button
                                                    key={mode.id}
                                                    onClick={() => setSelectedMode(mode.id)}
                                                    className={[
                                                        'rounded-[26px] border p-5 text-left transition-transform duration-200 hover:-translate-y-1',
                                                        selectedMode === mode.id
                                                            ? 'border-accent/35 bg-accent/18'
                                                            : 'border-white/10 bg-white/[0.04]',
                                                    ].join(' ')}
                                                >
                                                    <DoodleIcon
                                                        name={mode.doodle}
                                                        alt={`${mode.label} doodle`}
                                                        size="md"
                                                    />
                                                    <h3 className="mt-4 text-lg font-bold text-cream-bright">{mode.label}</h3>
                                                    <p className="mt-2 text-sm leading-6 text-cream-dim">{mode.desc}</p>
                                                </button>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {step === 3 && (
                                    <div className="max-w-xl">
                                        <div className="mb-5 flex items-center gap-3">
                                            <DoodleIcon name="legal" alt="Investigator details doodle" size="md" />
                                            <div>
                                                <h2 className="text-xl font-black text-cream-bright font-heading">
                                                    Investigator details
                                                </h2>
                                                <p className="text-sm text-cream-dim">
                                                    Add the analyst name that should appear in the case record.
                                                </p>
                                            </div>
                                        </div>

                                        <div className="rounded-[26px] border border-white/10 bg-white/[0.04] p-5">
                                            <label className="block text-[10px] font-semibold uppercase tracking-[0.18em] text-cream-dim">
                                                Investigator name
                                            </label>
                                            <input
                                                type="text"
                                                value={investigator}
                                                onChange={(event) => setInvestigator(event.target.value)}
                                                className="mt-3 w-full rounded-[18px] border border-white/10 bg-servos-surface px-4 py-3 text-sm text-cream-bright outline-none transition-colors focus:border-accent/40"
                                            />
                                        </div>
                                    </div>
                                )}

                                {step === 4 && selectedDevice !== null && (
                                    <div className="max-w-2xl">
                                        <div className="mb-5 flex items-center gap-3">
                                            <DoodleIcon name="alerts" alt="Confirmation doodle" size="md" />
                                            <div>
                                                <h2 className="text-xl font-black text-cream-bright font-heading">
                                                    Confirm setup
                                                </h2>
                                                <p className="text-sm text-cream-dim">
                                                    Review the case details before launching the scan.
                                                </p>
                                            </div>
                                        </div>

                                        <div className="grid gap-3 sm:grid-cols-2">
                                            {[
                                                ['Device', devices[selectedDevice]?.name || devices[selectedDevice]?.mount_point],
                                                ['Mount point', devices[selectedDevice]?.mount_point],
                                                ['Mode', MODES.find((mode) => mode.id === selectedMode)?.label],
                                                ['Investigator', investigator || 'Unassigned'],
                                            ].map(([label, value]) => (
                                                <div
                                                    key={label}
                                                    className="rounded-[22px] border border-white/10 bg-white/[0.04] p-4"
                                                >
                                                    <p className="text-[10px] uppercase tracking-[0.18em] text-cream-dim">
                                                        {label}
                                                    </p>
                                                    <p className="mt-2 text-sm font-semibold text-cream-bright">
                                                        {value}
                                                    </p>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                <div className="mt-8 flex flex-wrap items-center justify-between gap-3">
                                    <button
                                        onClick={() => setStep(Math.max(1, step - 1))}
                                        disabled={step === 1}
                                        className="doodle-button px-4 py-2 text-sm font-semibold disabled:opacity-40"
                                    >
                                        Back
                                    </button>

                                    {step < 4 ? (
                                        <button
                                            onClick={() => setStep(step + 1)}
                                            disabled={step === 1 && selectedDevice === null}
                                            className="doodle-button doodle-button-primary px-5 py-2 text-sm font-semibold disabled:opacity-40"
                                        >
                                            Next step
                                        </button>
                                    ) : (
                                        <button
                                            onClick={handleStart}
                                            className="doodle-button doodle-button-primary px-5 py-2 text-sm font-semibold"
                                        >
                                            Start investigation
                                        </button>
                                    )}
                                </div>
                            </>
                        )}
                    </div>
                </section>
            </div>
        </PageTransition>
    )
}
