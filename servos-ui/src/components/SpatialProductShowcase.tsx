import React from 'react'
import { motion, useMotionValue, useTransform } from 'framer-motion'

/**
 * Simplified spatial showcase with parallax layers. Accepts metadata and findings.
 */
interface Props {
    caseNumber: string
    investigator: string
    deviceInfo: string
    criticalFindings: string[]
}

export default function SpatialProductShowcase({ caseNumber, investigator, deviceInfo, criticalFindings }: Props) {
    const x = useMotionValue(0)
    const y = useMotionValue(0)
    const bgX = useTransform(x, (v) => `${v * 0.02}px`)
    const bgY = useTransform(y, (v) => `${v * 0.02}px`)
    const fgX = useTransform(x, (v) => `${v * 0.08}px`)
    const fgY = useTransform(y, (v) => `${v * 0.08}px`)

    const onMouseMove = (e: React.MouseEvent) => {
        const rect = (e.currentTarget as HTMLElement).getBoundingClientRect()
        const cx = e.clientX - rect.left - rect.width / 2
        const cy = e.clientY - rect.top - rect.height / 2
        x.set(cx / rect.width)
        y.set(cy / rect.height)
    }

    return (
        <div
            className="relative w-full h-60 overflow-hidden bg-servos-dark rounded-lg"
            onMouseMove={onMouseMove}
        >
            <motion.div
                className="absolute inset-0"
                style={{ x: bgX, y: bgY, background: 'linear-gradient(135deg,#0f172a,#030712)' }}
            />
            <motion.div
                className="absolute inset-0"
                style={{ x: fgX, y: fgY }}
            >
                <div className="relative p-6 text-cream">
                    <h2 className="text-lg font-semibold">Case {caseNumber}</h2>
                    <p className="text-xs mt-1">Investigator: {investigator}</p>
                    <p className="text-xs">Device: {deviceInfo}</p>
                    <ul className="mt-2 space-y-1">
                        {criticalFindings.map((f, i) => (
                            <li key={i} className="text-xs">
                                • {f}
                            </li>
                        ))}
                    </ul>
                </div>
            </motion.div>
        </div>
    )
}
