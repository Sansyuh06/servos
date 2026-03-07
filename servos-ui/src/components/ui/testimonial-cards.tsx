"use client";

import * as React from 'react';
import { motion } from 'framer-motion';
import { FolderOpen } from 'lucide-react';

export function TestimonialCard({ handleShuffle, testimonial, position, id, author, onClick }: { handleShuffle: () => void, testimonial: string, position: 'front' | 'middle' | 'back', id: string, author: string, onClick?: () => void }) {
  const dragRef = React.useRef(0);
  const isFront = position === "front";

  return (
    <motion.div
      style={{
        zIndex: position === "front" ? "2" : position === "middle" ? "1" : "0"
      }}
      animate={{
        rotate: position === "front" ? "-6deg" : position === "middle" ? "0deg" : "6deg",
        x: position === "front" ? "0%" : position === "middle" ? "33%" : "66%"
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
        dragRef.current = e.clientX || (e.touches && e.touches[0].clientX) || 0;
      }}
      onDragEnd={(e: any) => {
        const clientX = e.clientX || (e.changedTouches && e.changedTouches[0].clientX) || 0;
        if (dragRef.current - clientX > 150) {
          handleShuffle();
        }
        dragRef.current = 0;
      }}
      onClick={() => {
        if (isFront && onClick) {
          // Trigger click only on front card to view case details
          onClick();
        } else if (!isFront) {
          // Shuffle if clicking a background card
          handleShuffle();
        }
      }}
      transition={{ duration: 0.35 }}
      className={`absolute left-[calc(50%-175px)] top-[calc(50%-225px)] flex flex-col items-center justify-center space-y-6 h-[450px] w-[350px] select-none rounded-2xl border-2 border-servos-border bg-servos-surface/80 p-6 shadow-xl backdrop-blur-md ${isFront ? "cursor-grab active:cursor-grabbing" : ""
        }`}
    >
      <div className="mx-auto flex h-32 w-32 items-center justify-center rounded-full border-4 border-accent bg-servos-elevated shadow-[0_0_20px_rgba(156,138,185,0.4)]">
        <FolderOpen size={48} className="text-cream" />
      </div>
      <span className="text-center text-lg font-bold text-cream-bright font-mono">{testimonial}</span>
      <span className="text-center text-sm font-medium text-accent">Investigator: {author}</span>
    </motion.div>
  );
};