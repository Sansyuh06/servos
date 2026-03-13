import { useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import DoodleIcon, { type DoodleName } from '@/components/DoodleIcon'

const DEVICE_DATA = [
    {
        id: 'intel-ssd',
        name: 'Primary OS Drive',
        company: 'Intel Corp.',
        model: 'SSD 660p Series',
        status: 'High Risk',
        doodle: 'hdd-drive',
        stats: { capacity: '512GB', format: 'NTFS', encrypted: 'No', health: '82%' },
        features: ['MFT analyzed', '14 suspicious files', 'BitLocker disabled', 'SMART warning'],
    },
    {
        id: 'usb-kingston',
        name: 'Attached USB',
        company: 'Kingston Tech.',
        model: 'DataTraveler 3.0',
        status: 'Analyzing',
        doodle: 'usb-drive',
        stats: { capacity: '32GB', format: 'FAT32', encrypted: 'No', health: '100%' },
        features: ['MFT pending', 'Suspicious files pending', 'Portable media', 'Healthy'],
    },
] satisfies {
    id: string
    name: string
    company: string
    model: string
    status: string
    doodle: DoodleName
    stats: Record<string, string>
    features: string[]
}[]

export default function SpatialDeviceShowcase() {
    const [activeIndex, setActiveIndex] = useState(0)
    const activeDevice = DEVICE_DATA[activeIndex]

    return (
        <div className="doodle-panel h-[600px] w-full p-8">
            <div className="relative z-10 flex h-full flex-col justify-between">
                <div className="flex items-start justify-between gap-6">
                    <div>
                        <p className="text-[11px] uppercase tracking-[0.2em] text-cream-dim">Device showcase</p>
                        <h2 className="mt-3 text-4xl font-black text-cream-bright font-heading">
                            {activeDevice.name}
                        </h2>
                        <p className="mt-3 text-sm text-cream-dim">
                            {activeDevice.company} / {activeDevice.model}
                        </p>
                    </div>
                    <span className="doodle-chip text-[10px] font-bold uppercase tracking-[0.18em]">
                        {activeDevice.status}
                    </span>
                </div>

                <div className="grid flex-1 items-center gap-8 lg:grid-cols-[0.95fr_1.05fr]">
                    <div className="flex justify-center">
                        <AnimatePresence mode="wait">
                            <motion.div
                                key={activeDevice.id}
                                initial={{ opacity: 0, y: 12, scale: 0.96 }}
                                animate={{ opacity: 1, y: 0, scale: 1 }}
                                exit={{ opacity: 0, y: -12, scale: 0.96 }}
                                className="rounded-[36px] border border-white/10 bg-white/[0.04] p-8"
                            >
                                <DoodleIcon
                                    name={activeDevice.doodle}
                                    alt={`${activeDevice.name} doodle`}
                                    size="xl"
                                    className="h-44 w-44 rounded-[38px]"
                                    imageClassName="p-5"
                                />
                            </motion.div>
                        </AnimatePresence>
                    </div>

                    <div className="space-y-5">
                        <div className="grid gap-3 sm:grid-cols-2">
                            {Object.entries(activeDevice.stats).map(([key, value]) => (
                                <div key={key} className="rounded-[22px] border border-white/10 bg-white/[0.04] p-4">
                                    <p className="text-[10px] uppercase tracking-[0.18em] text-cream-dim">{key}</p>
                                    <p className="mt-2 text-sm font-semibold text-cream-bright">{value}</p>
                                </div>
                            ))}
                        </div>

                        <div className="rounded-[24px] border border-white/10 bg-white/[0.04] p-5">
                            <p className="text-[10px] uppercase tracking-[0.18em] text-cream-dim">Feature notes</p>
                            <div className="mt-4 flex flex-wrap gap-2">
                                {activeDevice.features.map((feature) => (
                                    <span key={feature} className="doodle-chip text-xs font-semibold">
                                        {feature}
                                    </span>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>

                <div className="flex justify-center gap-2">
                    {DEVICE_DATA.map((device, index) => (
                        <button
                            key={device.id}
                            onClick={() => setActiveIndex(index)}
                            className={[
                                'doodle-button flex items-center gap-2 px-4 py-2 text-sm font-semibold',
                                index === activeIndex ? 'doodle-button-primary' : '',
                            ].join(' ')}
                        >
                            <DoodleIcon name={device.doodle} alt={`${device.name} doodle`} size="sm" className="h-8 w-8 rounded-[16px]" />
                            {device.name}
                        </button>
                    ))}
                </div>
            </div>
        </div>
    )
}
