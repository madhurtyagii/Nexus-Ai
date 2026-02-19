import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { motion, AnimatePresence } from 'framer-motion';
import { useState } from 'react';
import { Copy, Check, Code2, Play, Terminal, XCircle } from 'lucide-react';
import api from '../../services/api';

/**
 * Premium Markdown Renderer with Copy Button
 * Renders AI output with beautiful, ChatGPT-quality styling.
 * Supports: Bold, Italic, Headers, Lists, Code Blocks with Copy, Links, Tables
 */

// Code Block with Copy Button Component
function CodeBlock({ children, className }) {
    const [copied, setCopied] = useState(false);
    const [executionOutput, setExecutionOutput] = useState(null);
    const [isExecuting, setIsExecuting] = useState(false);

    // Extract language from className (e.g., "language-python" -> "python")
    const match = /language-(\w+)/.exec(className || '');
    const language = match ? match[1] : 'code';
    const isRunnable = ['javascript', 'js', 'python', 'py'].includes(language.toLowerCase());

    const codeString = String(children).replace(/\n$/, '');

    const handleCopy = async () => {
        try {
            await navigator.clipboard.writeText(codeString);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error('Failed to copy:', err);
        }
    };

    const handleRun = async () => {
        setIsExecuting(true);
        setExecutionOutput({ type: 'info', content: 'Initializing sandbox...' });

        if (['javascript', 'js'].includes(language.toLowerCase())) {
            try {
                // Buffer to capture console.log
                let logs = [];
                const originalLog = console.log;
                console.log = (...args) => {
                    logs.push(args.map(a => typeof a === 'object' ? JSON.stringify(a, null, 2) : String(a)).join(' '));
                    originalLog(...args);
                };

                // Execute code
                // eslint-disable-next-line no-new-func
                const result = new Function(codeString)();

                // Restore console
                console.log = originalLog;

                const finalOutput = logs.length > 0 ? logs.join('\n') : (result !== undefined ? String(result) : 'Done (No output)');
                setExecutionOutput({ success: true, stdout: finalOutput, type: 'success' });
            } catch (err) {
                setExecutionOutput({ success: false, error: err.message, type: 'error' });
            } finally {
                setIsExecuting(false);
            }
        } else if (['python', 'py'].includes(language.toLowerCase())) {
            try {
                const response = await api.post('/sandbox/python', {
                    language: language.toLowerCase() === 'python' || language.toLowerCase() === 'py' ? 'python' : language,
                    code: codeString,
                    timeout: 30
                });

                setExecutionOutput({
                    success: response.data.success,
                    stdout: response.data.stdout,
                    stderr: response.data.stderr,
                    error: response.data.error,
                    time: response.data.execution_time
                });
            } catch (error) {
                console.error('Execution error:', error);
                setExecutionOutput({
                    success: false,
                    error: error.response?.data?.detail || error.message || 'Execution failed'
                });
            } finally {
                setIsExecuting(false);
            }
        }
    };

    const getOutputContent = () => {
        if (!executionOutput) return null;

        if (executionOutput.success) {
            return executionOutput.stdout || 'Execution successful (no output).';
        } else {
            return executionOutput.stderr || executionOutput.error || 'Execution failed.';
        }
    };

    const getOutputTypeClass = () => {
        if (!executionOutput) return 'text-blue-400'; // Default for initial state if needed

        if (executionOutput.type === 'info') return 'text-blue-400';
        if (executionOutput.success) return 'text-emerald-400';
        return 'text-red-400';
    };

    return (
        <div className="relative my-4 group">
            {/* Header with language and actions */}
            <div className="flex items-center justify-between px-4 py-2 bg-dark-700 rounded-t-lg border-b border-dark-600">
                <div className="flex items-center gap-2">
                    <div className="flex gap-1.5">
                        <div className="w-3 h-3 rounded-full bg-red-500/70" />
                        <div className="w-3 h-3 rounded-full bg-yellow-500/70" />
                        <div className="w-3 h-3 rounded-full bg-green-500/70" />
                    </div>
                    <span className="text-xs font-medium text-dark-400 uppercase tracking-wide ml-2">
                        {language}
                    </span>
                </div>

                <div className="flex items-center gap-2">
                    {/* Run Button */}
                    {isRunnable && (
                        <motion.button
                            onClick={handleRun}
                            disabled={isExecuting}
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium transition-all duration-200 border border-primary-500/30 ${isExecuting
                                ? 'bg-primary-500/10 text-primary-400 animate-pulse'
                                : 'bg-primary-500/10 text-primary-400 hover:bg-primary-500/20 active:bg-primary-500/30'
                                }`}
                        >
                            <Play size={12} fill="currentColor" />
                            <span>{isExecuting ? 'Running...' : 'Run'}</span>
                        </motion.button>
                    )}

                    {/* Copy Button */}
                    <motion.button
                        onClick={handleCopy}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium transition-all duration-200 ${copied
                            ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                            : 'bg-dark-600 text-dark-300 hover:bg-dark-500 hover:text-white border border-dark-500/30'
                            }`}
                    >
                        <AnimatePresence mode="wait">
                            {copied ? (
                                <motion.div key="check" initial={{ scale: 0 }} animate={{ scale: 1 }} exit={{ scale: 0 }} className="flex items-center gap-1">
                                    <Check size={12} />
                                    <span>Copied!</span>
                                </motion.div>
                            ) : (
                                <motion.div key="copy" initial={{ scale: 0 }} animate={{ scale: 1 }} exit={{ scale: 0 }} className="flex items-center gap-1">
                                    <Copy size={12} />
                                    <span>Copy</span>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </motion.button>
                </div>
            </div>

            {/* Code content */}
            <pre className={`bg-dark-800 border border-t-0 border-dark-600 ${executionOutput ? '' : 'rounded-b-lg'} py-4 px-4 overflow-x-auto transition-all`}>
                <code className="text-sm font-mono text-dark-100 leading-relaxed">
                    {children}
                </code>
            </pre>

            {/* Execution Output (Live Sandbox) */}
            <AnimatePresence>
                {executionOutput && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="overflow-hidden bg-black/40 border-x border-b border-dark-600 rounded-b-lg"
                    >
                        <div className="flex items-center justify-between px-4 py-1.5 bg-dark-800/50 border-b border-dark-600/30">
                            <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-wider text-dark-400">
                                <Terminal size={10} />
                                <span>Output</span>
                            </div>
                            <button
                                onClick={() => setExecutionOutput(null)}
                                className="text-dark-500 hover:text-white transition-colors"
                            >
                                <XCircle size={12} />
                            </button>
                        </div>
                        <div className={`p-4 font-mono text-sm whitespace-pre-wrap ${getOutputTypeClass()}`}>
                            {getOutputContent()}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}

export default function MarkdownRenderer({ content, onImageClick, className = '' }) {
    if (!content) return null;

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className={`markdown-renderer ${className}`}
        >
            <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                    // Headers
                    h1: ({ children }) => (
                        <h1 className="text-2xl font-bold text-white mt-6 mb-3 pb-2 border-b border-dark-700">
                            {children}
                        </h1>
                    ),
                    h2: ({ children }) => (
                        <h2 className="text-xl font-bold text-white mt-5 mb-2">
                            {children}
                        </h2>
                    ),
                    h3: ({ children }) => (
                        <h3 className="text-lg font-semibold text-dark-100 mt-4 mb-2">
                            {children}
                        </h3>
                    ),
                    h4: ({ children }) => (
                        <h4 className="text-base font-semibold text-dark-200 mt-3 mb-1">
                            {children}
                        </h4>
                    ),

                    // Paragraphs
                    p: ({ children }) => (
                        <p className="text-dark-200 leading-relaxed mb-4">
                            {children}
                        </p>
                    ),

                    // Bold & Italic
                    strong: ({ children }) => (
                        <strong className="font-bold text-white">{children}</strong>
                    ),
                    em: ({ children }) => (
                        <em className="italic text-dark-100">{children}</em>
                    ),

                    // Lists
                    ul: ({ children }) => (
                        <ul className="list-disc list-inside space-y-2 mb-4 ml-2 text-dark-200">
                            {children}
                        </ul>
                    ),
                    ol: ({ children }) => (
                        <ol className="list-decimal list-inside space-y-2 mb-4 ml-2 text-dark-200">
                            {children}
                        </ol>
                    ),
                    li: ({ children }) => (
                        <li className="text-dark-200 leading-relaxed">
                            <span className="text-dark-200">{children}</span>
                        </li>
                    ),

                    // Code - Now with Copy Button!
                    code: ({ inline, children, className }) => {
                        if (inline) {
                            return (
                                <code className="bg-dark-700 text-primary-400 px-1.5 py-0.5 rounded text-sm font-mono">
                                    {children}
                                </code>
                            );
                        }
                        return (
                            <CodeBlock className={className}>
                                {children}
                            </CodeBlock>
                        );
                    },
                    pre: ({ children }) => <>{children}</>,

                    // Blockquotes
                    blockquote: ({ children }) => (
                        <blockquote className="border-l-4 border-primary-500 pl-4 py-2 my-4 bg-primary-500/5 rounded-r-lg">
                            <div className="text-dark-200 italic">{children}</div>
                        </blockquote>
                    ),

                    // Links
                    a: ({ href, children }) => (
                        <a
                            href={href}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-primary-400 hover:text-primary-300 underline underline-offset-2 transition-colors"
                        >
                            {children}
                        </a>
                    ),

                    // Horizontal Rule
                    hr: () => (
                        <hr className="border-dark-600 my-6" />
                    ),

                    // Tables
                    table: ({ children }) => (
                        <div className="overflow-x-auto my-4">
                            <table className="w-full border-collapse border border-dark-600 rounded-lg overflow-hidden">
                                {children}
                            </table>
                        </div>
                    ),
                    thead: ({ children }) => (
                        <thead className="bg-dark-700">{children}</thead>
                    ),
                    th: ({ children }) => (
                        <th className="px-4 py-2 text-left text-white font-semibold border-b border-dark-600">
                            {children}
                        </th>
                    ),
                    td: ({ children }) => (
                        <td className="px-4 py-2 text-dark-200 border-b border-dark-700">
                            {children}
                        </td>
                    ),
                    tr: ({ children }) => (
                        <tr className="hover:bg-dark-700/50 transition-colors">{children}</tr>
                    ),

                    // Task Lists (GFM)
                    input: ({ checked }) => (
                        <input
                            type="checkbox"
                            checked={checked}
                            readOnly
                            className="mr-2 accent-primary-500"
                        />
                    ),

                    // Images - Support relative paths from backend
                    img: ({ src, alt }) => {
                        let fullSrc = src;
                        if (src && (src.startsWith('/storage') || src.startsWith('/uploads'))) {
                            const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
                            fullSrc = `${baseUrl}${src}`;
                        }
                        return (
                            <motion.div
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                onClick={() => onImageClick?.(fullSrc)}
                                className={`my-4 overflow-hidden rounded-xl border border-dark-700 bg-dark-800 shadow-lg group ${onImageClick ? 'cursor-zoom-in' : ''}`}
                            >
                                <img
                                    src={fullSrc}
                                    alt={alt || 'AI Generated Content'}
                                    className="w-full h-auto object-cover max-h-[512px] hover:scale-[1.02] transition-transform duration-500"
                                    loading="lazy"
                                />
                                {alt && (
                                    <div className="px-4 py-2 text-xs text-dark-400 bg-dark-700/50 italic border-t border-dark-700">
                                        {alt}
                                    </div>
                                )}
                            </motion.div>
                        );
                    }
                }}
            >
                {content}
            </ReactMarkdown>
        </motion.div>
    );
}

