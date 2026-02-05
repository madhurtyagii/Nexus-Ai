import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Brain,
    Zap,
    Shield,
    Sparkles,
    ArrowRight,
    Users,
    FileText,
    Code,
    Search,
    CheckCircle2,
    Play,
    ChevronRight,
    Star,
    Cpu,
    Network,
    Bot,
    Eye,
    EyeOff,
    Loader2,
    Mail,
    Lock
} from 'lucide-react';

// Floating particles background
const FloatingParticles = () => {
    const particles = Array.from({ length: 30 }, (_, i) => ({
        id: i,
        size: Math.random() * 4 + 2,
        x: Math.random() * 100,
        y: Math.random() * 100,
        duration: Math.random() * 20 + 15,
        delay: Math.random() * 5
    }));

    return (
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
            {particles.map((p) => (
                <motion.div
                    key={p.id}
                    className="absolute rounded-full bg-primary-500/20"
                    style={{
                        width: p.size,
                        height: p.size,
                        left: `${p.x}%`,
                        top: `${p.y}%`
                    }}
                    animate={{
                        y: [0, -100, 0],
                        x: [0, Math.random() * 50 - 25, 0],
                        opacity: [0.2, 0.6, 0.2],
                        scale: [1, 1.5, 1]
                    }}
                    transition={{
                        duration: p.duration,
                        repeat: Infinity,
                        delay: p.delay,
                        ease: "easeInOut"
                    }}
                />
            ))}
        </div>
    );
};

// Feature showcase slides
const features = [
    {
        icon: Brain,
        title: "7 Specialized AI Agents",
        description: "From code generation to quality assurance, each agent masters their domain",
        color: "from-primary-500 to-cyan-400",
        demo: ["ResearchAgent analyzing requirements...", "CoderAgent generating solution...", "QAAgent testing code..."]
    },
    {
        icon: Network,
        title: "Intelligent Task Orchestration",
        description: "Watch AI agents collaborate seamlessly on complex projects",
        color: "from-purple-500 to-pink-500",
        demo: ["Breaking down your request...", "Assigning to optimal agents...", "Synthesizing final output..."]
    },
    {
        icon: FileText,
        title: "Document Intelligence",
        description: "Upload any document and let AI extract knowledge instantly",
        color: "from-emerald-500 to-teal-400",
        demo: ["Processing PDF document...", "Extracting key insights...", "Ready for Q&A..."]
    },
    {
        icon: Code,
        title: "Full-Stack Code Generation",
        description: "From idea to production-ready code in minutes",
        color: "from-orange-500 to-amber-400",
        demo: ["Understanding requirements...", "Generating components...", "Writing tests..."]
    }
];

// How it works steps
const steps = [
    { num: "01", title: "Describe Your Goal", desc: "Tell Nexus what you want to build or solve" },
    { num: "02", title: "AI Analyzes", desc: "Intelligent agents break down the task" },
    { num: "03", title: "Agents Collaborate", desc: "Watch real-time progress as agents work together" },
    { num: "04", title: "Get Results", desc: "Receive polished, production-ready output" }
];

// Stats
const stats = [
    { value: "7", label: "AI Agents" },
    { value: "10x", label: "Faster" },
    { value: "99%", label: "Accuracy" },
    { value: "24/7", label: "Available" }
];

