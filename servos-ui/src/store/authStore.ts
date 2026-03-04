import { create } from 'zustand'

interface AuthState {
    isAuthenticated: boolean
    username: string
    role: string // 'investigator' | 'admin' | 'analyst'
    failedAttempts: number
    isLocked: boolean
    lockUntil: number | null
    login: (username: string, password: string) => Promise<void>
    register: (username: string, password: string) => Promise<void>
    loginWithGoogle: (accessToken: string) => Promise<void>
    logout: () => void
    recordFailedAttempt: () => void
    resetAttempts: () => void
}

export const useAuthStore = create<AuthState>((set, get) => ({
    isAuthenticated: false,
    username: '',
    role: '',
    failedAttempts: 0,
    isLocked: false,
    lockUntil: null,

    login: async (username, password) => {
        const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password, role: 'investigator' })
        })
        if(!res.ok) {
            get().recordFailedAttempt()
            throw new Error('Invalid username or password')
        }
        const data = await res.json()
        set({ isAuthenticated: true, username: data.username, role: data.role, failedAttempts: 0, isLocked: false, lockUntil: null })
        sessionStorage.setItem('servos_session', JSON.stringify({ username: data.username, role: data.role, ts: Date.now() }))
    },

    register: async (username, password) => {
        const res = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password, role: 'investigator' })
        })
        if(!res.ok) {
            const errData = await res.json()
            throw new Error(errData.detail || 'Username already taken')
        }
        const data = await res.json()
        set({ isAuthenticated: true, username: data.username, role: data.role, failedAttempts: 0, isLocked: false, lockUntil: null })
        sessionStorage.setItem('servos_session', JSON.stringify({ username: data.username, role: data.role, ts: Date.now() }))
    },

    loginWithGoogle: async (accessToken: string) => {
        const res = await fetch('/api/auth/google', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: accessToken })
        })
        if(!res.ok) throw new Error('Google Auth failed')
        const data = await res.json()
        set({ isAuthenticated: true, username: data.username, role: data.role, failedAttempts: 0, isLocked: false, lockUntil: null })
        sessionStorage.setItem('servos_session', JSON.stringify({ username: data.username, role: data.role, ts: Date.now() }))
    },

    logout: () => {
        set({ isAuthenticated: false, username: '', role: '' })
        sessionStorage.removeItem('servos_session')
    },

    recordFailedAttempt: () => {
        const attempts = get().failedAttempts + 1
        const locked = attempts >= 5
        set({
            failedAttempts: attempts,
            isLocked: locked,
            lockUntil: locked ? Date.now() + 60_000 : null,
        })
    },

    resetAttempts: () => set({ failedAttempts: 0, isLocked: false, lockUntil: null }),
}))

// Restore session on load
const saved = sessionStorage.getItem('servos_session')
if(saved) {
    try {
        const { username, role } = JSON.parse(saved)
        useAuthStore.setState({ isAuthenticated: true, username, role })
    } catch { }
}
