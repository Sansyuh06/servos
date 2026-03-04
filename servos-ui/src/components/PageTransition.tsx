import { motion } from 'framer-motion'

/* Standard page wrapper with fade + slight slide transition */
export default function PageTransition({ children }: { children: React.ReactNode }) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
            className="h-full w-full"
        >
            {children}
        </motion.div>
    )
}