export default function Login() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    const [activeFeature, setActiveFeature] = useState(0);
    const [demoLine, setDemoLine] = useState(0);
    const { login } = useAuth();
    const navigate = useNavigate();

    // Auto-rotate features
    useEffect(() => {
        const interval = setInterval(() => {
            setActiveFeature((prev) => (prev + 1) % features.length);
            setDemoLine(0);
        }, 5000);
        return () => clearInterval(interval);
    }, []);

    // Animate demo text
    useEffect(() => {
        const interval = setInterval(() => {
            setDemoLine((prev) => (prev + 1) % 3);
        }, 1500);
        return () => clearInterval(interval);
    }, [activeFeature]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        const result = await login(email, password);
        if (result.success) {
            navigate('/dashboard');
        }
        setIsLoading(false);
    };

    const currentFeature = features[activeFeature];

    return (
        <div className="min-h-screen bg-dark-950 relative overflow-hidden">
            {/* Background Effects */}
            <FloatingParticles />
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,rgba(14,165,233,0.15),transparent_50%)]" />
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_left,rgba(139,92,246,0.1),transparent_50%)]" />

            {/* Grid Pattern */}
            <div className="absolute inset-0 opacity-[0.02]" style={{
                backgroundImage: 'linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)',
                backgroundSize: '60px 60px'
            }} />

            <div className="relative z-10 min-h-screen flex">
                {/* Left Side - Feature Showcase */}
                <div className="hidden lg:flex lg:w-[55%] xl:w-[60%] flex-col p-12 relative">
                    {/* Logo */}
                    <motion.div
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="flex items-center gap-4 mb-16"
                    >
                        <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-primary-500/20 to-purple-500/20 p-0.5 shadow-[0_0_30px_rgba(14,165,233,0.3)]">
                            <img src="/logo.png" alt="Nexus AI" className="w-full h-full object-contain rounded-xl" />
                        </div>
                        <div>
                            <h1 className="text-2xl font-black text-white tracking-tight">Nexus AI</h1>
                            <p className="text-xs text-primary-400 font-bold uppercase tracking-widest">Intelligence Platform</p>
                        </div>
                    </motion.div>

                    {/* Main Headline */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                        className="mb-12"
                    >
                        <h2 className="text-5xl xl:text-6xl font-black text-white leading-[1.1] mb-6">
                            Build Anything with
                            <span className="block bg-gradient-to-r from-primary-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                                AI-Powered Teams
                            </span>
                        </h2>
                        <p className="text-xl text-dark-300 max-w-lg leading-relaxed">
                            Deploy 7 specialized AI agents that research, code, test, and deliver
                            production-ready solutions while you focus on what matters.
                        </p>
                    </motion.div>

                    {/* Stats Row */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 }}
                        className="flex gap-8 mb-12"
                    >
                        {stats.map((stat, i) => (
                            <div key={i} className="text-center">
                                <motion.p
                                    initial={{ scale: 0 }}
                                    animate={{ scale: 1 }}
                                    transition={{ delay: 0.4 + i * 0.1, type: "spring" }}
                                    className="text-4xl font-black bg-gradient-to-br from-white to-dark-300 bg-clip-text text-transparent"
                                >
                                    {stat.value}
                                </motion.p>
                                <p className="text-xs text-dark-500 font-bold uppercase tracking-wider mt-1">{stat.label}</p>
                            </div>
                        ))}
                    </motion.div>

                    {/* Feature Showcase Card */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.4 }}
                        className="flex-1 max-w-2xl"
                    >
                        <AnimatePresence mode="wait">
                            <motion.div
                                key={activeFeature}
                                initial={{ opacity: 0, x: 50 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: -50 }}
                                className="glass p-8 rounded-3xl border border-white/10 relative overflow-hidden"
                            >
                                {/* Gradient Background */}
                                <div className={`absolute inset-0 bg-gradient-to-br ${currentFeature.color} opacity-5`} />

                                <div className="relative z-10">
                                    <div className="flex items-center gap-4 mb-6">
                                        <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${currentFeature.color} flex items-center justify-center shadow-lg`}>
                                            <currentFeature.icon className="w-7 h-7 text-white" />
                                        </div>
                                        <div>
                                            <h3 className="text-xl font-bold text-white">{currentFeature.title}</h3>
                                            <p className="text-dark-400 text-sm">{currentFeature.description}</p>
                                        </div>
                                    </div>

                                    {/* Live Demo Animation */}
                                    <div className="bg-black/30 rounded-2xl p-6 border border-white/5">
                                        <div className="flex items-center gap-2 mb-4">
                                            <div className="w-3 h-3 rounded-full bg-red-500" />
                                            <div className="w-3 h-3 rounded-full bg-yellow-500" />
                                            <div className="w-3 h-3 rounded-full bg-green-500" />
                                            <span className="text-xs text-dark-500 ml-2 font-mono">nexus-ai-terminal</span>
                                        </div>
                                        <div className="font-mono text-sm space-y-2">
                                            {currentFeature.demo.map((line, i) => (
                                                <motion.div
                                                    key={i}
                                                    initial={{ opacity: 0.3 }}
                                                    animate={{ opacity: demoLine >= i ? 1 : 0.3 }}
                                                    className="flex items-center gap-3"
                                                >
                                                    <span className={`${demoLine === i ? 'text-primary-400' : 'text-emerald-400'}`}>
                                                        {demoLine > i ? '✓' : demoLine === i ? '▶' : '○'}
                                                    </span>
                                                    <span className={demoLine >= i ? 'text-white' : 'text-dark-500'}>
                                                        {line}
                                                        {demoLine === i && (
                                                            <motion.span
                                                                animate={{ opacity: [1, 0] }}
                                                                transition={{ duration: 0.5, repeat: Infinity }}
                                                                className="text-primary-400"
                                                            >|</motion.span>
                                                        )}
                                                    </span>
                                                </motion.div>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            </motion.div>
                        </AnimatePresence>

                        {/* Feature Indicators */}
                        <div className="flex gap-2 mt-6 justify-center">
                            {features.map((_, i) => (
                                <button
                                    key={i}
                                    onClick={() => { setActiveFeature(i); setDemoLine(0); }}
                                    className={`h-1.5 rounded-full transition-all ${i === activeFeature ? 'w-8 bg-primary-500' : 'w-1.5 bg-dark-600 hover:bg-dark-500'
                                        }`}
                                />
                            ))}
                        </div>
                    </motion.div>

                    {/* How It Works (Bottom) */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.6 }}
                        className="mt-auto pt-8"
                    >
                        <p className="text-xs font-bold text-dark-500 uppercase tracking-widest mb-4">How It Works</p>
                        <div className="flex gap-6">
                            {steps.map((step, i) => (
                                <div key={i} className="flex-1">
                                    <p className="text-primary-500 font-black text-lg mb-1">{step.num}</p>
                                    <p className="text-white font-bold text-sm">{step.title}</p>
                                    <p className="text-dark-500 text-xs">{step.desc}</p>
                                </div>
                            ))}
                        </div>
                    </motion.div>
                </div>

                {/* Right Side - Login Form */}
                <div className="w-full lg:w-[45%] xl:w-[40%] flex items-center justify-center p-6 lg:p-12">
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: 0.1 }}
                        className="w-full max-w-md"
                    >
                        {/* Mobile Logo */}
                        <div className="lg:hidden text-center mb-10">
                            <motion.div
                                initial={{ scale: 0 }}
                                animate={{ scale: 1 }}
                                transition={{ type: "spring", delay: 0.2 }}
                                className="w-20 h-20 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-primary-500/20 to-purple-500/20 p-1 shadow-[0_0_40px_rgba(14,165,233,0.3)]"
                            >
                                <img src="/logo.png" alt="Nexus AI" className="w-full h-full object-contain rounded-xl" />
                            </motion.div>
                            <h1 className="text-3xl font-black text-white mb-2">Nexus AI</h1>
                            <p className="text-dark-400">Multi-Agent Intelligence Platform</p>
                        </div>

                        {/* Login Card */}
                        <div className="glass p-8 lg:p-10 rounded-3xl border border-white/10 relative overflow-hidden">
                            {/* Card Glow */}
                            <div className="absolute -top-20 -right-20 w-40 h-40 bg-primary-500/20 rounded-full blur-3xl" />
                            <div className="absolute -bottom-20 -left-20 w-40 h-40 bg-purple-500/10 rounded-full blur-3xl" />

                            <div className="relative z-10">
                                <div className="text-center mb-8">
                                    <motion.div
                                        initial={{ y: 10, opacity: 0 }}
                                        animate={{ y: 0, opacity: 1 }}
                                        transition={{ delay: 0.3 }}
                                    >
                                        <h2 className="text-2xl lg:text-3xl font-black text-white mb-2">Welcome Back</h2>
                                        <p className="text-dark-400">Sign in to access your AI workspace</p>
                                    </motion.div>
                                </div>

                                <form onSubmit={handleSubmit} className="space-y-5">
                                    <motion.div
                                        initial={{ x: -20, opacity: 0 }}
                                        animate={{ x: 0, opacity: 1 }}
                                        transition={{ delay: 0.4 }}
                                    >
                                        <label className="block text-xs font-bold text-dark-400 uppercase tracking-wider mb-2 ml-1">
                                            Email Address
                                        </label>
                                        <div className="relative">
                                            <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-500" />
                                            <input
                                                type="email"
                                                value={email}
                                                onChange={(e) => setEmail(e.target.value)}
                                                className="w-full pl-12 pr-4 py-4 bg-white/[0.03] border border-white/10 rounded-xl text-white placeholder-dark-500 focus:outline-none focus:border-primary-500/50 focus:bg-white/[0.05] transition-all"
                                                placeholder="you@example.com"
                                                required
                                            />
                                        </div>
                                    </motion.div>

                                    <motion.div
                                        initial={{ x: -20, opacity: 0 }}
                                        animate={{ x: 0, opacity: 1 }}
                                        transition={{ delay: 0.5 }}
                                    >
                                        <label className="block text-xs font-bold text-dark-400 uppercase tracking-wider mb-2 ml-1">
                                            Password
                                        </label>
                                        <div className="relative">
                                            <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-500" />
                                            <input
                                                type={showPassword ? "text" : "password"}
                                                value={password}
                                                onChange={(e) => setPassword(e.target.value)}
                                                className="w-full pl-12 pr-12 py-4 bg-white/[0.03] border border-white/10 rounded-xl text-white placeholder-dark-500 focus:outline-none focus:border-primary-500/50 focus:bg-white/[0.05] transition-all"
                                                placeholder="••••••••"
                                                required
                                            />
                                            <button
                                                type="button"
                                                onClick={() => setShowPassword(!showPassword)}
                                                className="absolute right-4 top-1/2 -translate-y-1/2 text-dark-500 hover:text-white transition-colors"
                                            >
                                                {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                                            </button>
                                        </div>
                                    </motion.div>

                                    <motion.div
                                        initial={{ y: 20, opacity: 0 }}
                                        animate={{ y: 0, opacity: 1 }}
                                        transition={{ delay: 0.6 }}
                                    >
                                        <motion.button
                                            type="submit"
                                            disabled={isLoading}
                                            whileHover={{ scale: 1.02, boxShadow: "0 20px 40px rgba(14,165,233,0.3)" }}
                                            whileTap={{ scale: 0.98 }}
                                            className="w-full py-4 bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-400 hover:to-primary-500 text-white font-bold text-lg rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_10px_30px_rgba(14,165,233,0.2)] flex items-center justify-center gap-3"
                                        >
                                            {isLoading ? (
                                                <>
                                                    <Loader2 className="w-5 h-5 animate-spin" />
                                                    Signing in...
                                                </>
                                            ) : (
                                                <>
                                                    Sign In
                                                    <ArrowRight className="w-5 h-5" />
                                                </>
                                            )}
                                        </motion.button>
                                    </motion.div>
                                </form>

                                <motion.div
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    transition={{ delay: 0.7 }}
                                    className="mt-8 text-center"
                                >
                                    <p className="text-dark-400">
                                        Don't have an account?{' '}
                                        <Link to="/signup" className="text-primary-400 hover:text-primary-300 font-bold transition-colors">
                                            Create one free
                                        </Link>
                                    </p>
                                </motion.div>

                                {/* Trust Badges */}
                                <motion.div
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    transition={{ delay: 0.8 }}
                                    className="mt-8 pt-6 border-t border-white/5"
                                >
                                    <div className="flex items-center justify-center gap-6 text-dark-500">
                                        <div className="flex items-center gap-2">
                                            <Shield className="w-4 h-4" />
                                            <span className="text-xs font-medium">Secure</span>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <Zap className="w-4 h-4" />
                                            <span className="text-xs font-medium">Fast</span>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <Star className="w-4 h-4" />
                                            <span className="text-xs font-medium">Trusted</span>
                                        </div>
                                    </div>
                                </motion.div>
                            </div>
                        </div>

                        {/* Footer */}
                        <motion.p
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.9 }}
                            className="text-center text-dark-600 text-xs mt-6"
                        >
                            By signing in, you agree to our Terms & Privacy Policy
                        </motion.p>
                    </motion.div>
                </div>
            </div>
        </div>
    );
}
