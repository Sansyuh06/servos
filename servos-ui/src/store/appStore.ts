import { create } from 'zustand'
import { Device, CaseSummary, getDevices, getCases, getAlerts, AlertItem } from '@/api/client'

interface AppState {
    /* Devices */
    devices: Device[]
    devicesLoading: boolean
    fetchDevices: () => Promise<void>

    /* Cases */
    cases: CaseSummary[]
    casesLoading: boolean
    fetchCases: () => Promise<void>

    /* Alerts */
    alerts: AlertItem[]
    alertsLoading: boolean
    fetchAlerts: () => Promise<void>

    /* Active investigation */
    activeCaseId: string | null
    setActiveCaseId: (id: string | null) => void

    /* Sidebar */
    currentPage: string
    setCurrentPage: (page: string) => void
}

export const useAppStore = create<AppState>((set) => ({
    devices: [],
    devicesLoading: false,
    fetchDevices: async () => {
        set({ devicesLoading: true })
        try {
            const res = await getDevices()
            set({ devices: res.devices, devicesLoading: false })
        } catch {
            set({ devicesLoading: false })
        }
    },

    cases: [],
    casesLoading: false,
    fetchCases: async () => {
        set({ casesLoading: true })
        try {
            const res = await getCases()
            set({ cases: res.cases, casesLoading: false })
        } catch {
            set({ casesLoading: false })
        }
    },
    alerts: [],
    alertsLoading: false,
    fetchAlerts: async () => {
        set({ alertsLoading: true })
        try {
            const res = await getAlerts()
            set({ alerts: res.alerts, alertsLoading: false })
        } catch {
            set({ alertsLoading: false })
        }
    },

    activeCaseId: null,
    setActiveCaseId: (id) => set({ activeCaseId: id }),

    currentPage: 'dashboard',
    setCurrentPage: (page) => set({ currentPage: page }),
}))
