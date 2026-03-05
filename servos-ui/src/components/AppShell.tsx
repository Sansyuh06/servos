import { useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import {
    LayoutDashboard, Search, FolderOpen, FileText,
    Settings, LogOut, Shield, Wifi, WifiOff, Sparkles, Cpu, Bell, Wrench
} from 'lucide-react'

const NAV_ITEMS = [
    { id: '/', label: 'AI Chat', icon: Sparkles },
    { id: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: '/investigate', label: 'Investigate', icon: Search },
    { id: '/network', label: 'Network Scan', icon: Wifi },
    { id: '/memory', label: 'Memory', icon: Cpu },
    { id: '/logs', label: 'Logs', icon: FileText },
    { id: '/registry', label: 'Registry', icon: FolderOpen },
    { id: '/deep', label: 'Malware Deep', icon: Shield },
    { id: '/orchestrator', label: 'Multi Scan', icon: Wrench },
    { id: '/alerts', label: 'Alerts', icon: Bell },
    { id: '/settings', label: 'Settings', icon: Settings },
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
                    <div className="flex items-center gap-2.5">
                        <Shield size={20} className="text-accent" />
                        <span className="text-base font-bold tracking-wide text-cream-bright font-heading">SERVOS</span>
                    </div>
                    <p className="text-[11px] text-cream-dim mt-1 tracking-wide">AI Assistant Platform</p>
                </div>

                {/* Nav links */}
                <nav className="flex-1 px-3 py-4 space-y-1">
                    {NAV_ITEMS.map(({ id, label, icon: Icon }) => {
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
                                <Icon size={16} />
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
