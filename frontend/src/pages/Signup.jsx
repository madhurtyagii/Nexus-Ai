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
    CheckCircle2,
    Cpu,
    Eye,
    EyeOff,
    Loader2,
    Mail,
    Lock,
    User,
    Rocket,
    Gift
} from 'lucide-react';

// Floating particles background
const FloatingParticles = () => {
    const particles = Array.from({ length: 25 }, (_, i) => ({
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
                    className="absolute rounded-full bg-purple-500/20"
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

// Benefits
const benefits = [
    { icon: Brain, text: "7 Specialized AI Agents" },
    { icon: Zap, text: "Real-time Processing" },
    { icon: Shield, text: "Enterprise Security" },
    { icon: Code, text: "Full-Stack Generation" },
    { icon: FileText, text: "Document Intelligence" },
    { icon: Users, text: "Team Collaboration" }
];

// What you get highlights
const highlights = [
    { icon: Rocket, title: "Instant Access", desc: "Start building in seconds" },
    { icon: Gift, title: "Free Forever", desc: "Generous free tier included" },
    { icon: Shield, title: "Enterprise Ready", desc: "Bank-level security" }
];

export default function Signup() {
    const [email, setEmail] = useState('');
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const { signup } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (password !== confirmPassword) {
            setError('Passwords do not match');
            return;
        }
        if (password.length < 6) {
            setError('Password must be at least 6 characters');
            return;
        }
        if (username.length < 3) {
            setError('Username must be at least 3 characters');
            return;
        }

        setIsLoading(true);
        const result = await signup(email, username, password);
        if (result.success) {
            navigate('/dashboard');
        }
        setIsLoading(false);
    };

    return (
        <div className="min-h-screen bg-dark-950 relative overflow-hidden">
            {/* Background Effects */}
            <FloatingParticles />
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_left,rgba(139,92,246,0.15),transparent_50%)]" />
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_right,rgba(14,165,233,0.1),transparent_50%)]" />

            {/* Grid Pattern */}
            <div className="absolute inset-0 opacity-[0.02]" style={{
                backgroundImage: 'linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)',
                backgroundSize: '60px 60px'
            }} />

            <div className="relative z-10 min-h-screen flex">
                {/* Left Side - Benefits Showcase */}
                <div className="hidden lg:flex lg:w-[55%] xl:w-[60%] flex-col p-12 relative">
                    {/* Logo */}
                    <motion.div
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="flex items-center gap-4 mb-16"
                    >
                        <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-purple-500/20 to-primary-500/20 p-0.5 shadow-[0_0_30px_rgba(139,92,246,0.3)]">
                            <img src="/logo.png" alt="Nexus AI" className="w-full h-full object-contain rounded-xl" />
                        </div>
                        <div>
                            <h1 className="text-2xl font-black text-white tracking-tight">Nexus AI</h1>
                            <p className="text-xs text-purple-400 font-bold uppercase tracking-widest">Intelligence Platform</p>
                        </div>
                    </motion.div>

                    {/* Main Headline */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                        className="mb-12"
                    >
                        <div className="inline-flex items-center gap-2 px-4 py-2 bg-purple-500/10 rounded-full border border-purple-500/20 mb-6">
                            <Gift className="w-4 h-4 text-purple-400" />
                            <span className="text-sm font-bold text-purple-400">Free Forever Plan Available</span>
                        </div>
                        <h2 className="text-5xl xl:text-6xl font-black text-white leading-[1.1] mb-6">
                            Start Building
                            <span className="block bg-gradient-to-r from-purple-400 via-pink-400 to-primary-400 bg-clip-text text-transparent">
                                The Future Today
                            </span>
                        </h2>
                        <p className="text-xl text-dark-300 max-w-lg leading-relaxed">
                            Join thousands of developers using AI agents to build faster,
                            smarter, and more efficiently than ever before.
                        </p>
                    </motion.div>

                    {/* Benefits Grid */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 }}
                        className="grid grid-cols-2 gap-4 mb-12"
                    >
                        {benefits.map((benefit, i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: 0.4 + i * 0.1 }}
                                className="flex items-center gap-3 p-4 rounded-xl bg-white/[0.02] border border-white/5 hover:bg-white/[0.05] transition-colors"
                            >
                                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500/20 to-primary-500/20 flex items-center justify-center">
                                    <benefit.icon className="w-5 h-5 text-purple-400" />
                                </div>
                                <span className="text-white font-medium">{benefit.text}</span>
                            </motion.div>
                        ))}
                    </motion.div>

                    {/* What You Get */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.6 }}
                        className="mt-auto"
                    >
                        <p className="text-xs font-bold text-dark-500 uppercase tracking-widest mb-4">What You Get</p>
                        <div className="grid grid-cols-3 gap-3">
                            {highlights.map((item, i) => (
                                <motion.div
                                    key={i}
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: 0.7 + i * 0.1 }}
                                    className="glass p-4 rounded-xl border border-white/10 text-center"
                                >
                                    <item.icon className="w-6 h-6 text-purple-400 mx-auto mb-2" />
                                    <p className="text-white font-bold text-sm">{item.title}</p>
                                    <p className="text-dark-500 text-xs mt-1">{item.desc}</p>
                                </motion.div>
                            ))}
                        </div>
                    </motion.div>
                </div>

                {/* Right Side - Signup Form */}
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
                                className="w-20 h-20 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-purple-500/20 to-primary-500/20 p-1 shadow-[0_0_40px_rgba(139,92,246,0.3)]"
                            >
                                <img src="/logo.png" alt="Nexus AI" className="w-full h-full object-contain rounded-xl" />
                            </motion.div>
                            <h1 className="text-3xl font-black text-white mb-2">Nexus AI</h1>
                            <p className="text-dark-400">Create your AI workspace</p>
                        </div>

                        {/* Signup Card */}
                        <div className="glass p-8 lg:p-10 rounded-3xl border border-white/10 relative overflow-hidden">
                            {/* Card Glow */}
                            <div className="absolute -top-20 -right-20 w-40 h-40 bg-purple-500/20 rounded-full blur-3xl" />
                            <div className="absolute -bottom-20 -left-20 w-40 h-40 bg-primary-500/10 rounded-full blur-3xl" />

                            <div className="relative z-10">
                                <div className="text-center mb-8">
                                    <motion.div
                                        initial={{ y: 10, opacity: 0 }}
                                        animate={{ y: 0, opacity: 1 }}
                                        transition={{ delay: 0.3 }}
                                    >
                                        <h2 className="text-2xl lg:text-3xl font-black text-white mb-2">Get Started Free</h2>
                                        <p className="text-dark-400">Create your account in seconds</p>
                                    </motion.div>
                                </div>

                                {error && (
                                    <motion.div
                                        initial={{ opacity: 0, y: -10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm font-medium"
                                    >
                                        {error}
                                    </motion.div>
                                )}

                                <form onSubmit={handleSubmit} className="space-y-4">
                                    <motion.div
                                        initial={{ x: -20, opacity: 0 }}
                                        animate={{ x: 0, opacity: 1 }}
                                        transition={{ delay: 0.4 }}
                                    >
                                        <label className="block text-xs font-bold text-dark-400 uppercase tracking-wider mb-2 ml-1">
                                            Email
                                        </label>
                                        <div className="relative">
                                            <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-500" />
                                            <input
                                                type="email"
                                                value={email}
                                                onChange={(e) => setEmail(e.target.value)}
                                                className="w-full pl-12 pr-4 py-4 bg-white/[0.03] border border-white/10 rounded-xl text-white placeholder-dark-500 focus:outline-none focus:border-purple-500/50 focus:bg-white/[0.05] transition-all"
                                                placeholder="you@example.com"
                                                required
                                            />
                                        </div>
                                    </motion.div>

                                    <motion.div
                                        initial={{ x: -20, opacity: 0 }}
                                        animate={{ x: 0, opacity: 1 }}
                                        transition={{ delay: 0.45 }}
                                    >
                                        <label className="block text-xs font-bold text-dark-400 uppercase tracking-wider mb-2 ml-1">
                                            Username
                                        </label>
                                        <div className="relative">
                                            <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-500" />
                                            <input
                                                type="text"
                                                value={username}
                                                onChange={(e) => setUsername(e.target.value)}
                                                className="w-full pl-12 pr-4 py-4 bg-white/[0.03] border border-white/10 rounded-xl text-white placeholder-dark-500 focus:outline-none focus:border-purple-500/50 focus:bg-white/[0.05] transition-all"
                                                placeholder="johndoe"
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
                                                className="w-full pl-12 pr-12 py-4 bg-white/[0.03] border border-white/10 rounded-xl text-white placeholder-dark-500 focus:outline-none focus:border-purple-500/50 focus:bg-white/[0.05] transition-all"
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
                                        initial={{ x: -20, opacity: 0 }}
                                        animate={{ x: 0, opacity: 1 }}
                                        transition={{ delay: 0.55 }}
                                    >
                                        <label className="block text-xs font-bold text-dark-400 uppercase tracking-wider mb-2 ml-1">
                                            Confirm Password
                                        </label>
                                        <div className="relative">
                                            <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-500" />
                                            <input
                                                type={showPassword ? "text" : "password"}
                                                value={confirmPassword}
                                                onChange={(e) => setConfirmPassword(e.target.value)}
                                                className="w-full pl-12 pr-4 py-4 bg-white/[0.03] border border-white/10 rounded-xl text-white placeholder-dark-500 focus:outline-none focus:border-purple-500/50 focus:bg-white/[0.05] transition-all"
                                                placeholder="••••••••"
                                                required
                                            />
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
                                            whileHover={{ scale: 1.02, boxShadow: "0 20px 40px rgba(139,92,246,0.3)" }}
                                            whileTap={{ scale: 0.98 }}
                                            className="w-full py-4 bg-gradient-to-r from-purple-500 to-primary-500 hover:from-purple-400 hover:to-primary-400 text-white font-bold text-lg rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_10px_30px_rgba(139,92,246,0.2)] flex items-center justify-center gap-3 mt-2"
                                        >
                                            {isLoading ? (
                                                <>
                                                    <Loader2 className="w-5 h-5 animate-spin" />
                                                    Creating account...
                                                </>
                                            ) : (
                                                <>
                                                    <Rocket className="w-5 h-5" />
                                                    Create Account
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
                                        Already have an account?{' '}
                                        <Link to="/login" className="text-purple-400 hover:text-purple-300 font-bold transition-colors">
                                            Sign in
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
                                            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                                            <span className="text-xs font-medium">No Credit Card</span>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <Zap className="w-4 h-4 text-yellow-400" />
                                            <span className="text-xs font-medium">Instant Setup</span>
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
                            By signing up, you agree to our Terms & Privacy Policy
                        </motion.p>
                    </motion.div>
                </div>
            </div>
        </div>
    );
}
