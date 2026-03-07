import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import LoginPage from '@/pages/LoginPage'
import DashboardPage from '@/pages/DashboardPage'
import NetworkScanPage from '@/pages/NetworkScanPage'
import MalwareDeepPage from '@/pages/MalwareDeepPage'
import SettingsPage from '@/pages/SettingsPage'
import ChatPage from '@/pages/ChatPage'
import AlertsPage from '@/pages/AlertsPage'
import AppShell from '@/components/AppShell'
import LegalPage from '@/pages/LegalPage'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
    const isAuth = useAuthStore((s) => s.isAuthenticated)
    if (!isAuth) return <Navigate to="/login" replace />
    return <>{children}</>
}

export default function App() {
    return (
        <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route
                path="/*"
                element={
                    <ProtectedRoute>
                        <AppShell>
                            <Routes>
                                <Route index element={<ChatPage />} />
                                <Route path="chat" element={<ChatPage />} />
                                <Route path="dashboard" element={<DashboardPage />} />
                                <Route path="network" element={<NetworkScanPage />} />
                                <Route path="deep" element={<MalwareDeepPage />} />
                                <Route path="legal" element={<LegalPage />} />
                                <Route path="alerts" element={<AlertsPage />} />
                                <Route path="settings" element={<SettingsPage />} />
                            </Routes>
                        </AppShell>
                    </ProtectedRoute>
                }
            />
        </Routes>
    )
}
