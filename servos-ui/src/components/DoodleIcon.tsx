type DoodleName =
    | 'alerts'
    | 'chat'
    | 'dashboard'
    | 'hdd-drive'
    | 'legal'
    | 'network'
    | 'settings'
    | 'threat'
    | 'usb-drive'

const DOODLE_SOURCES: Record<DoodleName, string> = {
    alerts: '/doodles/alerts.png',
    chat: '/doodles/chat.png',
    dashboard: '/doodles/dashboard.png',
    'hdd-drive': '/doodles/hdd-drive.png',
    legal: '/doodles/legal.png',
    network: '/doodles/network.png',
    settings: '/doodles/settings.png',
    threat: '/doodles/threat.png',
    'usb-drive': '/doodles/usb-drive.png',
}

const SIZE_CLASSES = {
    sm: 'h-10 w-10',
    md: 'h-14 w-14',
    lg: 'h-16 w-16',
    xl: 'h-20 w-20',
} as const

interface DoodleIconProps {
    name: DoodleName
    alt: string
    size?: keyof typeof SIZE_CLASSES
    className?: string
    imageClassName?: string
}

export type { DoodleName }

export default function DoodleIcon({
    name,
    alt,
    size = 'md',
    className = '',
    imageClassName = '',
}: DoodleIconProps) {
    return (
        <div
            className={[
                'doodle-badge',
                SIZE_CLASSES[size],
                className,
            ].join(' ')}
        >
            <img
                src={DOODLE_SOURCES[name]}
                alt={alt}
                className={[
                    'h-full w-full object-contain p-1.5',
                    imageClassName,
                ].join(' ')}
                draggable={false}
            />
        </div>
    )
}
