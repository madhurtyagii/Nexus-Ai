import React from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/layout/Navbar';
import Sidebar from '../components/layout/Sidebar';
import './Help.css';

export default function Help() {
    const navigate = useNavigate();

    const sections = [
        {
            title: '🏗️ Project Orchestration',
            content: 'Nexus AI uses a Multi-Agent system to plan and execute projects. You can create projects using built-in templates or let the ManagerAgent plan one dynamically from your description.'
        },
        {
            title: '📋 Workflow Templates',
            content: 'Choose from 5 industry-standard templates (Software Dev, Marketing, Data Analysis, etc.) to instantly initialize complex project structures.'
        },
        {
            title: '📤 Multi-Format Exports',
            content: 'Download your project details and outputs in PDF, Word (DOCX), Markdown, or JSON. Perfect for reporting and sharing results.'
        },
        {
            title: '📁 File Management',
            content: 'Upload PDFs, CSVs, and images to your projects. The agents will automatically process these files to inform their work.'
        },
        {
            title: '📌 Organization',
            content: 'Use Pinning to keep important projects at the top, and Archiving to hide completed or old projects without deleting them.'
        }
    ];

    return (
        <div className="min-h-screen bg-dark-900">
            <Navbar />
            <div className="flex">
                <Sidebar />
                <main className="flex-1 p-6 lg:p-8">
                    <div className="help-container max-w-4xl mx-auto">
                        <section className="help-header mb-12">
                            <h1 className="text-4xl font-bold text-white mb-4">Nexus AI Help Center</h1>
                            <p className="text-dark-400 text-lg">
                                Master the autonomous multi-agent workspace and supercharge your productivity.
                            </p>
                        </section>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
                            {sections.map((section, i) => (
                                <div key={i} className="help-card p-6 rounded-2xl bg-dark-800 border border-dark-700 hover:border-primary-500/50 transition-all">
                                    <h3 className="text-xl font-semibold text-white mb-3">{section.title}</h3>
                                    <p className="text-dark-400 leading-relaxed text-sm">
                                        {section.content}
                                    </p>
                                </div>
                            ))}
                        </div>

                        <section className="quick-tips p-8 rounded-3xl bg-gradient-to-br from-primary-500/10 to-purple-500/10 border border-primary-500/20">
                            <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
                                💡 Pro Tips
                            </h2>
                            <ul className="space-y-4 text-dark-300">
                                <li className="flex gap-4">
                                    <span className="text-primary-400 font-bold">01.</span>
                                    <span>Use **AI Planning** for custom projects where you want the agents to brainstorm the phases.</span>
                                </li>
                                <li className="flex gap-4">
                                    <span className="text-primary-400 font-bold">02.</span>
                                    <span>Check the **Activity Feed** in Project Detail to see exactly what your agents are doing in real-time.</span>
                                </li>
                                <li className="flex gap-4">
                                    <span className="text-primary-400 font-bold">03.</span>
                                    <span>Tags help you filter large project lists. Type a tag and press Enter to add it instantly.</span>
                                </li>
                            </ul>
                        </section>

                        <div className="mt-12 text-center">
                            <button
                                onClick={() => navigate('/dashboard')}
                                className="btn-primary px-8"
                            >
                                Back to Dashboard
                            </button>
                        </div>
                    </div>
                </main>
            </div>
        </div>
    );
}
