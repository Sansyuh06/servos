import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useAuthStore } from '@/store/authStore'
import { useGoogleLogin } from '@react-oauth/google'
import { AtSign, Lock, ChevronRight, AlertTriangle, Shield } from 'lucide-react'

/* ─────────────────────────────────────────────
   Floating SVG Elements — Servos design system
   Uses real generated artwork for face/hand and polyhedron,
   SVG sparkles and blobs for geometric accents
   ───────────────────────────────────────────── */

/** 4-point sparkle star */
function Sparkle({ x, y, size = 24, delay = 0, duration = 5 }: { x: number; y: number; size?: number; delay?: number; duration?: number }) {
    return (
        <motion.svg
            viewBox="0 0 24 24"
            width={size}
            height={size}
            style={{ position: 'absolute', left: `${x}%`, top: `${y}%`, zIndex: 10 }}
            initial={{ opacity: 0, scale: 0 }}
            animate={{
                opacity: [0, 0.9, 0.6, 0.9, 0],
                scale: [0.5, 1, 0.85, 1, 0.5],
                rotate: [0, 15, -10, 5, 0],
                y: [0, -8, 4, -6, 0],
            }}
            transition={{ duration, delay, repeat: Infinity, ease: 'easeInOut' }}
        >
            <path
                d="M12 0 L14 10 L24 12 L14 14 L12 24 L10 14 L0 12 L10 10 Z"
                fill="#8F7DBA"
                fillOpacity={0.85}
            />
        </motion.svg>
    )
}

/** Small 4-point mini sparkle */
function MiniSparkle({ x, y, size = 14, delay = 0 }: { x: number; y: number; size?: number; delay?: number }) {
    return (
        <motion.svg
            viewBox="0 0 24 24"
            width={size}
            height={size}
            style={{ position: 'absolute', left: `${x}%`, top: `${y}%`, zIndex: 10 }}
            initial={{ opacity: 0 }}
            animate={{
                opacity: [0, 0.7, 0.4, 0.7, 0],
                scale: [0.6, 1.1, 0.8, 1, 0.6],
                rotate: [0, 30, -20, 10, 0],
            }}
            transition={{ duration: 4, delay, repeat: Infinity, ease: 'easeInOut' }}
        >
            <path
                d="M12 0 L14 10 L24 12 L14 14 L12 24 L10 14 L0 12 L10 10 Z"
                fill="#A794CC"
                fillOpacity={0.6}
            />
        </motion.svg>
    )
}

