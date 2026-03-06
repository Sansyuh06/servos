import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    HardDrive,
    Cpu,
    Monitor,
    Activity,
    LucideIcon,
    ShieldAlert,
    Search,
    Settings
} from 'lucide-react';

const DEVICE_DATA = [
    {
        id: 'intel-ssd',
        name: 'Primary OS Drive',
        company: 'Intel Corp.',
        model: 'SSD 660p Series',
        type: 'Storage',
        status: 'High Risk',
        color: '#ef4444',
        icon: HardDrive,
        stats: { capacity: '512GB', format: 'NTFS', encrypted: 'No', health: '82%' },
        features: [
            { name: 'MFT Analyzed', icon: Search, value: 'Yes' },
            { name: 'Suspicious Files', icon: ShieldAlert, value: '14' },
            { name: 'BitLocker', icon: Settings, value: 'Disabled' },
            { name: 'SMART Status', icon: Activity, value: 'Warning' }
        ]
    },
    {
        id: 'usb-kingston',
        name: 'Attached USB',
        company: 'Kingston Tech.',
        model: 'DataTraveler 3.0',
        type: 'Removable',
        status: 'Analyzing',
        color: '#eab308',
        icon: HardDrive,
        stats: { capacity: '32GB', format: 'FAT32', encrypted: 'No', health: '100%' },
        features: [
            { name: 'MFT Analyzed', icon: Search, value: 'Pending' },
            { name: 'Suspicious Files', icon: ShieldAlert, value: '?' },
            { name: 'BitLocker', icon: Settings, value: 'N/A' },
            { name: 'SMART Status', icon: Activity, value: 'Good' }
        ]
    }
];

export default function SpatialDeviceShowcase() {
    const [activeIndex, setActiveIndex] = useState(0);
    const activeDevice = DEVICE_DATA[activeIndex];

    return (
        <div className="relative w-full h-[600px] bg-servos-bg border border-servos-border rounded-2xl overflow-hidden flex flex-col pt-12">
            {/* Background Gradient */}
            <AnimatePresence>
                <motion.div
                    key={activeDevice.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 0.15 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 1 }}
                    className="absolute inset-0 z-0 blur-3xl"
                    style={{ background: `radial-gradient(circle at 50% 50%, ${activeDevice.color}, transparent 60%)` }}
                />
            </AnimatePresence>

            <div className="z-10 px-10 pt-4 pb-0 flex flex-col itms-center h-full">
                <div className="flex justify-between items-start w-full mb-12">
                    <div className="flex flex-col gap-2">
                        <motion.h2
                            key={`${activeDevice.id}-title`}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="text-4xl font-bold text-white tracking-tight"
                        >
                            {activeDevice.name}
                        </motion.h2>
                        <motion.p
                            key={`${activeDevice.id}-subtitle`}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.1 }}
                            className="text-cream-dim text-lg flex space-x-2 items-center"
                        >
                            <span>{activeDevice.company}</span>
                            <span>•</span>
                            <span>{activeDevice.model}</span>
                        </motion.p>
                    </div>

                    <motion.div
                        key={`${activeDevice.id}-status`}
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className={`px-4 py-2 rounded-full border bg-servos-surface/80 backdrop-blur-md shadow-lg
                     ${activeDevice.status === 'High Risk' ? 'border-red-500/50 text-red-400' : 'border-orange-500/50 text-orange-400'}`}
                    >
                        {activeDevice.status}
                    </motion.div>
                </div>

                <div className="relative flex-1 flex justify-center items-center">
                    {/* 3D Representation Placeholder */}
                    <motion.div
                        key={`${activeDevice.id}-image`}
                        initial={{ opacity: 0, scale: 0.8, rotateY: -30 }}
                        animate={{ opacity: 1, scale: 1, rotateY: 0 }}
                        transition={{ type: "spring", stiffness: 100, damping: 20 }}
                        className="w-64 h-64 border-2 border-servos-border/50 bg-gradient-to-br from-servos-surface to-servos-bg rounded-3xl shadow-2xl flex items-center justify-center transform perspective-1000"
                        style={{ transformStyle: 'preserve-3d' }}
                    >
                        <activeDevice.icon className="w-32 h-32 text-accent drop-shadow-2xl" />
                    </motion.div>
                </div>
            </div>

            {/* Floating Control Dock */}
            <div className="absolute bottom-8 left-1/2 -translate-x-1/2 z-20">
                <div className="flex space-x-2 p-2 bg-servos-surface/80 backdrop-blur-xl border border-servos-border rounded-full shadow-2xl">
                    {DEVICE_DATA.map((device, idx) => (
                        <button
                            key={device.id}
                            onClick={() => setActiveIndex(idx)}
                            className={`relative px-6 py-3 rounded-full text-sm font-medium transition-colors ${activeIndex === idx ? 'text-cream-bright' : 'text-cream-dim hover:text-cream-bright'}`}
                        >
                            {activeIndex === idx && (
                                <motion.div
                                    layoutId="active-pill"
                                    className="absolute inset-0 bg-servos-card rounded-full -z-10 shadow-inner"
                                    initial={false}
                                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                                />
                            )}
                            <span className="relative z-10 flex items-center space-x-2">
                                <device.icon className="w-4 h-4" />
                                <span>{device.name}</span>
                            </span>
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
}
