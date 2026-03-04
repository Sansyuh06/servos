import { Routes, Route, useLocation, Navigate } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import { useAuthStore } from '@/store/authStore'
import LoginPage from '@/pages/LoginPage'
import DashboardPage from '@/pages/DashboardPage'
import InvestigatePage from '@/pages/InvestigatePage'
import WorkspacePage from '@/pages/WorkspacePage'
import ReportPage from '@/pages/ReportPage'
import SettingsPage from '@/pages/SettingsPage'
import ChatPage from '@/pages/ChatPage'
import AppShell from '@/components/AppShell'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
    const isAuth = useAuthStore((s) => s.isAuthenticated)
    if(!isAuth) return <Navigate to="/login" replace />
    return <>{children}</>
}

export default function App() {
    const location = useLocation()
    const isAuth = useAuthStore((s) => s.isAuthenticated)

    return (
        <AnimatePresence mode="wait">
            <Routes location={location} key={location.pathname}>
                <Route path="/login" element={<LoginPage />} />
                <Route
                    path="/*"
                    element={
                        <ProtectedRoute>
                            <AppShell>
                                <Routes>
                                    <Route index element={<ChatPage />} />
                                    <Route path="dashboard" element={<DashboardPage />} />
                                    <Route path="investigate" element={<InvestigatePage />} />
                                    <Route path="workspace/:caseId" element={<WorkspacePage />} />
                                    <Route path="report/:caseId" element={<ReportPage />} />
                                    <Route path="settings" element={<SettingsPage />} />
                                </Routes>
                            </AppShell>
                        </ProtectedRoute>
                    }
                />
            </Routes>
        </AnimatePresence>
    )
}
