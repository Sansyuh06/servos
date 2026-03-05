import { useEffect } from 'react'
import { useAppStore } from '@/store/appStore'
import PageTransition from '@/components/PageTransition'
import { Bell, Clock } from 'lucide-react'

export default function AlertsPage() {
    const { alerts, alertsLoading, fetchAlerts } = useAppStore()

    useEffect(() => {
        fetchAlerts()
        const iv = setInterval(fetchAlerts, 5000)
        return () => clearInterval(iv)
    }, [])

    return (
        <PageTransition>
            <div className="h-full overflow-y-auto p-6">
                <h2 className="text-lg font-semibold text-cream-bright mb-4">System Alerts</h2>
                {alertsLoading ? (
                    <div className="text-sm text-cream-dim">Loading alerts...</div>
                ) : alerts.length === 0 ? (
                    <div className="text-sm text-cream-dim">No alerts</div>
                ) : (
                    <div className="space-y-2">
                        {alerts.map((a, idx) => (
                            <div key={idx} className="bg-servos-surface border border-servos-border rounded-lg p-3">
                                <div className="flex items-center justify-between mb-1">
                                    <div className="flex items-center gap-2">
                                        <Bell size={16} className="text-accent" />
                                        <span className="text-sm font-medium text-cream-bright capitalize">{a.event_type.replace(/_/g, ' ').toLowerCase()}</span>
                                    </div>
                                    <span className="text-[10px] text-cream-dim flex items-center gap-1">
                                        <Clock size={10} />{new Date(a.timestamp).toLocaleTimeString()}
                                    </span>
                                </div>
                                <p className="text-xs text-cream-dim mb-1">Risk: <span className="font-semibold">{a.risk}</span></p>
                                <p className="text-xs text-cream">{a.message}</p>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </PageTransition>
    )
}
