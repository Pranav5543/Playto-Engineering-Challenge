import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import PostCard from './components/PostCard';
import Leaderboard from './components/Leaderboard';
import AuthModal from './components/AuthModal';
import api from './api';
import { Plus, Layout, Flame, Hash } from 'lucide-react';

function App() {
  const [user, setUser] = useState(null);
  const [posts, setPosts] = useState([]);
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [showCreatePost, setShowCreatePost] = useState(false);
  const [newPostContent, setNewPostContent] = useState('');

  const fetchPosts = async () => {
    try {
      const res = await api.get('posts/');
      setPosts(res.data);
    } catch (err) {
      console.error("Fetch Posts Error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPosts();
    // In a real app, you'd check token validity on mount
    const savedUser = localStorage.getItem('playto_username');
    if (savedUser) setUser({ username: savedUser });
  }, []);

  const handleAuthSuccess = (userData) => {
    setUser(userData);
    localStorage.setItem('playto_username', userData.username);
    fetchPosts(); // Refresh liked states
  };

  const handleCreatePost = async () => {
    if (!newPostContent.trim()) return;
    try {
      await api.post('posts/', { content: newPostContent });
      setNewPostContent('');
      setShowCreatePost(false);
      fetchPosts();
    } catch (err) {
      console.error("Create Post Error:", err.response?.data || err.message);
      if (err.response?.status === 401) setIsAuthOpen(true);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('playto_auth_token');
    localStorage.removeItem('playto_username');
    setUser(null);
    setShowCreatePost(false);
    fetchPosts(); // Refresh to show public view
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar
        user={user}
        onOpenAuth={() => setIsAuthOpen(true)}
        onNewPost={() => {
          if (!user) return setIsAuthOpen(true);
          setShowCreatePost(true);
          window.scrollTo({ top: 0, behavior: 'smooth' });
        }}
        onLogout={handleLogout}
      />

      <main className="max-w-6xl mx-auto px-4 pt-24 pb-12">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">

          {/* Main Feed */}
          <div className="lg:col-span-8 space-y-6">

            {/* Create Post Widget */}
            <div className="card border-dashed border-2 border-slate-800 bg-transparent hover:border-indigo-500/50 transition-all group p-6">
              {!showCreatePost ? (
                <button
                  onClick={() => user ? setShowCreatePost(true) : setIsAuthOpen(true)}
                  className="w-full flex items-center gap-4 text-slate-500 group-hover:text-slate-300 transition-colors"
                >
                  <div className="w-12 h-12 rounded-xl bg-slate-900 flex items-center justify-center group-hover:bg-indigo-600/10 transition-colors">
                    <Plus className="group-hover:text-indigo-500" />
                  </div>
                  <span className="text-lg font-medium">What's on your mind? Share with the community...</span>
                </button>
              ) : (
                <div className="space-y-4">
                  <textarea
                    className="input-field min-h-[120px] text-lg resize-none"
                    placeholder="Write your story..."
                    autoFocus
                    value={newPostContent}
                    onChange={(e) => setNewPostContent(e.target.value)}
                  />
                  <div className="flex justify-end gap-3">
                    <button onClick={() => setShowCreatePost(false)} className="btn-ghost">Cancel</button>
                    <button onClick={handleCreatePost} className="btn-primary px-8">Post Now</button>
                  </div>
                </div>
              )}
            </div>

            {/* Posts List */}
            <div className="space-y-6">
              <div className="flex items-center gap-2 mb-2 px-1">
                <Flame className="text-orange-500" size={20} />
                <h2 className="text-xl font-bold">Trending Feed</h2>
              </div>

              {loading ? (
                [1, 2, 3].map(i => (
                  <div key={i} className="card h-48 animate-pulse bg-slate-900/50" />
                ))
              ) : posts.map(post => (
                <PostCard
                  key={post.id}
                  post={post}
                  onAuthRequired={() => setIsAuthOpen(true)}
                />
              ))}
            </div>
          </div>

          {/* Sidebar */}
          <aside className="lg:col-span-4 space-y-6 hidden lg:block">
            <Leaderboard />
            <div className="card bg-gradient-to-br from-indigo-900/20 to-purple-900/20 border-indigo-500/20">
              <h3 className="font-bold mb-2 flex items-center gap-2">
                <Hash className="text-indigo-400" size={18} />
                Community Guide
              </h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Earn Karma by posting and helping others. 5 Karma for post likes, 1 Karma for comment likes.
                Keep it friendly!
              </p>
            </div>
          </aside>

        </div>
      </main>

      <AuthModal
        isOpen={isAuthOpen}
        onClose={() => setIsAuthOpen(false)}
        onAuthSuccess={handleAuthSuccess}
      />
    </div>
  );
}

export default App;
