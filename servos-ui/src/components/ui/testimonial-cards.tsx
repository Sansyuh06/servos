"use client"

import * as React from 'react'
import { motion } from 'framer-motion'
import DoodleIcon from '@/components/DoodleIcon'

export function TestimonialCard({
    handleShuffle,
    testimonial,
    position,
    author,
    onClick,
}: {
    handleShuffle: () => void
    testimonial: string
    position: 'front' | 'middle' | 'back'
    id: string
    author: string
    onClick?: () => void
}) {
    const dragRef = React.useRef(0)
    const isFront = position === 'front'

    return (
        <motion.div
            style={{
                zIndex: position === 'front' ? '2' : position === 'middle' ? '1' : '0',
            }}
            animate={{
                rotate: position === 'front' ? '-6deg' : position === 'middle' ? '0deg' : '6deg',
                x: position === 'front' ? '0%' : position === 'middle' ? '33%' : '66%',
            }}
            drag={true}
            dragElastic={0.35}
            dragListener={isFront}
            dragConstraints={{
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
            }}
            onDragStart={(event: any) => {
                dragRef.current = event.clientX || (event.touches && event.touches[0].clientX) || 0
            }}
            onDragEnd={(event: any) => {
                const clientX = event.clientX || (event.changedTouches && event.changedTouches[0].clientX) || 0
                if(dragRef.current - clientX > 150) {
                    handleShuffle()
                }
                dragRef.current = 0
            }}
            onClick={() => {
                if(isFront && onClick) {
                    onClick()
                } else if(!isFront) {
                    handleShuffle()
                }
            }}
            transition={{ duration: 0.35 }}
            className={`absolute left-[calc(50%-175px)] top-[calc(50%-225px)] flex h-[450px] w-[350px] select-none flex-col items-center justify-center space-y-6 rounded-[28px] border border-white/10 bg-servos-card/90 p-6 shadow-[0_24px_50px_rgba(28,26,31,0.22)] backdrop-blur-md ${
                isFront ? 'cursor-grab active:cursor-grabbing' : ''
            }`}
        >
            <DoodleIcon name="dashboard" alt="Case doodle" size="xl" />
            <span className="text-center text-lg font-bold text-cream-bright font-mono">{testimonial}</span>
            <span className="text-center text-sm font-medium text-accent-light">
                Investigator: {author}
            </span>
        </motion.div>
    )
}
