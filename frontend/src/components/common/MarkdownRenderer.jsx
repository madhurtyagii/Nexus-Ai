import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { motion, AnimatePresence } from 'framer-motion';
import { useState } from 'react';
import { Copy, Check, Code2 } from 'lucide-react';

/**
 * Premium Markdown Renderer with Copy Button
 * Renders AI output with beautiful, ChatGPT-quality styling.
 * Supports: Bold, Italic, Headers, Lists, Code Blocks with Copy, Links, Tables
 */

// Code Block with Copy Button Component
function CodeBlock({ children, className }) {
    const [copied, setCopied] = useState(false);

    // Extract language from className (e.g., "language-python" -> "python")
    const match = /language-(\w+)/.exec(className || '');
    const language = match ? match[1] : 'code';

    // Get the raw text content
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

    return (
        <div className="relative my-4 group">
            {/* Header with language and copy button */}
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

                {/* Copy Button */}
                <motion.button
                    onClick={handleCopy}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium transition-all duration-200 ${copied
                            ? 'bg-green-500/20 text-green-400'
                            : 'bg-dark-600 text-dark-300 hover:bg-dark-500 hover:text-white'
                        }`}
                >
                    <AnimatePresence mode="wait">
                        {copied ? (
                            <motion.div
                                key="check"
                                initial={{ scale: 0 }}
                                animate={{ scale: 1 }}
                                exit={{ scale: 0 }}
                                className="flex items-center gap-1"
                            >
                                <Check size={12} />
                                <span>Copied!</span>
                            </motion.div>
                        ) : (
                            <motion.div
                                key="copy"
                                initial={{ scale: 0 }}
                                animate={{ scale: 1 }}
                                exit={{ scale: 0 }}
                                className="flex items-center gap-1"
                            >
                                <Copy size={12} />
                                <span>Copy</span>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </motion.button>
            </div>

            {/* Code content */}
            <pre className="bg-dark-800 border border-t-0 border-dark-600 rounded-b-lg py-4 px-4 overflow-x-auto">
                <code className="text-sm font-mono text-dark-100 leading-relaxed">
                    {children}
                </code>
            </pre>
        </div>
    );
}

export default function MarkdownRenderer({ content, className = '' }) {
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
                }}
            >
                {content}
            </ReactMarkdown>
        </motion.div>
    );
}

