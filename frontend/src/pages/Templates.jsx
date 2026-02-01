import React from 'react';

const Templates = () => {
    return (
        <div className="min-h-screen bg-dark-900 pt-20 px-4 pb-12">
            <div className="max-w-7xl mx-auto">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-white mb-2">Agent Templates</h1>
                    <p className="text-dark-400">Browse and manage specialized AI agent configurations.</p>
                </div>

                <div className="bg-dark-800 rounded-2xl border border-dark-700 p-12 text-center">
                    <div className="w-20 h-20 bg-dark-700 rounded-full flex items-center justify-center mx-auto mb-6">
                        <span className="text-4xl">🤖</span>
                    </div>
                    <h2 className="text-2xl font-semibold text-white mb-2">Coming Soon</h2>
                    <p className="text-dark-400 max-w-md mx-auto">
                        We're building a library of pre-configured agent templates to help you get started faster.
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Templates;
