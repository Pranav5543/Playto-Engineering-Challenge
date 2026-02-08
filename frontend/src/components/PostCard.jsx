import React, { useState } from 'react';
import { Heart, MessageSquare, Share2, User } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../api';
import CommentSection from './CommentSection';

export default function PostCard({ post: initialPost, onAuthRequired }) {
    const [post, setPost] = useState(initialPost);
    const [showComments, setShowComments] = useState(false);
    const [isLiking, setIsLiking] = useState(false);

    const handleLike = async () => {
        try {
            setIsLiking(true);
            const res = await api.post(`posts/${post.id}/like/`);
            setPost(prev => ({
                ...prev,
                is_liked: res.data.liked,
                likes_count: res.data.liked ? prev.likes_count + 1 : prev.likes_count - 1
            }));
        } catch (err) {
            if (err.response?.status === 401) onAuthRequired();
            console.error(err);
        } finally {
            setIsLiking(false);
        }
    };

    return (
        <div className="card space-y-4">
            <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center text-slate-400">
                    <User size={20} />
                </div>
                <div>
                    <div className="font-bold text-slate-200">{post.author.username}</div>
                    <div className="text-xs text-slate-500">{new Date(post.created_at).toLocaleDateString()}</div>
                </div>
            </div>

            <p className="text-slate-300 leading-relaxed">
                {post.content}
            </p>

            <div className="flex items-center gap-6 pt-2 border-t border-slate-800/50">
                <button
                    onClick={handleLike}
                    disabled={isLiking}
                    className={`flex items-center gap-2 group transition-colors ${post.is_liked ? 'text-rose-500' : 'text-slate-400 hover:text-rose-400'}`}
                >
                    <motion.div whileTap={{ scale: 1.5 }}>
                        <Heart size={20} fill={post.is_liked ? 'currentColor' : 'none'} />
                    </motion.div>
                    <span className="text-sm font-medium">{post.likes_count}</span>
                </button>

                <button
                    onClick={() => setShowComments(!showComments)}
                    className="flex items-center gap-2 text-slate-400 hover:text-indigo-400 transition-colors"
                >
                    <MessageSquare size={20} />
                    <span className="text-sm font-medium">{post.comments_count} Comments</span>
                </button>

                <button className="flex items-center gap-2 text-slate-400 hover:text-slate-200 ml-auto">
                    <Share2 size={18} />
                </button>
            </div>

            <AnimatePresence>
                {showComments && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="overflow-hidden"
                    >
                        <CommentSection postId={post.id} onAuthRequired={onAuthRequired} />
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
