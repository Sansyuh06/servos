import { useMemo } from 'react'

/**
 * Subtle SVG topographic contour background.
 * Slow, calm, non-distracting — forensic investigation tool, not marketing.
 */
export default function TopoBackground() {
    const rings = useMemo(() => {
        const r: { cx: number; cy: number; rx: number; ry: number; opacity: number }[] = []
        // Main peak
        for(let i = 0; i < 14; i++) {
            const radius = 80 + i * 55
            r.push({ cx: 50, cy: 45, rx: radius, ry: radius * 0.6, opacity: Math.max(0.03, 0.12 - i * 0.007) })
        }
        // Secondary peak (right)
        for(let i = 0; i < 8; i++) {
            const radius = 40 + i * 45
            r.push({ cx: 78, cy: 60, rx: radius, ry: radius * 0.55, opacity: Math.max(0.02, 0.08 - i * 0.008) })
        }
        // Tertiary peak (left)
        for(let i = 0; i < 6; i++) {
            const radius = 30 + i * 40
            r.push({ cx: 15, cy: 30, rx: radius, ry: radius * 0.65, opacity: Math.max(0.02, 0.06 - i * 0.007) })
        }
        return r
    }, [])

    return (
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
            <svg
                className="w-full h-full animate-topo-drift"
                viewBox="0 0 100 100"
                preserveAspectRatio="none"
                xmlns="http://www.w3.org/2000/svg"
            >
                {rings.map((ring, i) => (
                    <ellipse
                        key={i}
                        cx={ring.cx}
                        cy={ring.cy}
                        rx={ring.rx / 10}
                        ry={ring.ry / 10}
                        fill="none"
                        stroke="#8F7DBA"
                        strokeWidth="0.08"
                        opacity={ring.opacity}
                    />
                ))}
            </svg>

            {/* Film grain overlay */}
            <div
                className="absolute inset-0 mix-blend-overlay opacity-[0.03]"
                style={{
                    backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='256' height='256' filter='url(%23n)' opacity='0.7'/%3E%3C/svg%3E")`,
                    backgroundSize: '128px 128px',
                }}
            />
        </div>
    )
}
