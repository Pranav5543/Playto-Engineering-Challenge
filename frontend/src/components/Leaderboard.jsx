import React, { useEffect, useState } from 'react';
import { Trophy, Award, TrendingUp } from 'lucide-react';
import api from '../api';

export default function Leaderboard() {
    const [topUsers, setTopUsers] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchLeaderboard = async () => {
            try {
                const res = await api.get('leaderboard/');
                setTopUsers(res.data);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchLeaderboard();
        const interval = setInterval(fetchLeaderboard, 60000); // Update every minute
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="card space-y-4 sticky top-24">
            <div className="flex items-center gap-2 pb-2 border-b border-slate-800">
                <Trophy className="text-yellow-500" size={20} />
                <h2 className="font-bold text-lg">Top Authors</h2>
                <span className="text-[10px] bg-slate-800 text-slate-400 px-2 py-1 rounded-full ml-auto uppercase tracking-wider">Last 24h</span>
            </div>

            <div className="space-y-4">
                {loading ? (
                    [1, 2, 3].map(i => (
                        <div key={i} className="flex items-center gap-3 animate-pulse">
                            <div className="w-8 h-8 rounded-full bg-slate-800" />
                            <div className="flex-1 space-y-2">
                                <div className="h-3 bg-slate-800 rounded w-20" />
                                <div className="h-2 bg-slate-800 rounded w-12" />
                            </div>
                        </div>
                    ))
                ) : topUsers.length > 0 ? (
                    topUsers.map((user, index) => (
                        <div key={user.username} className="flex items-center gap-3 group">
                            <div className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold text-sm
                ${index === 0 ? 'bg-yellow-500/20 text-yellow-500' :
                                    index === 1 ? 'bg-slate-300/20 text-slate-300' :
                                        index === 2 ? 'bg-amber-600/20 text-amber-600' : 'bg-slate-800 text-slate-400'}`}>
                                {index + 1}
                            </div>
                            <div className="flex-1">
                                <div className="font-medium text-slate-200 group-hover:text-white transition-colors">
                                    {user.username}
                                </div>
                                <div className="text-xs text-slate-500 flex items-center gap-1">
                                    <TrendingUp size={10} />
                                    {user.karma} Karma earned
                                </div>
                            </div>
                            {index === 0 && <Award size={16} className="text-yellow-500" />}
                        </div>
                    ))
                ) : (
                    <div className="text-center py-4 text-slate-500 text-sm">
                        No activity in the last 24h
                    </div>
                )}
            </div>
        </div>
    );
}
