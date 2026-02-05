import { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion, useScroll, useTransform, AnimatePresence } from 'framer-motion';
import {
    Sparkles,
    Zap,
    Brain,
    Users,
    Shield,
    Rocket,
    ChevronRight,
    Play,
    ArrowRight,
    Code2,
    GitBranch,
    Layers,
    Target,
    CheckCircle2,
    Star,
    MousePointer2
} from 'lucide-react';

// Floating particles component
const FloatingParticles = () => {
    const particles = Array.from({ length: 50 }, (_, i) => ({
        id: i,
        size: Math.random() * 4 + 2,
        x: Math.random() * 100,
        y: Math.random() * 100,
        duration: Math.random() * 20 + 10,
        delay: Math.random() * 5,
    }));

    return (
        <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
            {particles.map((p) => (
                <motion.div
                    key={p.id}
                    className="absolute rounded-full bg-primary-500/20"
                    style={{
                        width: p.size,
                        height: p.size,
                        left: `${p.x}%`,
                        top: `${p.y}%`,
                    }}
                    animate={{
                        y: [0, -100, 0],
                        opacity: [0.2, 0.8, 0.2],
                        scale: [1, 1.5, 1],
                    }}
                    transition={{
                        duration: p.duration,
                        delay: p.delay,
                        repeat: Infinity,
                        ease: "easeInOut",
                    }}
                />
            ))}
        </div>
    );
};

// Animated gradient orbs
const GradientOrbs = () => (
    <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
        <motion.div
            className="absolute -top-40 -right-40 w-96 h-96 bg-primary-500/30 rounded-full blur-[128px]"
            animate={{ scale: [1, 1.2, 1], opacity: [0.3, 0.5, 0.3] }}
            transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.div
            className="absolute top-1/2 -left-40 w-96 h-96 bg-purple-500/20 rounded-full blur-[128px]"
            animate={{ scale: [1.2, 1, 1.2], opacity: [0.2, 0.4, 0.2] }}
            transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.div
            className="absolute -bottom-40 right-1/4 w-80 h-80 bg-pink-500/20 rounded-full blur-[100px]"
            animate={{ scale: [1, 1.3, 1], opacity: [0.2, 0.3, 0.2] }}
            transition={{ duration: 12, repeat: Infinity, ease: "easeInOut" }}
        />
    </div>
);

// Animated logo component
const AnimatedLogo = () => (
    <motion.div
        className="relative w-32 h-32 mx-auto mb-8"
        initial={{ scale: 0, rotate: -180 }}
        animate={{ scale: 1, rotate: 0 }}
        transition={{ type: "spring", stiffness: 200, damping: 20, delay: 0.2 }}
    >
        <motion.div
            className="absolute inset-0 bg-gradient-to-br from-primary-500 to-purple-600 rounded-3xl blur-2xl"
            animate={{ scale: [1, 1.2, 1], opacity: [0.5, 0.8, 0.5] }}
            transition={{ duration: 3, repeat: Infinity }}
        />
        <motion.div
            className="relative w-full h-full bg-gradient-to-br from-primary-500/20 to-purple-500/20 rounded-3xl p-3 border border-white/10 overflow-hidden"
            whileHover={{ scale: 1.05, rotate: 5 }}
        >
            <img src="/logo.png" alt="Nexus AI" className="w-full h-full object-contain" />
            <motion.div
                className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
                animate={{ x: ['-100%', '100%'] }}
                transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
            />
        </motion.div>
    </motion.div>
);

