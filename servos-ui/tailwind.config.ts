/** @type {import('tailwindcss').Config} */
export default {
    content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
    theme: {
        extend: {
            colors: {
                servos: {
                    bg: '#535353',            // BG_PRIMARY
                    surface: '#4a4a4a',       // BG_SURFACE
                    elevated: '#615d66',      // BG_ELEVATED
                    card: '#5b595e',          // BG_CARD
                    hover: '#66676e',
                    border: '#4f4f4f',
                    'border-dim': '#3f3f3f',
                },
                accent: {
                    DEFAULT: '#8F7DBA',
                    dark: '#7A6AA3',
                    light: '#A794CC',
                    muted: 'rgba(143, 125, 186, 0.12)',
                    'muted-border': 'rgba(143, 125, 186, 0.25)',
                },
                cream: '#EDEBE3',
                'cream-dim': '#AFAFAF',
                'cream-bright': '#F5F3ED',
                danger: '#C85A5A',
                'danger-muted': 'rgba(200, 90, 90, 0.12)',
                success: '#5A8F6A',
                'success-muted': 'rgba(90, 143, 106, 0.12)',
                warning: '#C4935A',
                'warning-muted': 'rgba(196, 147, 90, 0.12)',
            },
            fontFamily: {
                sans: ['"TT Firs Neue"', '"Inter"', '"Segoe UI"', 'system-ui', '-apple-system', 'sans-serif'],
                heading: ['"Heading Now"', '"TT Firs Neue"', '"Inter"', 'sans-serif'],
                mono: ['"JetBrains Mono"', '"Cascadia Code"', '"Consolas"', 'monospace'],
            },
            borderRadius: {
                DEFAULT: '6px',
                lg: '8px',
            },
            spacing: {
                '18': '4.5rem',
                '88': '22rem',
            },
            animation: {
                'topo-drift': 'topoDrift 60s linear infinite',
                'fade-in': 'fadeIn 0.5s ease-out',
            },
            keyframes: {
                topoDrift: {
                    '0%': { transform: 'translate(0, 0)' },
                    '50%': { transform: 'translate(-2%, -1%)' },
                    '100%': { transform: 'translate(0, 0)' },
                },
                fadeIn: {
                    '0%': { opacity: '0', transform: 'translateY(4px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' },
                },
            },
        },
    },
    plugins: [],
}
