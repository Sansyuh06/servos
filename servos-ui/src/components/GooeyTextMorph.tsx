import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

/**
 * Gooey text morphing — SVG filter based.
 * Used ONLY for page titles, mode switching, investigation state.
 * Fast, elegant. Not overused.
 */
interface Props {
    texts: string[]
    intervalMs?: number
    className?: string
}

export default function GooeyTextMorph({ texts, intervalMs = 3000, className = '' }: Props) {
    const [index, setIndex] = useState(0)

    useEffect(() => {
        const timer = setInterval(() => {
            setIndex((prev) => (prev + 1) % texts.length)
        }, intervalMs)
        return () => clearInterval(timer)
    }, [texts.length, intervalMs])

    return (
        <div className={`relative ${className}`}>
            {/* SVG filter for gooey effect */}
            <svg className="absolute w-0 h-0">
                <defs>
                    <filter id="gooey-morph">
                        <feGaussianBlur in="SourceGraphic" stdDeviation="6" result="blur" />
                        <feColorMatrix
                            in="blur"
                            mode="matrix"
                            values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 18 -7"
                            result="goo"
                        />
                        <feComposite in="SourceGraphic" in2="goo" operator="atop" />
                    </filter>
                </defs>
            </svg>

            <div style={{ filter: 'url(#gooey-morph)' }}>
                <AnimatePresence mode="wait">
                    <motion.span
                        key={index}
                        initial={{ opacity: 0, filter: 'blur(8px)' }}
                        animate={{ opacity: 1, filter: 'blur(0px)' }}
                        exit={{ opacity: 0, filter: 'blur(8px)' }}
                        transition={{ duration: 0.5, ease: [0.4, 0, 0.2, 1] }}
                        className="inline-block"
                    >
                        {texts[index]}
                    </motion.span>
                </AnimatePresence>
            </div>
        </div>
    )
}
