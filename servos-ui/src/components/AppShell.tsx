import { useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import {
    Settings, LogOut
} from 'lucide-react'

const NAV_ITEMS = [
    { id: '/', label: 'AI Chat', icon: '/doodles/chat.png' },
    { id: '/dashboard', label: 'Dashboard', icon: '/doodles/dashboard.png' },
    { id: '/network', label: 'Network Scan', icon: '/doodles/network.png' },
    { id: '/deep', label: 'Threat Scan', icon: '/doodles/threat.png' },
    { id: '/legal', label: 'Legal & Procedure', icon: '/doodles/legal.png' },
    { id: '/alerts', label: 'Alerts', icon: '/doodles/alerts.png' },
    { id: '/settings', label: 'Settings', icon: '/doodles/settings.png' },
]

export default function AppShell({ children }: { children: React.ReactNode }) {
    const navigate = useNavigate()
    const location = useLocation()
    const { username, role, logout } = useAuthStore()

    const handleLogout = () => {
        logout()
        navigate('/login')
    }

    return (
        <div className="flex h-screen w-screen overflow-hidden">
            {/* ── Sidebar ── */}
            <aside className="w-56 flex flex-col bg-servos-surface border-r border-servos-border shrink-0">
                {/* Logo */}
                <div className="px-5 pt-6 pb-4 border-b border-servos-border-dim">
                    <div className="flex items-center gap-3">
                        <img src="/logo.png" alt="Servos Logo" className="h-[26px] w-auto drop-shadow-md" />
                        <span className="text-lg font-bold tracking-widest text-cream-bright font-heading uppercase drop-shadow-sm">SERVOS</span>
                    </div>
                    <p className="text-[11px] text-cream-dim mt-1 tracking-wide">AI Assistant Platform</p>
                </div>

                {/* Nav links */}
                <nav className="flex-1 px-3 py-4 space-y-1">
                    {NAV_ITEMS.map(({ id, label, icon }) => {
                        const isActive = location.pathname === id || (id !== '/' && location.pathname.startsWith(id))
                        return (
                            <button
                                key={id}
                                onClick={() => navigate(id)}
                                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors duration-150 ${isActive
                                    ? 'bg-accent-muted text-cream-bright border-l-2 border-accent'
                                    : 'text-cream-dim hover:bg-servos-hover hover:text-cream'
                                    }`}
                            >
                                <img
                                    src={icon}
                                    alt={`${label} icon`}
                                    className={`w-7 h-7 object-contain transition-all duration-200 ${isActive ? 'opacity-100 brightness-150 drop-shadow-[0_0_8px_rgba(255,255,255,0.6)] scale-105' : 'opacity-90 brightness-125 drop-shadow-[0_0_2px_rgba(255,255,255,0.2)] hover:opacity-100 hover:brightness-150'}`}
                                />
                                {label}
                            </button>
                        )
                    })}
                </nav>

                {/* Offline indicator */}
                <div className="px-4 py-3 border-t border-servos-border-dim">
                    <div className="flex items-center gap-2 text-[11px] text-success">
                        <span className="w-1.5 h-1.5 rounded-full bg-success animate-pulse" />
                        Offline Mode Active
                    </div>
                </div>

                {/* User + Logout */}
                <div className="px-4 py-3 border-t border-servos-border-dim">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-xs font-semibold text-cream">{username}</p>
                            <p className="text-[10px] text-cream-dim uppercase tracking-wider">{role}</p>
                        </div>
                        <button
                            onClick={handleLogout}
                            className="p-1.5 rounded-md hover:bg-servos-hover text-cream-dim hover:text-danger transition-colors"
                            title="Logout"
                        >
                            <LogOut size={14} />
                        </button>
                    </div>
                </div>
            </aside>

            {/* ── Main Content ── */}
            <main className="flex-1 overflow-y-auto bg-servos-bg">
                {children}
            </main>
        </div>
    )
}
