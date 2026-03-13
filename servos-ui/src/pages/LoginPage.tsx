import { useState } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import DoodleIcon from '@/components/DoodleIcon'
import { useAuthStore } from '@/store/authStore'

const INPUT_CLASS =
    'mt-2 w-full rounded-[18px] border border-white/10 bg-servos-surface px-4 py-3 text-sm text-cream-bright outline-none transition-colors focus:border-accent/40 placeholder:text-cream-dim'

const DOODLE_FEATURES = [
    {
        name: 'Device triage',
        doodle: 'usb-drive',
        description: 'Spot attached evidence quickly and launch clean investigations.',
    },
    {
        name: 'Threat review',
        doodle: 'threat',
        description: 'Bring suspicious findings to the surface with a friendlier visual system.',
    },
    {
        name: 'Network traces',
        doodle: 'network',
        description: 'Keep volatile activity visible while staying entirely local-first.',
    },
    {
        name: 'Evidence notes',
        doodle: 'legal',
        description: 'Move from raw artifacts to report-ready summaries with less friction.',
    },
] as const

export default function LoginPage() {
    const navigate = useNavigate()
    const { failedAttempts, isLocked, lockUntil, login, register } = useAuthStore()
    const [isSignup, setIsSignup] = useState(false)
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')
    const [isLoading, setIsLoading] = useState(false)

    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault()
        if(isLocked && lockUntil && Date.now() < lockUntil) {
            setError(`Account locked. Try again in ${Math.ceil((lockUntil - Date.now()) / 1000)}s`)
            return
        }
        if(!username.trim() || !password) {
            setError('Email and password are required')
            return
        }

        setIsLoading(true)
        setError('')

        try {
            if(isSignup) {
                await register(username.trim(), password)
            } else {
                await login(username.trim(), password)
            }
            navigate('/')
        } catch(authError: any) {
            setError(authError.message || 'Authentication failed')
        } finally {
            setIsLoading(false)
        }
    }

    const lockRemaining = lockUntil ? Math.max(0, Math.ceil((lockUntil - Date.now()) / 1000)) : 0

    return (
        <div className="min-h-screen w-screen overflow-hidden bg-servos-bg text-cream">
            <div className="grid min-h-screen lg:grid-cols-[1.05fr_0.95fr]">
                <section className="hidden p-6 lg:block">
                    <div className="doodle-panel h-full p-8">
                        <div className="relative z-10 flex h-full flex-col justify-between">
                            <div>
                                <div className="flex items-center gap-4">
                                    <DoodleIcon name="dashboard" alt="SERVOS doodle" size="lg" />
                                    <div>
                                        <p className="text-[11px] uppercase tracking-[0.24em] text-cream-dim">
                                            SERVOS
                                        </p>
                                        <h1 className="mt-2 text-5xl font-black leading-[0.95] text-cream-bright font-heading">
                                            Hand-drawn forensics for serious casework.
                                        </h1>
                                    </div>
                                </div>

                                <p className="mt-6 max-w-2xl text-sm leading-7 text-cream-dim">
                                    The interface now leans into your custom gray-lavender palette with doodled evidence
                                    markers, softer panels, and a calmer production-ready feel for hackathon demos.
                                </p>
                            </div>

                            <div className="grid gap-4 md:grid-cols-2">
                                {DOODLE_FEATURES.map((feature) => (
                                    <motion.div
                                        key={feature.name}
                                        whileHover={{ y: -4 }}
                                        className="rounded-[26px] border border-white/10 bg-white/[0.04] p-5"
                                    >
                                        <DoodleIcon
                                            name={feature.doodle}
                                            alt={`${feature.name} doodle`}
                                            size="md"
                                        />
                                        <h2 className="mt-4 text-lg font-bold text-cream-bright">{feature.name}</h2>
                                        <p className="mt-2 text-sm leading-6 text-cream-dim">
                                            {feature.description}
                                        </p>
                                    </motion.div>
                                ))}
                            </div>

                            <div className="rounded-[24px] border border-white/10 bg-white/[0.04] p-5">
                                <p className="text-sm leading-7 text-cream-dim">
                                    "SERVOS now feels like a real product: calmer colors, clearer hierarchy, and a
                                    dashboard that looks intentional instead of improvised."
                                </p>
                                <p className="mt-3 text-[11px] uppercase tracking-[0.18em] text-accent-light">
                                    Digital Forensics Division
                                </p>
                            </div>
                        </div>
                    </div>
                </section>

                <section className="flex items-center justify-center p-6 md:p-10">
                    <motion.div
                        initial={{ opacity: 0, y: 18 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.45 }}
                        className="w-full max-w-lg"
                    >
                        <div className="doodle-panel p-8">
                            <div className="relative z-10">
                                <div className="flex items-center gap-4">
                                    <DoodleIcon name="chat" alt="Auth doodle" size="lg" />
                                    <div>
                                        <p className="text-[11px] uppercase tracking-[0.22em] text-cream-dim">
                                            Welcome back
                                        </p>
                                        <h2 className="mt-2 text-3xl font-black text-cream-bright font-heading">
                                            {isSignup ? 'Create your workspace' : 'Sign in to SERVOS'}
                                        </h2>
                                    </div>
                                </div>

                                <p className="mt-4 text-sm leading-7 text-cream-dim">
                                    {isSignup
                                        ? 'Set up your investigator profile to start local-first casework.'
                                        : 'Reconnect to your evidence workspace and resume the latest investigation.'}
                                </p>

                                {error && (
                                    <div className="mt-5 rounded-[20px] border border-danger/30 bg-danger-muted px-4 py-3 text-sm text-danger">
                                        {error}
                                    </div>
                                )}

                                {isLocked && lockRemaining > 0 && (
                                    <div className="mt-3 rounded-[20px] border border-warning/30 bg-warning-muted px-4 py-3 text-sm text-warning">
                                        Account locked. Retry in {lockRemaining}s.
                                    </div>
                                )}

                                <form onSubmit={handleSubmit} className="mt-6 space-y-5">
                                    <div>
                                        <label className="block text-[10px] font-semibold uppercase tracking-[0.18em] text-cream-dim">
                                            Username
                                        </label>
                                        <input
                                            type="text"
                                            value={username}
                                            onChange={(event) => {
                                                setUsername(event.target.value)
                                                setError('')
                                            }}
                                            placeholder="investigator@servos.local"
                                            autoFocus
                                            className={INPUT_CLASS}
                                        />
                                    </div>

                                    <div>
                                        <label className="block text-[10px] font-semibold uppercase tracking-[0.18em] text-cream-dim">
                                            Password
                                        </label>
                                        <input
                                            type="password"
                                            value={password}
                                            onChange={(event) => {
                                                setPassword(event.target.value)
                                                setError('')
                                            }}
                                            placeholder="Enter your password"
                                            className={INPUT_CLASS}
                                        />
                                    </div>

                                    <div className="flex items-center justify-between gap-3 text-sm">
                                        <label className="flex items-center gap-2 text-cream-dim">
                                            <input
                                                type="checkbox"
                                                className="h-4 w-4 accent-[#9c8ab9]"
                                            />
                                            Remember me
                                        </label>
                                        <span className="text-xs text-cream-dim">
                                            First time here? Create an offline account.
                                        </span>
                                    </div>

                                    <button
                                        type="submit"
                                        disabled={(isLocked && lockRemaining > 0) || isLoading}
                                        className="doodle-button doodle-button-primary w-full px-5 py-3 text-sm font-semibold disabled:opacity-40"
                                    >
                                        {isLoading ? 'Working...' : isSignup ? 'Create account' : 'Sign in'}
                                    </button>
                                </form>

                                <div className="mt-6 rounded-[22px] border border-white/10 bg-white/[0.04] p-4">
                                    <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-accent-light">
                                        Offline access
                                    </p>
                                    <p className="mt-2 text-sm leading-6 text-cream-dim">
                                        This build is fully local-first. Create an investigator account once, then sign in
                                        without any cloud identity provider.
                                    </p>
                                </div>

                                <p className="mt-6 text-center text-sm text-cream-dim">
                                    {isSignup ? 'Already have an account?' : "Don't have an account?"}{' '}
                                    <button
                                        type="button"
                                        onClick={() => {
                                            setIsSignup(!isSignup)
                                            setError('')
                                        }}
                                        className="font-semibold text-accent-light transition-colors hover:text-cream"
                                    >
                                        {isSignup ? 'Sign in' : 'Sign up'}
                                    </button>
                                </p>

                                <p className="mt-5 text-center text-[11px] leading-6 text-cream-dim">
                                    Failed attempts: {failedAttempts}. All forensic actions remain locally logged for
                                    chain-of-custody review.
                                </p>
                            </div>
                        </div>
                    </motion.div>
                </section>
            </div>
        </div>
    )
}
