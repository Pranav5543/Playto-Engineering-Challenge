import React from 'react';
import { Layout, Users, PlusCircle, LogIn } from 'lucide-react';

export default function Navbar({ user, onOpenAuth, onNewPost, onLogout }) {
    return (
        <nav className="fixed top-0 left-0 right-0 z-50 glass border-b border-slate-800/50">
            <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-500/20">
                        <Layout className="text-white w-6 h-6" />
                    </div>
                    <span className="text-xl font-bold bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
                        Playto Community
                    </span>
                </div>

                <div className="flex items-center gap-4">
                    {user ? (
                        <div className="flex items-center gap-3">
                            <span className="text-slate-400 text-sm hidden sm:block">Welcome, <span className="text-white font-medium">{user.username}</span></span>
                            <button
                                onClick={onNewPost}
                                className="btn-primary flex items-center gap-2"
                            >
                                <PlusCircle size={18} />
                                <span className="hidden sm:inline">New Post</span>
                            </button>
                            <button
                                onClick={onLogout}
                                className="btn-ghost flex items-center gap-2 text-sm"
                                title="Logout"
                            >
                                <LogIn size={16} className="rotate-180" />
                                <span className="hidden sm:inline">Logout</span>
                            </button>
                        </div>
                    ) : (
                        <button
                            onClick={onOpenAuth}
                            className="btn-primary flex items-center gap-2"
                        >
                            <LogIn size={18} />
                            Login
                        </button>
                    )}
                </div>
            </div>
        </nav>
    );
}
