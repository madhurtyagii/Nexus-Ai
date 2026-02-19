/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    darkMode: 'class',
    theme: {
        extend: {
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
                mono: ['JetBrains Mono', 'monospace'],
            },
            colors: {
                primary: {
                    50: 'var(--color-primary-50)',
                    100: 'var(--color-primary-100)',
                    200: 'var(--color-primary-200)',
                    300: 'var(--color-primary-300)',
                    400: 'var(--color-primary-400)',
                    500: 'var(--color-primary-500)',
                    600: 'var(--color-primary-600)',
                    700: 'var(--color-primary-700)',
                    800: 'var(--color-primary-800)',
                    900: 'var(--color-primary-900)',
                    950: 'var(--color-primary-950)',
                },
                dark: {
                    50: 'var(--color-dark-50)',
                    100: 'var(--color-dark-100)',
                    200: 'var(--color-dark-200)',
                    300: 'var(--color-dark-300)',
                    400: 'var(--color-dark-400)',
                    500: 'var(--color-dark-500)',
                    600: 'var(--color-dark-600)',
                    700: 'var(--color-dark-700)',
                    800: 'var(--color-dark-800)',
                    900: 'var(--color-dark-900)',
                    950: 'var(--color-dark-950)',
                }
            },
            animation: {
                'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                'gradient': 'gradient 8s linear infinite',
                'float': 'float 6s ease-in-out infinite',
                'float-slow': 'float 10s ease-in-out infinite',
                'float-delayed': 'float 8s ease-in-out 2s infinite',
                'shimmer': 'shimmer 1.5s ease-in-out infinite',
                'glow-pulse': 'glow-pulse 2s ease-in-out infinite',
                'gradient-flow': 'gradient-flow 6s ease infinite',
                'spin-slow': 'spin 6s linear infinite',
                'bounce-subtle': 'bounce-subtle 2s ease-in-out infinite',
                'slide-up': 'slide-up 0.5s cubic-bezier(0.16, 1, 0.3, 1)',
                'scale-in': 'scale-in 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
                // God-level additions
                'aurora-1': 'aurora-drift-1 25s ease-in-out infinite alternate',
                'aurora-2': 'aurora-drift-2 30s ease-in-out infinite alternate',
                'aurora-3': 'aurora-drift-3 35s ease-in-out infinite alternate',
                'border-flow': 'border-flow 4s linear infinite',
                'ripple': 'ripple 1s cubic-bezier(0, 0, 0.2, 1) forwards',
                'spotlight-pulse': 'spotlight-pulse 3s ease-in-out infinite',
                'text-reveal': 'text-reveal 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards',
                'counter-pop': 'counter-pop 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)',
                'progress-fill': 'progress-fill 1.5s cubic-bezier(0.4, 0, 0.2, 1) forwards',
                'status-ping': 'status-ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite',
            },
            keyframes: {
                gradient: {
                    '0%, 100%': { backgroundPosition: '0% 50%' },
                    '50%': { backgroundPosition: '100% 50%' },
                },
                float: {
                    '0%, 100%': { transform: 'translateY(0px)' },
                    '50%': { transform: 'translateY(-10px)' },
                },
                'gradient-flow': {
                    '0%': { backgroundPosition: '0% 50%' },
                    '50%': { backgroundPosition: '100% 50%' },
                    '100%': { backgroundPosition: '0% 50%' },
                },
                shimmer: {
                    '0%': { backgroundPosition: '-200% 0' },
                    '100%': { backgroundPosition: '200% 0' },
                },
                'glow-pulse': {
                    '0%, 100%': { boxShadow: '0 0 4px currentColor, 0 0 8px currentColor' },
                    '50%': { boxShadow: '0 0 8px currentColor, 0 0 20px currentColor' },
                },
                'bounce-subtle': {
                    '0%, 100%': { transform: 'translateY(0)' },
                    '50%': { transform: 'translateY(-4px)' },
                },
                'slide-up': {
                    '0%': { transform: 'translateY(10px)', opacity: '0' },
                    '100%': { transform: 'translateY(0)', opacity: '1' },
                },
                'scale-in': {
                    '0%': { transform: 'scale(0.95)', opacity: '0' },
                    '100%': { transform: 'scale(1)', opacity: '1' },
                },
                // God-level keyframes
                'aurora-drift-1': {
                    '0%': { transform: 'translate(-10%, -15%) rotate(0deg) scale(1)' },
                    '33%': { transform: 'translate(5%, -5%) rotate(60deg) scale(1.1)' },
                    '66%': { transform: 'translate(-5%, 10%) rotate(120deg) scale(0.95)' },
                    '100%': { transform: 'translate(10%, -10%) rotate(180deg) scale(1.05)' },
                },
                'aurora-drift-2': {
                    '0%': { transform: 'translate(10%, 5%) rotate(0deg) scale(1.05)' },
                    '33%': { transform: 'translate(-8%, 15%) rotate(-60deg) scale(0.95)' },
                    '66%': { transform: 'translate(5%, -10%) rotate(-120deg) scale(1.1)' },
                    '100%': { transform: 'translate(-10%, 5%) rotate(-180deg) scale(1)' },
                },
                'aurora-drift-3': {
                    '0%': { transform: 'translate(0%, 10%) rotate(0deg) scale(0.95)' },
                    '33%': { transform: 'translate(10%, -5%) rotate(90deg) scale(1.05)' },
                    '66%': { transform: 'translate(-10%, 0%) rotate(180deg) scale(1)' },
                    '100%': { transform: 'translate(5%, 5%) rotate(270deg) scale(1.1)' },
                },
                'border-flow': {
                    '0%': { backgroundPosition: '0% 0%' },
                    '100%': { backgroundPosition: '400% 0%' },
                },
                'ripple': {
                    '0%': { transform: 'scale(0)', opacity: '0.5' },
                    '100%': { transform: 'scale(4)', opacity: '0' },
                },
                'spotlight-pulse': {
                    '0%, 100%': { opacity: '0.5' },
                    '50%': { opacity: '0.8' },
                },
                'text-reveal': {
                    '0%': { transform: 'translateY(100%)', opacity: '0' },
                    '100%': { transform: 'translateY(0)', opacity: '1' },
                },
                'counter-pop': {
                    '0%': { transform: 'scale(0.8)', opacity: '0' },
                    '50%': { transform: 'scale(1.1)' },
                    '100%': { transform: 'scale(1)', opacity: '1' },
                },
                'progress-fill': {
                    '0%': { width: '0%' },
                    '100%': { width: 'var(--progress-target, 100%)' },
                },
                'status-ping': {
                    '0%': { transform: 'scale(1)', opacity: '1' },
                    '75%, 100%': { transform: 'scale(2.5)', opacity: '0' },
                },
            },
            backdropBlur: {
                '3xl': '64px',
                '4xl': '96px',
            },
            boxShadow: {
                'glow-sm': '0 0 10px rgba(14, 165, 233, 0.2)',
                'glow-md': '0 0 20px rgba(14, 165, 233, 0.3)',
                'glow-lg': '0 0 40px rgba(14, 165, 233, 0.2)',
                'glow-purple': '0 0 20px rgba(139, 92, 246, 0.3)',
                'glow-emerald': '0 0 20px rgba(16, 185, 129, 0.3)',
                'glow-amber': '0 0 20px rgba(245, 158, 11, 0.3)',
                'glow-rose': '0 0 20px rgba(244, 63, 94, 0.3)',
                'inner-glow': 'inset 0 1px 0 rgba(255, 255, 255, 0.05)',
                'inner-glow-strong': 'inset 0 1px 0 rgba(255, 255, 255, 0.1), inset 0 0 20px rgba(255, 255, 255, 0.02)',
                'depth': '0 1px 2px rgba(0,0,0,0.07), 0 2px 4px rgba(0,0,0,0.07), 0 4px 8px rgba(0,0,0,0.07), 0 8px 16px rgba(0,0,0,0.07)',
            },
        },
    },
    plugins: [],
}
