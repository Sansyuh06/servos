import React, { useEffect, useRef } from 'react';

const TopoHero: React.FC = () => {
    const canvasRef = useRef<HTMLDivElement>(null);
    const layersRef = useRef<HTMLDivElement[]>([]);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        // Mouse Parallax Logic
        const handleMouseMove = (e: MouseEvent) => {
            const x = (window.innerWidth / 2 - e.pageX) / 40;
            const y = (window.innerHeight / 2 - e.pageY) / 40;

            // Rotate the 3D Canvas
            canvas.style.transform = `rotateX(${65 + y / 2}deg) rotateZ(${-25 + x / 2}deg)`;

            // Apply depth shift to layers
            layersRef.current.forEach((layer, index) => {
                if (!layer) return;
                const depth = (index + 1) * 20;
                const moveX = x * (index + 1) * 0.1;
                const moveY = y * (index + 1) * 0.1;
                layer.style.transform = `translateZ(${depth}px) translate(${moveX}px, ${moveY}px)`;
            });
        };

        // Entrance Animation
        canvas.style.opacity = '0';
        canvas.style.transform = 'rotateX(90deg) rotateZ(0deg) scale(0.8)';

        const timeout = setTimeout(() => {
            canvas.style.transition = 'all 2.5s cubic-bezier(0.16, 1, 0.3, 1)';
            canvas.style.opacity = '1';
            canvas.style.transform = 'rotateX(65deg) rotateZ(-25deg) scale(1)';
        }, 300);

        window.addEventListener('mousemove', handleMouseMove);

        return () => {
            window.removeEventListener('mousemove', handleMouseMove);
            clearTimeout(timeout);
        };
    }, []);

    return (
        <div className="relative w-full h-[60vh] bg-servos-bg overflow-hidden flex items-center justify-center rounded-2xl border border-servos-border">
            <div className="absolute inset-0 pointer-events-none z-10 opacity-20 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0IiBoZWlnaHQ9IjQiPgo8cmVjdCB3aWR0aD0iNCIgaGVpZ2h0PSI0IiBmaWxsPSIjZmZmIiBmaWxsLW9wYWNpdHk9IjAuMDUiLz4KPC9zdmc+')] mix-blend-overlay"></div>

            <div className="perspective-[2000px] w-full h-full flex items-center justify-center overflow-hidden absolute inset-0">
                <div
                    ref={canvasRef}
                    className="relative w-[120%] h-[120%] transform-style-3d transition-transform duration-[800ms] ease-out-expo"
                    style={{ transformStyle: 'preserve-3d' }}
                >
                    {/* Topographic Lines Effect */}
                    <div
                        ref={el => el && (layersRef.current[0] = el)}
                        className="absolute inset-[-50%] border border-servos-border rounded-full transition-transform duration-500"
                        style={{ backgroundImage: 'repeating-radial-gradient(circle at 50% 50%, transparent 0, transparent 40px, rgba(255,255,255,0.02) 41px, transparent 42px)' }}
                    />
                    <div
                        ref={el => el && (layersRef.current[1] = el)}
                        className="absolute inset-[-50%] border border-servos-border-dim rounded-full transition-transform duration-500"
                        style={{ backgroundImage: 'repeating-radial-gradient(circle at 50% 50%, transparent 0, transparent 40px, rgba(156,138,185,0.05) 41px, transparent 42px)' }}
                    />

                    {/* Core Network Nodes */}
                    <div
                        ref={el => el && (layersRef.current[2] = el)}
                        className="absolute inset-0 transition-transform duration-500 flex items-center justify-center"
                    >
                        <div className="w-[400px] h-[400px] border border-accent/20 rounded-full animate-[spin_60s_linear_infinite] flex items-center justify-center">
                            <div className="w-[300px] h-[300px] border border-servos-border/30 rounded-full animate-[spin_40s_linear_infinite_reverse] flex items-center justify-center">
                                <div className="w-[100px] h-[100px] bg-accent/10 blur-xl rounded-full" />
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="relative z-20 text-center pointer-events-none flex flex-col items-center">
                <h1 className="text-6xl md:text-8xl font-black text-transparent bg-clip-text bg-gradient-to-b from-cream-bright to-cream-dim tracking-tighter drop-shadow-2xl mb-4 mix-blend-plus-lighter">
                    SERVOS
                </h1>
                <p className="text-xl md:text-2xl text-accent font-medium tracking-widest uppercase">
                    Offline AI Forensics
                </p>
            </div>

            {/* Overlay Gradients */}
            <div className="absolute inset-0 bg-gradient-to-t from-servos-bg via-transparent to-transparent z-10" />
            <div className="absolute inset-0 bg-gradient-to-b from-servos-bg/50 via-transparent to-transparent z-10" />
        </div>
    );
};

export default TopoHero;
