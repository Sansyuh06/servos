import { useEffect, useState } from 'react'
import { getSettings, updateSettings, getLLMStatus } from '@/api/client'
import PageTransition from '@/components/PageTransition'
import { Settings, Cpu, FolderOpen, Shield, Save } from 'lucide-react'

export default function SettingsPage() {
    const [settings, setSettings] = useState<Record<string, any>>({})
    const [llm, setLlm] = useState<{ available: boolean; model: string; base_url: string } | null>(null)
    const [saving, setSaving] = useState(false)

    useEffect(() => {
        getSettings().then((r) => setSettings(r.settings)).catch(() => { })
        getLLMStatus().then((r) => setLlm(r)).catch(() => { })
    }, [])

    const handleSave = async () => {
        setSaving(true)
        try { await updateSettings(settings) } catch { }
        setSaving(false)
    }

    return (
        <PageTransition>
            <div className="h-full overflow-y-auto p-6 max-w-2xl">
                <h1 className="text-xl font-bold text-cream-bright mb-6 flex items-center gap-2">
                    <Settings size={20} className="text-accent" /> Settings
                </h1>

                <div className="space-y-4">
                    {/* LLM Status */}
                    <div className="bg-servos-surface border border-servos-border rounded-lg p-4">
                        <div className="flex items-center gap-2 mb-3">
                            <Cpu size={14} className="text-accent" />
                            <h3 className="text-sm font-semibold text-cream">AI / LLM Configuration</h3>
                        </div>
                        {llm ? (
                            <div className="space-y-2 text-xs">
                                <div className="flex justify-between">
                                    <span className="text-cream-dim">Status</span>
                                    <span className={llm.available ? 'text-success' : 'text-danger'}>
                                        {llm.available ? '● Connected' : '● Disconnected'}
                                    </span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-cream-dim">Model</span>
                                    <span className="text-cream font-mono">{llm.model}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-cream-dim">Endpoint</span>
                                    <span className="text-cream font-mono text-[10px]">{llm.base_url}</span>
                                </div>
                            </div>
                        ) : (
                            <p className="text-xs text-cream-dim">Checking LLM status...</p>
                        )}
                    </div>

                    {/* Data Directories */}
                    <div className="bg-servos-surface border border-servos-border rounded-lg p-4">
                        <div className="flex items-center gap-2 mb-3">
                            <FolderOpen size={14} className="text-accent" />
                            <h3 className="text-sm font-semibold text-cream">Data Directories</h3>
                        </div>
                        <div className="space-y-3">
                            {['data_dir', 'backup_dir', 'reports_dir'].map((k) => (
                                <div key={k}>
                                    <label className="block text-[10px] font-semibold text-cream-dim uppercase tracking-wider mb-1">
                                        {k.replace(/_/g, ' ')}
                                    </label>
                                    <input
                                        type="text"
                                        value={settings[k] || ''}
                                        onChange={(e) => setSettings({ ...settings, [k]: e.target.value })}
                                        className="w-full bg-servos-bg border border-servos-border rounded-lg py-2 px-3 text-xs text-cream font-mono focus:border-accent focus:outline-none"
                                    />
                                </div>
                            ))}
                        </div>
                    </div>
                    {/* Automation */}
                    <div className="bg-servos-surface border border-servos-border rounded-lg p-4">
                        <div className="flex items-center gap-2 mb-3">
                            <Cpu size={14} className="text-accent" />
                            <h3 className="text-sm font-semibold text-cream">Automation</h3>
                        </div>
                        <div className="space-y-2 text-xs">
                            <label className="flex items-center gap-2">
                                <input
                                    type="checkbox"
                                    checked={!!settings.auto_investigate}
                                    onChange={e => setSettings({...settings, auto_investigate: e.target.checked})}
                                    className="accent-accent"
                                />
                                Automatically investigate new devices
                            </label>
                            <div>
                                <label className="block text-[10px] font-semibold text-cream-dim uppercase tracking-wider mb-1">
                                    USB poll interval (sec)
                                </label>
                                <input
                                    type="number"
                                    step="0.5"
                                    value={settings.usb_poll_interval || 2}
                                    onChange={e => setSettings({...settings, usb_poll_interval: parseFloat(e.target.value)})}
                                    className="w-24 bg-servos-bg border border-servos-border rounded-lg py-1 px-2 text-xs text-cream font-mono focus:border-accent focus:outline-none"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Security */}
                    <div className="bg-servos-surface border border-servos-border rounded-lg p-4">
                        <div className="flex items-center gap-2 mb-3">
                            <Shield size={14} className="text-accent" />
                            <h3 className="text-sm font-semibold text-cream">Security</h3>
                        </div>
                        <p className="text-[11px] text-cream-dim leading-relaxed">
                            All forensic data is stored locally. No network connections are established.
                            Evidence integrity is preserved via SHA-256 hashing. Audit logs are immutable.
                        </p>
                    </div>

                    {/* Save */}
                    <button
                        onClick={handleSave}
                        className="flex items-center gap-2 px-4 py-2 bg-accent hover:bg-accent-dark text-white text-sm font-semibold rounded-lg transition-colors"
                    >
                        <Save size={14} />
                        {saving ? 'Saving...' : 'Save Settings'}
                    </button>
                </div>
            </div>
        </PageTransition>
    )
}
