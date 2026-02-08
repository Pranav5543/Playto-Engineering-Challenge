import React, { useState, useEffect } from 'react';
import { Heart, Reply, Send } from 'lucide-react';
import api from '../api';

const CommentItem = ({ comment, depth = 0, onReplyAdded, onAuthRequired }) => {
    const [isLiked, setIsLiked] = useState(comment.is_liked);
    const [likesCount, setLikesCount] = useState(comment.likes_count);
    const [showReply, setShowReply] = useState(false);
    const [replyText, setReplyText] = useState('');

    useEffect(() => {
        setIsLiked(comment.is_liked);
        setLikesCount(comment.likes_count);
    }, [comment]);

    const handleLike = async () => {
        try {
            const res = await api.post(`comments/${comment.id}/like/`);
            setIsLiked(res.data.liked);
            setLikesCount(prev => res.data.liked ? prev + 1 : prev - 1);
        } catch (err) {
            console.error("Comment Like Error:", err.response?.data || err.message);
            if (err.response?.status === 401) onAuthRequired();
        }
    };

    const submitReply = async () => {
        if (!replyText.trim()) return;
        if (!comment.post) {
            console.error("Reply Error: comment.post is missing!");
            return;
        }
        try {
            const res = await api.post(`posts/${comment.post}/comments/`, {
                content: replyText,
                parent: comment.id
            });
            onReplyAdded(res.data);
            setReplyText('');
            setShowReply(false);
        } catch (err) {
            console.error("Reply Error:", err.response?.data || err.message);
            if (err.response?.status === 401) onAuthRequired();
        }
    };

    return (
        <div className={`space-y-3 ${depth > 0 ? 'ml-6 border-l-2 border-slate-800 pl-4' : ''}`}>
            <div className="group">
                <div className="flex items-center gap-2 mb-1">
                    <span className="font-bold text-xs text-indigo-400">{comment.author.username}</span>
                    {comment.parent_author && (
                        <span className="text-[10px] text-slate-500 flex items-center gap-1">
                            <Reply size={10} className="rotate-180" />
                            to <span className="text-slate-400 font-bold">@{comment.parent_author}</span>
                        </span>
                    )}
                    <span className="text-[10px] text-slate-600 font-mono mt-0.5">{new Date(comment.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                </div>
                <p className="text-sm text-slate-300 leading-relaxed">{comment.content}</p>

                <div className="flex items-center gap-4 mt-2">
                    <button
                        onClick={handleLike}
                        className={`flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider transition-colors ${isLiked ? 'text-rose-500' : 'text-slate-500 hover:text-rose-400'}`}
                    >
                        <Heart size={14} fill={isLiked ? 'currentColor' : 'none'} />
                        {likesCount}
                    </button>
                    <button
                        onClick={() => setShowReply(!showReply)}
                        className="flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-slate-500 hover:text-indigo-400 transition-colors"
                    >
                        <Reply size={14} />
                        Reply
                    </button>
                </div>

                {showReply && (
                    <div className="mt-3 flex gap-2">
                        <input
                            className="input-field text-xs py-1.5"
                            placeholder="Write a reply..."
                            autoFocus
                            value={replyText}
                            onChange={(e) => setReplyText(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && submitReply()}
                        />
                        <button onClick={submitReply} className="btn-primary py-1 px-3">
                            <Send size={14} />
                        </button>
                    </div>
                )}
            </div>

            {comment.replies && comment.replies.map(reply => (
                <CommentItem
                    key={reply.id}
                    comment={reply}
                    depth={depth + 1}
                    onReplyAdded={onReplyAdded}
                    onAuthRequired={onAuthRequired}
                />
            ))}
        </div>
    );
};

export default function CommentSection({ postId, onAuthRequired }) {
    const [comments, setComments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [newComment, setNewComment] = useState('');

    const fetchComments = async () => {
        try {
            const res = await api.get(`posts/${postId}/`);
            setComments(res.data.comments);
        } catch (err) {
            console.error("Fetch Comments Error:", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchComments();
    }, [postId]);

    const submitComment = async () => {
        if (!newComment.trim()) return;
        try {
            await api.post(`posts/${postId}/comments/`, {
                content: newComment
            });
            setNewComment('');
            fetchComments(); // Refresh the tree
        } catch (err) {
            console.error("Comment Submit Error:", err.response?.data || err.message);
            if (err.response?.status === 401) onAuthRequired();
        }
    };

    return (
        <div className="pt-4 space-y-6">
            <div className="flex gap-3">
                <input
                    className="input-field text-sm"
                    placeholder="What are your thoughts?"
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && submitComment()}
                />
                <button onClick={submitComment} className="btn-primary">
                    <Send size={18} />
                </button>
            </div>

            <div className="space-y-6">
                {loading ? (
                    <div className="text-center py-4 text-slate-500 text-sm animate-pulse">Loading comments...</div>
                ) : comments.length > 0 ? (
                    comments.map(comment => (
                        <CommentItem
                            key={comment.id}
                            comment={comment}
                            onReplyAdded={fetchComments}
                            onAuthRequired={onAuthRequired}
                        />
                    ))
                ) : (
                    <div className="text-center py-4 text-slate-600 text-sm">No comments yet. Be the first to start the conversation!</div>
                )}
            </div>
        </div>
    );
}
