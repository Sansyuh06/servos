import { HardDrive, Usb, Server, AlertTriangle, ShieldCheck, Clock, Hash, Archive, Search } from 'lucide-react'
import type { Device } from '@/api/client'

const DISK_ICONS: Record<string, typeof HardDrive> = {
    USB: Usb,
    HDD: HardDrive,
    SSD: Server,
    External: HardDrive,
}

function formatBytes(bytes: number | undefined | null): string {
    if(!bytes || bytes <= 0 || isNaN(bytes)) return '—'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`
}

interface Props {
    device: Device
    onAnalyze?: () => void
    onBackup?: () => void
}

/**
 * Spatial Device Card — forensic-grade disk display.
 * Layered depth, subtle elevation, dark forensic theme.
 * No playful lighting, no glassmorphism.
 */
export default function SpatialDeviceCard({ device, onAnalyze, onBackup }: Props) {
    const usedBytes = device.used_bytes || 0
    const usedPct = (device.capacity_bytes > 0 && usedBytes > 0)
        ? Math.round((usedBytes / device.capacity_bytes) * 100)
        : 0
    const hasUsageData = usedBytes > 0 && device.capacity_bytes > 0
    const diskType = device.is_removable ? 'USB' : 'HDD'
    const Icon = DISK_ICONS[diskType] || HardDrive

    return (
        <div className="group relative bg-servos-surface border border-servos-border rounded-lg p-5 hover:border-accent/30 transition-all duration-200">
            {/* Top row: icon + disk type */}
            <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-accent-muted border border-accent-muted-border flex items-center justify-center">
                        <Icon size={18} className="text-accent" />
                    </div>
                    <div>
                        <h3 className="text-sm font-semibold text-cream-bright leading-tight">
                            {device.name || device.mount_point}
                        </h3>
                        <p className="text-[11px] text-cream-dim mt-0.5">
                            {diskType} • {device.filesystem || 'Unknown FS'}
                        </p>
                    </div>
                </div>

                {/* Risk badge */}
                <span className="px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider rounded-md bg-success-muted text-success border border-success/20">
                    Low Risk
                </span>
            </div>

            {/* Specs grid */}
            <div className="grid grid-cols-2 gap-x-6 gap-y-2 mb-4 text-[11px]">
                <div className="flex items-center gap-1.5 text-cream-dim">
                    <HardDrive size={11} />
                    <span>Size:</span>
                    <span className="text-cream ml-auto font-medium">{formatBytes(device.capacity_bytes)}</span>
                </div>
                <div className="flex items-center gap-1.5 text-cream-dim">
                    <Archive size={11} />
                    <span>Mount:</span>
                    <span className="text-cream ml-auto font-medium font-mono text-[10px]">{device.mount_point}</span>
                </div>
                <div className="flex items-center gap-1.5 text-cream-dim">
                    <Hash size={11} />
                    <span>Serial:</span>
                    <span className="text-cream ml-auto font-mono text-[10px]">{device.serial_number?.slice(0, 8) || '—'}</span>
                </div>
                <div className="flex items-center gap-1.5 text-cream-dim">
                    <Clock size={11} />
                    <span>Status:</span>
                    <span className="text-success ml-auto font-medium">Connected</span>
                </div>
            </div>

            {/* Usage bar */}
            <div className="mb-4">
                <div className="flex items-center justify-between text-[10px] text-cream-dim mb-1">
                    <span>Usage</span>
                    <span>{hasUsageData ? `${usedPct}% — ${formatBytes(usedBytes)} / ${formatBytes(device.capacity_bytes)}` : formatBytes(device.capacity_bytes)}</span>
                </div>
                <div className="w-full h-1.5 bg-servos-bg rounded-full overflow-hidden">
                    <div
                        className="h-full rounded-full transition-all duration-500"
                        style={{
                            width: `${usedPct}%`,
                            background: usedPct > 90 ? '#C85A5A' : usedPct > 70 ? '#C4935A' : '#8F7DBA',
                        }}
                    />
                </div>
            </div>

            {/* Actions */}
            <div className="flex gap-2">
                <button
                    onClick={onBackup}
                    className="flex-1 flex items-center justify-center gap-1.5 py-2 text-[11px] font-semibold text-cream-dim bg-servos-bg border border-servos-border rounded-md hover:border-accent/30 hover:text-cream transition-colors"
                >
                    <Archive size={12} />
                    Enforce Backup
                </button>
                <button
                    onClick={onAnalyze}
                    className="flex-1 flex items-center justify-center gap-1.5 py-2 text-[11px] font-semibold text-white bg-accent hover:bg-accent-dark rounded-md transition-colors"
                >
                    <Search size={12} />
                    Analyze
                </button>
            </div>
        </div>
    )
}