// Feature card component
const FeatureCard = ({ icon: Icon, title, description, delay, gradient }) => (
    <motion.div
        initial={{ opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-50px" }}
        transition={{ duration: 0.6, delay }}
        whileHover={{ y: -10, scale: 1.02 }}
        className="group relative"
    >
        <div className="absolute inset-0 bg-gradient-to-br opacity-0 group-hover:opacity-100 transition-opacity duration-500 rounded-3xl blur-xl -z-10"
            style={{ background: gradient }} />
        <div className="glass p-8 rounded-3xl border border-white/5 h-full relative overflow-hidden">
            <motion.div
                className="absolute top-0 right-0 w-32 h-32 opacity-5"
                animate={{ rotate: 360 }}
                transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
            >
                <Icon className="w-full h-full" />
            </motion.div>
            <div className={`w-14 h-14 rounded-2xl flex items-center justify-center mb-6 ${gradient} shadow-lg`}>
                <Icon className="w-7 h-7 text-white" />
            </div>
            <h3 className="text-xl font-black text-white mb-3 tracking-tight">{title}</h3>
            <p className="text-dark-400 leading-relaxed">{description}</p>
        </div>
    </motion.div>
);

// Stat counter component
const StatCounter = ({ value, suffix, label, delay }) => {
    const [count, setCount] = useState(0);
    const ref = useRef(null);

    useEffect(() => {
        const observer = new IntersectionObserver(
            ([entry]) => {
                if (entry.isIntersecting) {
                    let start = 0;
                    const end = parseInt(value);
                    const duration = 2000;
                    const increment = end / (duration / 16);

                    const timer = setInterval(() => {
                        start += increment;
                        if (start >= end) {
                            setCount(end);
                            clearInterval(timer);
                        } else {
                            setCount(Math.floor(start));
                        }
                    }, 16);
                }
            },
            { threshold: 0.5 }
        );

        if (ref.current) observer.observe(ref.current);
        return () => observer.disconnect();
    }, [value]);

    return (
        <motion.div
            ref={ref}
            initial={{ opacity: 0, scale: 0.5 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay }}
            className="text-center"
        >
            <div className="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-primary-400 to-purple-400">
                {count}{suffix}
            </div>
            <div className="text-dark-400 font-medium mt-2">{label}</div>
        </motion.div>
    );
};

// Main Landing component
export default function Landing() {
    const navigate = useNavigate();
    const { scrollYProgress } = useScroll();
    const heroOpacity = useTransform(scrollYProgress, [0, 0.2], [1, 0]);
    const heroScale = useTransform(scrollYProgress, [0, 0.2], [1, 0.95]);

    const features = [
        {
            icon: Brain,
            title: "7 Specialized Agents",
            description: "From planning to execution, our AI agents work in perfect harmony to complete your tasks.",
            gradient: "bg-gradient-to-br from-primary-500 to-cyan-500",
        },
        {
            icon: GitBranch,
            title: "Visual Workflow Builder",
            description: "Drag-and-drop interface to create complex automation pipelines with ease.",
            gradient: "bg-gradient-to-br from-purple-500 to-pink-500",
        },
        {
            icon: Layers,
            title: "Multi-Phase Projects",
            description: "Break down complex goals into manageable phases with automatic progress tracking.",
            gradient: "bg-gradient-to-br from-orange-500 to-red-500",
        },
        {
            icon: Shield,
            title: "Enterprise Security",
            description: "AES-256 encryption, secure API tunnels, and granular access controls.",
            gradient: "bg-gradient-to-br from-green-500 to-emerald-500",
        },
        {
            icon: Target,
            title: "Smart Task Routing",
            description: "AI automatically assigns tasks to the most capable agent for optimal results.",
            gradient: "bg-gradient-to-br from-blue-500 to-indigo-500",
        },
        {
            icon: Code2,
            title: "Developer First",
            description: "RESTful API, webhooks, and SDKs for seamless integration with your stack.",
            gradient: "bg-gradient-to-br from-violet-500 to-purple-500",
        },
    ];

    const steps = [
        { icon: MousePointer2, title: "Describe Your Goal", description: "Tell Nexus what you want to achieve in natural language." },
        { icon: Brain, title: "AI Plans & Assigns", description: "Our orchestrator breaks down tasks and assigns specialized agents." },
        { icon: Zap, title: "Watch It Execute", description: "Real-time progress tracking as agents collaborate on your project." },
        { icon: CheckCircle2, title: "Review & Deploy", description: "Get polished deliverables ready for production." },
    ];

    return (
        <div className="min-h-screen bg-dark-950 text-white overflow-x-hidden">
            <FloatingParticles />
            <GradientOrbs />

            {/* Navigation */}
            <motion.nav
                initial={{ y: -100 }}
                animate={{ y: 0 }}
                transition={{ type: "spring", stiffness: 100, damping: 20 }}
                className="fixed top-0 left-0 right-0 z-50 px-6 py-4"
            >
                <div className="max-w-7xl mx-auto glass rounded-2xl px-6 py-3 border border-white/5 flex items-center justify-between">
                    <Link to="/" className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl overflow-hidden bg-gradient-to-br from-primary-500/20 to-purple-500/20 p-0.5">
                            <img src="/logo.png" alt="Nexus AI" className="w-full h-full object-contain" />
                        </div>
                        <span className="text-xl font-black tracking-tighter">Nexus AI</span>
                    </Link>
                    <div className="flex items-center gap-4">
                        <Link to="/login" className="text-dark-300 hover:text-white transition-colors font-medium px-4 py-2">
                            Sign In
                        </Link>
                        <Link
                            to="/signup"
                            className="bg-primary-500 hover:bg-primary-400 text-white font-bold px-6 py-2.5 rounded-xl transition-all hover:shadow-[0_10px_30px_rgba(14,165,233,0.3)] active:scale-95"
                        >
                            Get Started
                        </Link>
                    </div>
                </div>
            </motion.nav>

            {/* Hero Section */}
            <motion.section
                style={{ opacity: heroOpacity, scale: heroScale }}
                className="min-h-screen flex flex-col items-center justify-center px-6 pt-24 pb-16 relative z-10"
            >
                <AnimatedLogo />

                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4 }}
                    className="text-center max-w-4xl mx-auto"
                >
                    <motion.div
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: 0.5 }}
                        className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-500/10 border border-primary-500/20 text-primary-400 text-sm font-bold mb-8"
                    >
                        <Sparkles className="w-4 h-4" />
                        <span>Intelligence v2.0 Now Live</span>
                        <ChevronRight className="w-4 h-4" />
                    </motion.div>

                    <h1 className="text-5xl md:text-7xl font-black tracking-tighter mb-6 leading-[0.95]">
                        <span className="text-white">The Future of</span>
                        <br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-400 via-purple-400 to-pink-400">
                            AI Automation
                        </span>
                    </h1>

                    <p className="text-xl text-dark-400 max-w-2xl mx-auto mb-10 leading-relaxed">
                        7 specialized AI agents working in perfect harmony. From idea to execution,
                        Nexus transforms your vision into reality with unprecedented speed and precision.
                    </p>

                    <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                        <motion.button
                            onClick={() => navigate('/signup')}
                            whileHover={{ scale: 1.05, boxShadow: "0 20px 40px rgba(14,165,233,0.3)" }}
                            whileTap={{ scale: 0.95 }}
                            className="group flex items-center gap-3 bg-gradient-to-r from-primary-500 to-primary-400 text-white font-bold px-8 py-4 rounded-2xl text-lg transition-all"
                        >
                            <Rocket className="w-5 h-5" />
                            <span>Start Building Free</span>
                            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                        </motion.button>

                        <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="flex items-center gap-3 bg-white/5 hover:bg-white/10 border border-white/10 text-white font-bold px-8 py-4 rounded-2xl text-lg transition-all"
                        >
                            <Play className="w-5 h-5" />
                            <span>Watch Demo</span>
                        </motion.button>
                    </div>
                </motion.div>

                {/* Scroll indicator */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 1.5 }}
                    className="absolute bottom-8 left-1/2 -translate-x-1/2"
                >
                    <motion.div
                        animate={{ y: [0, 10, 0] }}
                        transition={{ duration: 2, repeat: Infinity }}
                        className="w-6 h-10 border-2 border-white/20 rounded-full flex justify-center pt-2"
                    >
                        <motion.div
                            animate={{ opacity: [0.5, 1, 0.5], y: [0, 8, 0] }}
                            transition={{ duration: 2, repeat: Infinity }}
                            className="w-1.5 h-1.5 bg-primary-400 rounded-full"
                        />
                    </motion.div>
                </motion.div>
            </motion.section>

            {/* Stats Section */}
            <section className="py-24 px-6 relative z-10">
                <div className="max-w-5xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-8">
                    <StatCounter value="7" suffix="" label="AI Agents" delay={0} />
                    <StatCounter value="500" suffix="ms" label="Avg Response" delay={0.1} />
                    <StatCounter value="99" suffix="%" label="Uptime" delay={0.2} />
                    <StatCounter value="10" suffix="K+" label="Tasks Completed" delay={0.3} />
                </div>
            </section>

            {/* Features Section */}
            <section className="py-24 px-6 relative z-10">
                <div className="max-w-7xl mx-auto">
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        className="text-center mb-16"
                    >
                        <h2 className="text-4xl md:text-5xl font-black tracking-tight mb-4">
                            <span className="text-transparent bg-clip-text bg-gradient-to-r from-white to-dark-300">
                                Built for the Future
                            </span>
                        </h2>
                        <p className="text-dark-400 text-xl max-w-2xl mx-auto">
                            Everything you need to automate complex workflows with AI
                        </p>
                    </motion.div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {features.map((feature, i) => (
                            <FeatureCard key={i} {...feature} delay={i * 0.1} />
                        ))}
                    </div>
                </div>
            </section>

            {/* How It Works Section */}
            <section className="py-24 px-6 relative z-10">
                <div className="max-w-5xl mx-auto">
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        className="text-center mb-16"
                    >
                        <h2 className="text-4xl md:text-5xl font-black tracking-tight mb-4">
                            How It Works
                        </h2>
                        <p className="text-dark-400 text-xl">From idea to execution in 4 simple steps</p>
                    </motion.div>

                    <div className="relative">
                        {/* Connection line */}
                        <div className="absolute top-1/2 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-primary-500/30 to-transparent hidden md:block" />

                        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
                            {steps.map((step, i) => (
                                <motion.div
                                    key={i}
                                    initial={{ opacity: 0, y: 40 }}
                                    whileInView={{ opacity: 1, y: 0 }}
                                    viewport={{ once: true }}
                                    transition={{ delay: i * 0.15 }}
                                    className="relative text-center"
                                >
                                    <motion.div
                                        whileHover={{ scale: 1.1, rotate: 5 }}
                                        className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-primary-500/20 to-purple-500/20 border border-white/10 flex items-center justify-center relative"
                                    >
                                        <step.icon className="w-9 h-9 text-primary-400" />
                                        <div className="absolute -top-2 -right-2 w-7 h-7 bg-primary-500 rounded-lg flex items-center justify-center text-xs font-black">
                                            {i + 1}
                                        </div>
                                    </motion.div>
                                    <h3 className="text-lg font-bold text-white mb-2">{step.title}</h3>
                                    <p className="text-dark-400 text-sm">{step.description}</p>
                                </motion.div>
                            ))}
                        </div>
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="py-32 px-6 relative z-10">
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    viewport={{ once: true }}
                    className="max-w-4xl mx-auto text-center glass rounded-[3rem] p-16 border border-white/5 relative overflow-hidden"
                >
                    <motion.div
                        className="absolute inset-0 bg-gradient-to-br from-primary-500/10 to-purple-500/10"
                        animate={{ opacity: [0.5, 0.8, 0.5] }}
                        transition={{ duration: 4, repeat: Infinity }}
                    />
                    <div className="relative z-10">
                        <h2 className="text-4xl md:text-5xl font-black tracking-tight mb-4">
                            Ready to Transform Your Workflow?
                        </h2>
                        <p className="text-dark-400 text-xl mb-10 max-w-xl mx-auto">
                            Join thousands of developers automating their work with Nexus AI
                        </p>
                        <motion.button
                            onClick={() => navigate('/signup')}
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="bg-gradient-to-r from-primary-500 to-purple-500 hover:from-primary-400 hover:to-purple-400 text-white font-bold px-10 py-5 rounded-2xl text-lg transition-all shadow-[0_20px_50px_rgba(14,165,233,0.3)]"
                        >
                            Get Started for Free
                        </motion.button>
                    </div>
                </motion.div>
            </section>

            {/* Footer */}
            <footer className="py-12 px-6 border-t border-white/5 relative z-10">
                <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg overflow-hidden">
                            <img src="/logo.png" alt="Nexus AI" className="w-full h-full object-contain" />
                        </div>
                        <span className="font-bold text-dark-400">© 2026 Nexus AI. All rights reserved.</span>
                    </div>
                    <div className="flex items-center gap-6 text-dark-400">
                        <a href="#" className="hover:text-white transition-colors">Privacy</a>
                        <a href="#" className="hover:text-white transition-colors">Terms</a>
                        <a href="#" className="hover:text-white transition-colors">Docs</a>
                        <a href="#" className="hover:text-white transition-colors">GitHub</a>
                    </div>
                </div>
            </footer>
        </div>
    );
}