/** Organic background blobs */
function BackgroundBlobs() {
    return (
        <svg className="absolute inset-0 w-full h-full" viewBox="0 0 800 900" preserveAspectRatio="none">
            {/* Large blob — top right */}
            <motion.path
                d="M500 50 Q650 -20, 750 80 Q850 180, 780 320 Q720 420, 600 380 Q480 340, 450 220 Q420 100, 500 50Z"
                fill="#2A2C33"
                initial={{ opacity: 0 }}
                animate={{ opacity: [0.4, 0.6, 0.4], scale: [1, 1.02, 1] }}
                transition={{ duration: 16, repeat: Infinity, ease: 'easeInOut' }}
            />
            {/* Medium blob — center left */}
            <motion.path
                d="M50 350 Q-30 280, 30 200 Q100 120, 200 170 Q300 220, 280 340 Q260 450, 150 470 Q40 480, 50 350Z"
                fill="#33353D"
                initial={{ opacity: 0 }}
                animate={{ opacity: [0.3, 0.5, 0.3], scale: [1, 1.03, 0.98, 1] }}
                transition={{ duration: 20, delay: 2, repeat: Infinity, ease: 'easeInOut' }}
            />
            {/* Small blob — bottom right */}
            <motion.path
                d="M550 650 Q630 600, 720 640 Q810 680, 780 770 Q750 860, 650 840 Q540 820, 500 740 Q460 660, 550 650Z"
                fill="#2A2C33"
                initial={{ opacity: 0 }}
                animate={{ opacity: [0.25, 0.4, 0.25] }}
                transition={{ duration: 18, delay: 4, repeat: Infinity, ease: 'easeInOut' }}
            />
            {/* Accent blob — top area with purple tint */}
            <motion.path
                d="M250 -40 Q380 -60, 420 30 Q460 120, 380 180 Q300 240, 210 180 Q120 120, 160 40 Q200 -20, 250 -40Z"
                fill="rgba(143, 125, 186, 0.06)"
                initial={{ opacity: 0 }}
                animate={{ opacity: [0.06, 0.12, 0.06] }}
                transition={{ duration: 22, delay: 1, repeat: Infinity, ease: 'easeInOut' }}
            />
            {/* Wispy outline blob — bottom left */}
            <motion.path
                d="M30 700 Q-40 620, 60 560 Q160 500, 260 560 Q360 620, 300 720 Q240 830, 120 810 Q0 790, 30 700Z"
                fill="none"
                stroke="#3E4149"
                strokeWidth="1.2"
                initial={{ opacity: 0 }}
                animate={{ opacity: [0.2, 0.35, 0.2] }}
                transition={{ duration: 24, delay: 3, repeat: Infinity, ease: 'easeInOut' }}
            />
            {/* Extra wispy blob — mid */}
            <motion.path
                d="M350 400 Q420 350, 500 390 Q580 430, 550 510 Q520 590, 430 570 Q340 550, 320 470 Q300 390, 350 400Z"
                fill="none"
                stroke="#33353D"
                strokeWidth="0.8"
                initial={{ opacity: 0 }}
                animate={{ opacity: [0.15, 0.28, 0.15] }}
                transition={{ duration: 26, delay: 5, repeat: Infinity, ease: 'easeInOut' }}
            />
        </svg>
    )
}

/** Small floating particle dots for ambient feel */
function AmbientParticles() {
    const particles = [
        { x: 12, y: 25, size: 2.5, dur: 7, del: 0 },
        { x: 78, y: 15, size: 2, dur: 9, del: 1 },
        { x: 45, y: 70, size: 3, dur: 8, del: 2 },
        { x: 88, y: 55, size: 2, dur: 6, del: 3 },
        { x: 22, y: 85, size: 2.5, dur: 10, del: 1.5 },
        { x: 65, y: 42, size: 1.5, dur: 7, del: 4 },
        { x: 35, y: 55, size: 2, dur: 11, del: 2.5 },
        { x: 92, y: 80, size: 3, dur: 8, del: 0.5 },
    ]

    return (
        <>
            {particles.map((p, i) => (
                <motion.div
                    key={i}
                    className="absolute rounded-full"
                    style={{
                        left: `${p.x}%`,
                        top: `${p.y}%`,
                        width: p.size,
                        height: p.size,
                        background: 'rgba(143, 125, 186, 0.35)',
                    }}
                    animate={{
                        opacity: [0, 0.5, 0],
                        y: [0, -15, 0],
                    }}
                    transition={{ duration: p.dur, delay: p.del, repeat: Infinity, ease: 'easeInOut' }}
                />
            ))}
        </>
    )
}


/**
 * Premium Login Page — Split-screen with floating presentation elements
 * Left: Real artwork images (face/hand sketch, polyhedron) + SVG sparkles/blobs
 * Right: Clean auth form with role selector
 */
