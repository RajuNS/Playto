import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { MessageSquare, ThumbsUp } from 'lucide-react';
import api from '../api';

const Feed = ({ currentUser }) => {
    const [posts, setPosts] = useState([]);
    const [content, setContent] = useState("");

    const fetchPosts = async () => {
        try {
            const res = await api.get('posts/');
            setPosts(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    useEffect(() => {
        fetchPosts();
    }, [currentUser]); // Refresh if user toggles to see correct liked state

    const handleCreatePost = async (e) => {
        e.preventDefault();
        try {
            await api.post('posts/', { content });
            setContent("");
            fetchPosts();
        } catch (err) {
            console.error("Failed to create post", err);
        }
    };

    const handleLike = async (postId, liked) => {
        // Optimistic update impossible easily without deep copy, better just refetch or careful state update
        // Let's refetch for simplicity of prototype, or just toggle locally
        try {
            const res = await api.post(`vote/post/${postId}/`);
            // Simple re-fetch
            fetchPosts();
        } catch (err) {
            console.error(err);
        }
    };

    return (
        <div className="space-y-6">
            {currentUser && (
                <div className="bg-white p-4 rounded-lg shadow-md">
                    <form onSubmit={handleCreatePost}>
                        <textarea
                            className="w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 mb-2"
                            rows="3"
                            placeholder={`What's on your mind, ${currentUser}?`}
                            value={content}
                            onChange={e => setContent(e.target.value)}
                            required
                        />
                        <div className="text-right">
                            <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">Post</button>
                        </div>
                    </form>
                </div>
            )}

            <div className="space-y-4">
                {posts.map(post => (
                    <div key={post.id} className="bg-white p-4 rounded-lg shadow-md hover:shadow-lg transition-shadow">
                        <div className="flex justify-between items-start mb-2">
                            <div className="font-bold text-gray-800">{post.author.username}</div>
                            <div className="text-gray-500 text-sm">{new Date(post.created_at).toLocaleString()}</div>
                        </div>
                        <p className="text-gray-700 mb-4 whitespace-pre-wrap">{post.content}</p>

                        <div className="flex items-center space-x-6 text-gray-500">
                            <button
                                onClick={() => handleLike(post.id, post.user_has_liked)}
                                className={`flex items-center space-x-2 p-1 rounded hover:bg-gray-100 ${post.user_has_liked ? 'text-blue-600 font-bold' : ''}`}
                            >
                                <ThumbsUp size={18} />
                                <span>{post.likes_count}</span>
                            </button>
                            <Link to={`/post/${post.id}`} className="flex items-center space-x-2 hover:text-blue-600">
                                <MessageSquare size={18} />
                                <span>Discuss</span>
                            </Link>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Feed;
