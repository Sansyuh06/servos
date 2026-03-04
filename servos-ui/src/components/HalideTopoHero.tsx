import React from 'react'
import { motion } from 'framer-motion'

/**
 * HalideTopoHero component replicates the 21st.dev halide topo hero design.
 * Animated topographic contour lines with colour shifting. Intended as a
 * dark cypherpunk dashboard header. Props allow overlay text and status badges.
 */
interface Props {
    title?: string
    subtitle?: string
    statusBadge?: React.ReactNode
    /** pulseRed indicates alert state e.g. when BadUSB is detected */
    pulseRed?: boolean
}

export default function HalideTopoHero({ title = 'SERVOS', subtitle = '', statusBadge, pulseRed = false }: Props) {
    return (
        <div className="relative w-full h-64 overflow-hidden bg-servos-dark">
            {/* animated svg or canvas backgrounds could be implemented here */}
            <motion.div
                className="absolute inset-0"
                animate={{ opacity: pulseRed ? [0.8, 1, 0.8] : 1 }}
                transition={{ duration: pulseRed ? 1.5 : 0 }}
                style={{ background: 'radial-gradient(circle at center, #005f73 0%, #030712 100%)' }}
            />
            <div className="relative z-10 flex flex-col items-center justify-center h-full px-8 text-center">
                <h1 className="text-4xl font-extrabold tracking-tight text-cream-bright">{title}</h1>
                {subtitle && <p className="mt-2 text-sm text-cream-dim">{subtitle}</p>}
                {statusBadge && <div className="mt-4">{statusBadge}</div>}
            </div>
        </div>
    )
}