export default function LoginPage() {
    const navigate = useNavigate()
    const { login, register, loginWithGoogle, failedAttempts, isLocked, lockUntil } = useAuthStore()
    const [isSignup, setIsSignup] = useState(false)
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')
    const [isLoading, setIsLoading] = useState(false)

    const googleLogin = useGoogleLogin({
        onSuccess: async (tokenResponse) => {
            setIsLoading(true)
            setError('')
            try {
                // In a production app, we would send `tokenResponse.access_token` or `code`
                // to the FastAPI backend to be verified by Google's servers.
                // For this demo, we can just trigger the backend's dummy Google login
                // since the user *did* actually just authenticate with Google successfully on the frontend!
                await loginWithGoogle(tokenResponse.access_token)
                navigate('/')
            } catch(err: any) {
                setError(err.message || 'Google Auth failed')
            } finally {
                setIsLoading(false)
            }
        },
        onError: () => {
            setError('Google login failed or was cancelled.')
        }
    })

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
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
        } catch(err: any) {
            setError(err.message || 'Authentication failed')
        } finally {
            setIsLoading(false)
        }
    }

    const lockRemaining = lockUntil ? Math.max(0, Math.ceil((lockUntil - Date.now()) / 1000)) : 0

    return (
        <div className="flex h-screen w-screen bg-[#1E1F24] overflow-hidden">
            {/* ── Left Panel: Floating Artwork + Decorative Elements ── */}
            <div className="hidden lg:flex lg:w-1/2 relative flex-col justify-between p-8 overflow-hidden">
                {/* Organic blob background */}
                <BackgroundBlobs />

                {/* Ambient floating particles */}
                <AmbientParticles />

                {/* Sparkle stars — scattered */}
                <Sparkle x={42} y={8} size={32} delay={0.5} duration={6} />
                <Sparkle x={50} y={13} size={22} delay={1.2} duration={5} />
                <MiniSparkle x={36} y={5} size={14} delay={2} />
                <MiniSparkle x={55} y={18} size={11} delay={0.8} />
                <MiniSparkle x={15} y={30} size={14} delay={3} />
                <MiniSparkle x={80} y={24} size={12} delay={1.5} />
                <MiniSparkle x={88} y={68} size={13} delay={2.2} />
                <MiniSparkle x={25} y={65} size={10} delay={3.5} />

                {/* ── Real artwork: Face + Hand sketch ── */}
                <motion.div
                    className="absolute"
                    style={{
                        right: '0%',
                        top: '5%',
                        width: '85%',
                        height: '85%',
                        zIndex: 5,
                    }}
                    initial={{ opacity: 0 }}
                    animate={{
                        opacity: 0.85,
                        y: [0, -14, 8, -6, 0],
                    }}
                    transition={{
                        opacity: { duration: 1.5, delay: 0.3 },
                        y: { duration: 12, repeat: Infinity, ease: 'easeInOut' },
                    }}
                >
                    <img
                        src="/images/face-hand.png"
                        alt=""
                        className="w-full h-full object-contain pointer-events-none select-none"
                        style={{
                            filter: 'brightness(1.1) contrast(1.05)',
                            opacity: 0.9,
                        }}
                        draggable={false}
                    />
                </motion.div>

                {/* ── Servos logo floating above the hand ── */}
                <motion.div
                    className="absolute"
                    style={{
                        right: '0%',
                        top: '5%',
                        width: '70%',
                        height: '70%',
                        zIndex: 8,
                    }}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{
                        opacity: [0.85, 1, 0.85],
                        y: [0, -14, 6, -10, 0],
                        rotate: [0, 2, -1.5, 1, 0],
                    }}
                    transition={{
                        opacity: { duration: 4, delay: 0.8, repeat: Infinity, ease: 'easeInOut' },
                        y: { duration: 10, repeat: Infinity, ease: 'easeInOut' },
                        rotate: { duration: 14, repeat: Infinity, ease: 'easeInOut' },
                    }}
                >
                    <img
                        src="/images/servos-logo.png"
                        alt=""
                        className="w-full h-full object-contain pointer-events-none select-none drop-shadow-[0_0_25px_rgba(143,125,186,0.4)]"
                        draggable={false}
                    />
                </motion.div>

                {/* Logo — top left, anchored */}
                <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6 }}
                    className="relative z-20 flex items-center gap-4"
                >
                    <img
                        src="/images/servos-logo.png"
                        alt="Servos"
                        className="h-16 w-auto object-contain pointer-events-none select-none"
                        draggable={false}
                    />
                    <span className="text-3xl font-bold text-cream tracking-tight font-heading">SERVOS</span>
                </motion.div>

                {/* Testimonial — bottom left, anchored */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.5 }}
                    className="relative z-20 max-w-sm"
                >
                    <p className="text-[15px] text-cream/70 leading-relaxed font-light">
                        "Servos has transformed our forensic workflow. Evidence integrity preserved,
                        chain-of-custody automated, and investigations completed in a fraction of the time."
                    </p>
                    <p className="text-[13px] text-accent-light/60 mt-3">~ Digital Forensics Division</p>
                </motion.div>
            </div>

            {/* ── Right Panel: Auth Form ── */}
            <div className="w-full lg:w-1/2 flex flex-col justify-center px-8 md:px-16 lg:px-20 bg-[#1A1B20]">
                <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.5, delay: 0.2 }}
                    className="max-w-md w-full mx-auto"
                >
                    {/* Card container with subtle border */}
                    <div className="border border-servos-border/40 rounded-2xl p-8 bg-[#16171B]/60">

                        <form onSubmit={handleSubmit} className="space-y-5">
                            {/* Email */}
                            <div>
                                <label className="block text-sm font-semibold text-cream mb-2">Email</label>
                                <div className="relative">
                                    <AtSign size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-cream-dim/40" />
                                    <input
                                        type="text"
                                        value={username}
                                        onChange={(e) => { setUsername(e.target.value); setError('') }}
                                        placeholder="Enter your email"
                                        autoFocus
                                        className="w-full bg-servos-bg border border-servos-border rounded-lg py-3 pl-10 pr-4 text-sm text-cream placeholder:text-cream-dim/30 focus:border-accent/60 focus:outline-none focus:ring-1 focus:ring-accent/30 transition-colors"
                                    />
                                </div>
                            </div>

                            {/* Password */}
                            <div>
                                <label className="block text-sm font-semibold text-cream mb-2">Password</label>
                                <div className="relative">
                                    <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-cream-dim/40" />
                                    <input
                                        type="password"
                                        value={password}
                                        onChange={(e) => { setPassword(e.target.value); setError('') }}
                                        placeholder="Enter your password"
                                        className="w-full bg-servos-bg border border-servos-border rounded-lg py-3 pl-10 pr-4 text-sm text-cream placeholder:text-cream-dim/30 focus:border-accent/60 focus:outline-none focus:ring-1 focus:ring-accent/30 transition-colors"
                                    />
                                </div>
                            </div>

                            {/* Remember me + Forgot password */}
                            <div className="flex items-center justify-between">
                                <label className="flex items-center gap-2 cursor-pointer group">
                                    <input
                                        type="checkbox"
                                        className="w-4 h-4 rounded border-servos-border bg-servos-bg text-accent focus:ring-accent/30 focus:ring-offset-0 cursor-pointer accent-[#8F7DBA]"
                                    />
                                    <span className="text-sm text-cream-dim group-hover:text-cream transition-colors">Remember me</span>
                                </label>
                                <button
                                    type="button"
                                    className="text-sm text-accent-light hover:text-accent transition-colors"
                                >
                                    Forgot password?
                                </button>
                            </div>

                            {/* Error */}
                            {error && (
                                <motion.div
                                    initial={{ opacity: 0, y: -4 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="flex items-center gap-2 px-3 py-2 bg-danger/10 border border-danger/20 rounded-lg"
                                >
                                    <AlertTriangle size={12} className="text-danger" />
                                    <span className="text-[12px] text-danger">{error}</span>
                                </motion.div>
                            )}

                            {/* Lockout warning */}
                            {isLocked && lockRemaining > 0 && (
                                <div className="flex items-center gap-2 px-3 py-2 bg-warning/10 border border-warning/20 rounded-lg">
                                    <AlertTriangle size={12} className="text-warning" />
                                    <span className="text-[12px] text-warning">Account locked. Retry in {lockRemaining}s</span>
                                </div>
                            )}

                            {/* Sign In / Sign Up button */}
                            <button
                                type="submit"
                                disabled={isLocked && lockRemaining > 0 || isLoading}
                                className="w-full py-3 rounded-lg bg-cream hover:bg-cream-bright text-[#1A1B20] text-sm font-bold transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-accent/10 flex items-center justify-center gap-2"
                            >
                                {isLoading ? (
                                    <span className="w-5 h-5 border-2 border-[#1A1B20]/20 border-t-[#1A1B20] rounded-full animate-spin" />
                                ) : isSignup ? (
                                    'Create Account'
                                ) : (
                                    'Sign In'
                                )}
                            </button>
                        </form>

                        {/* Divider */}
                        <div className="flex items-center gap-3 my-6">
                            <div className="flex-1 h-px bg-servos-border/50" />
                            <div className="text-[11px] text-cream-dim/50 uppercase tracking-wider px-2">OR</div>
                            <div className="flex-1 h-px bg-servos-border/50" />
                        </div>

                        {/* Social login buttons */}
                        <div className="space-y-3">
                            {/* Google */}
                            <button
                                type="button"
                                disabled={isLoading}
                                onClick={() => googleLogin()}
                                className="w-full flex items-center justify-center gap-4 py-3 rounded-xl bg-servos-bg border border-servos-border hover:bg-servos-surface hover:border-servos-hover transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                <svg width="24" height="24" viewBox="0 0 48 48">
                                    <path fill="#FFC107" d="M43.611 20.083H42V20H24v8h11.303c-1.649 4.657-6.08 8-11.303 8-6.627 0-12-5.373-12-12s5.373-12 12-12c3.059 0 5.842 1.154 7.961 3.039l5.657-5.657C34.046 6.053 29.268 4 24 4 12.955 4 4 12.955 4 24s8.955 20 20 20 20-8.955 20-20c0-1.341-.138-2.65-.389-3.917z" />
                                    <path fill="#FF3D00" d="M6.306 14.691l6.571 4.819C14.655 15.108 18.961 12 24 12c3.059 0 5.842 1.154 7.961 3.039l5.657-5.657C34.046 6.053 29.268 4 24 4 16.318 4 9.656 8.337 6.306 14.691z" />
                                    <path fill="#4CAF50" d="M24 44c5.166 0 9.86-1.977 13.409-5.192l-6.19-5.238A11.91 11.91 0 0124 36c-5.202 0-9.619-3.317-11.283-7.946l-6.522 5.025C9.505 39.556 16.227 44 24 44z" />
                                    <path fill="#1976D2" d="M43.611 20.083H42V20H24v8h11.303a12.04 12.04 0 01-4.087 5.571l.003-.002 6.19 5.238C36.971 39.205 44 34 44 24c0-1.341-.138-2.65-.389-3.917z" />
                                </svg>
                                <span className="text-[15px] font-medium text-cream">Continue with Google</span>
                            </button>
                        </div>

                        {/* Sign Up / Sign In link */}
                        <p className="text-center text-sm text-cream-dim mt-6">
                            {isSignup ? 'Already have an account?' : "Don't have an account?"}{' '}
                            <button
                                type="button"
                                onClick={() => { setIsSignup(!isSignup); setError(''); }}
                                className="text-accent-light hover:text-accent font-semibold transition-colors"
                            >
                                {isSignup ? 'Sign In' : 'Sign Up'}
                            </button>
                        </p>

                    </div>

                    {/* Footer */}
                    <p className="text-[11px] text-cream-dim/40 mt-4 leading-relaxed text-center">
                        By signing in, you acknowledge that all forensic activities are logged
                        and evidence integrity is preserved per chain-of-custody requirements.
                    </p>
                </motion.div>
            </div>
        </div>
    )
}
