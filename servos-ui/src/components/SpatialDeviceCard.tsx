import DoodleIcon from '@/components/DoodleIcon'
import type { Device } from '@/api/client'

function formatBytes(bytes: number | undefined | null): string {
    if(!bytes || bytes <= 0 || Number.isNaN(bytes)) return '--'
    const units = ['B', 'KB', 'MB', 'GB', 'TB']
    let value = bytes
    let unit = 0
    while(value >= 1024 && unit < units.length - 1) {
        value /= 1024
        unit += 1
    }
    return `${value.toFixed(1)} ${units[unit]}`
}

interface Props {
    device: Device
    onAnalyze?: () => void
    onBackup?: () => void
}

export default function SpatialDeviceCard({ device, onAnalyze, onBackup }: Props) {
    const usedBytes = device.used_bytes || 0
    const capacityBytes = device.capacity_bytes || 0
    const usagePercent = capacityBytes > 0 ? Math.min(100, Math.round((usedBytes / capacityBytes) * 100)) : 0
    const doodle = device.is_removable ? 'usb-drive' : 'hdd-drive'

    return (
        <div className="doodle-panel p-5">
            <div className="relative z-10">
                <div className="flex items-start justify-between gap-4">
                    <div className="flex items-center gap-3">
                        <DoodleIcon
                            name={doodle}
                            alt={`${device.name || 'Storage device'} doodle`}
                            size="lg"
                            className="bg-accent/20"
                        />
                        <div>
                            <h3 className="text-base font-bold text-cream-bright">{device.name || device.mount_point}</h3>
                            <p className="mt-1 text-[11px] uppercase tracking-[0.2em] text-cream-dim">
                                {device.is_removable ? 'USB evidence source' : 'Mounted storage volume'}
                            </p>
                        </div>
                    </div>

                    <span className="doodle-chip text-[10px] font-bold uppercase tracking-[0.2em] text-success">
                        Connected
                    </span>
                </div>

                <div className="mt-5 grid grid-cols-2 gap-3">
                    <div className="rounded-[20px] border border-white/8 bg-white/[0.035] p-3">
                        <p className="text-[10px] uppercase tracking-[0.18em] text-cream-dim">Filesystem</p>
                        <p className="mt-2 text-sm font-semibold text-cream-bright">{device.filesystem || 'Unknown'}</p>
                    </div>
                    <div className="rounded-[20px] border border-white/8 bg-white/[0.035] p-3">
                        <p className="text-[10px] uppercase tracking-[0.18em] text-cream-dim">Mount point</p>
                        <p className="mt-2 truncate font-mono text-xs text-cream-bright">{device.mount_point || '--'}</p>
                    </div>
                    <div className="rounded-[20px] border border-white/8 bg-white/[0.035] p-3">
                        <p className="text-[10px] uppercase tracking-[0.18em] text-cream-dim">Capacity</p>
                        <p className="mt-2 text-sm font-semibold text-cream-bright">{formatBytes(capacityBytes)}</p>
                    </div>
                    <div className="rounded-[20px] border border-white/8 bg-white/[0.035] p-3">
                        <p className="text-[10px] uppercase tracking-[0.18em] text-cream-dim">Serial</p>
                        <p className="mt-2 truncate font-mono text-xs text-cream-bright">{device.serial_number || '--'}</p>
                    </div>
                </div>

                <div className="mt-5 rounded-[22px] border border-white/8 bg-white/[0.03] p-4">
                    <div className="mb-2 flex items-center justify-between text-[11px] text-cream-dim">
                        <span className="uppercase tracking-[0.18em]">Usage sketch</span>
                        <span>{capacityBytes > 0 ? `${usagePercent}%` : 'No data'}</span>
                    </div>
                    <div className="h-3 overflow-hidden rounded-full bg-black/15">
                        <div
                            className="h-full rounded-full bg-accent transition-all duration-500"
                            style={{ width: `${usagePercent}%` }}
                        />
                    </div>
                    <p className="mt-2 text-xs text-cream-dim">
                        {usedBytes > 0 && capacityBytes > 0
                            ? `${formatBytes(usedBytes)} used out of ${formatBytes(capacityBytes)}`
                            : 'Usage metadata is not available for this device yet.'}
                    </p>
                </div>

                <div className="mt-5 flex flex-wrap gap-2">
                    <button
                        onClick={onBackup}
                        className="doodle-button px-4 py-2 text-sm font-semibold"
                    >
                        Backup first
                    </button>
                    <button
                        onClick={onAnalyze}
                        className="doodle-button doodle-button-primary px-4 py-2 text-sm font-semibold"
                    >
                        Analyze device
                    </button>
                </div>
            </div>
        </div>
    )
}
