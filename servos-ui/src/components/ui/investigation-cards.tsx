"use client";

import * as React from 'react';
import { motion } from 'framer-motion';

export function InvestigationCard({
    handleShuffle, caseRef, position, id, title, date, risk, status
}: {
    handleShuffle: () => void, caseRef: string, position: string, id: string, title: string, date: string, risk: string, status: string
}) {
    const dragRef = React.useRef(0);
    const isFront = position === "front";

    const getRiskColor = (r: string) => {
        switch (r.toLowerCase()) {
            case 'high': return 'text-red-400 border-red-500/50 bg-red-500/10';
            case 'medium': return 'text-orange-400 border-orange-500/50 bg-orange-500/10';
            default: return 'text-green-400 border-green-500/50 bg-green-500/10';
        }
    };

    return (
        <motion.div
            style={{
                zIndex: position === "front" ? "2" : position === "middle" ? "1" : "0"
            }}
            animate={{
                rotate: position === "front" ? "-6deg" : position === "middle" ? "0deg" : "6deg",
                x: position === "front" ? "0%" : position === "middle" ? "33%" : "66%",
                scale: position === "front" ? 1 : position === "middle" ? 0.9 : 0.8,
            }}
            drag={true}
            dragElastic={0.35}
            dragListener={isFront}
            dragConstraints={{
                top: 0,
                left: 0,
                right: 0,
                bottom: 0
            }}
            onDragStart={(e: any) => {
                dragRef.current = e.clientX;
            }}
            onDragEnd={(e: any) => {
                if (typeof e.clientX !== 'undefined' && dragRef.current - e.clientX > 100) {
                    handleShuffle();
                }
                dragRef.current = 0;
            }}
            transition={{ duration: 0.35 }}
            className={`absolute left-0 top-0 flex flex-col h-[300px] w-[350px] select-none space-y-4 rounded-2xl border border-servos-border bg-servos-card p-6 shadow-2xl backdrop-blur-md ${isFront ? "cursor-grab active:cursor-grabbing" : ""
                }`}
        >
            <div className="flex justify-between items-start">
                <div className="flex flex-col">
                    <span className="text-sm font-mono text-cream-dim">{caseRef}</span>
                    <span className="text-xl font-bold text-cream-bright mt-1 truncate">{title}</span>
                </div>
                <span className={`text-xs px-2 py-1 rounded-full font-semibold border ${getRiskColor(risk)}`}>
                    {risk} Risk
                </span>
            </div>

            <div className="flex-1" />

            <div className="flex justify-between items-center text-sm text-cream-dim">
                <span>{date}</span>
                <span className="bg-servos-elevated px-3 py-1 rounded-md text-cream-bright">{status}</span>
            </div>

            {isFront && (
                <div className="absolute -bottom-10 left-1/2 -translate-x-1/2 text-xs text-accent animate-pulse">
                    Swipe left for next
                </div>
            )}
        </motion.div>
    );
};
