import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import api from '../api';
import Comment from './Comment';
import { MessageSquare, ThumbsUp } from 'lucide-react';

const PostDetail = ({ currentUser }) => {
    const { id } = useParams();
    const [post, setPost] = useState(null);
    const [loading, setLoading] = useState(true);
    const [commentContent, setCommentContent] = useState("");

    const fetchPost = async () => {
        try {
            setLoading(true);
            const res = await api.get(`posts/${id}/`);
            setPost(res.data);
        } catch (err) {
            console.error("Failed to fetch post", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchPost();
    }, [id, currentUser]); // Refetch if user changes to update 'user_has_liked' status

    const handleLike = async () => {
        try {
            const res = await api.post(`vote/post/${post.id}/`);
            if (res.data.status === 'liked') {
                setPost({ ...post, likes_count: post.likes_count + 1, user_has_liked: true });
            } else if (res.data.status === 'unliked') {
                setPost({ ...post, likes_count: post.likes_count - 1, user_has_liked: false });
            }
        } catch (err) {
            console.error("Like failed", err);
        }
    };

    const handleComment = async (parentId, content) => {
        try {
            await api.post('comments/', {
                post: post.id,
                parent: parentId,
                content: content
            });
            fetchPost(); // Refresh tree (Optimally should inject locally, but full refresh ensures correct nesting order from server)
            if (!parentId) setCommentContent("");
        } catch (err) {
            console.error("Comment failed", err);
        }
    };

    if (loading) return <div className="p-4">Loading...</div>;
    if (!post) return <div className="p-4">Post not found</div>;

    return (
        <div className="bg-white p-6 rounded-lg shadow-md">
            <h1 className="text-xl font-bold text-gray-800 mb-2">Post by {post.author.username}</h1>
            <p className="text-sm text-gray-500 mb-4">{new Date(post.created_at).toLocaleString()}</p>
            <div className="text-lg text-gray-800 mb-6 border-b pb-4">
                {post.content}
            </div>

            <div className="flex space-x-6 text-gray-600 mb-6">
                <button onClick={handleLike} className={`flex items-center space-x-2 px-3 py-1 rounded hover:bg-gray-100 ${post.user_has_liked ? 'text-blue-600 font-bold' : ''}`}>
                    <ThumbsUp size={18} />
                    <span>{post.likes_count} Likes</span>
                </button>
                <div className="flex items-center space-x-2">
                    <MessageSquare size={18} />
                    <span>{post.comments ? post.comments.length : 0} Roots</span>
                    {/* Note: comments.length only counts top-level roots here unless we flatten */}
                </div>
            </div>

            <div className="mb-8">
                <h3 className="font-bold text-lg mb-4">Comments</h3>
                {currentUser && (
                    <form onSubmit={(e) => { e.preventDefault(); handleComment(null, commentContent); }} className="mb-6 flex gap-2">
                        <textarea
                            className="w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                            rows="2"
                            placeholder="Write a comment..."
                            value={commentContent}
                            onChange={e => setCommentContent(e.target.value)}
                            required
                        />
                        <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded-lg self-end h-10 hover:bg-blue-700">Post</button>
                    </form>
                )}

                <div className="space-y-4">
                    {post.comments && post.comments.map(comment => (
                        <Comment key={comment.id} comment={comment} currentUser={currentUser} onReply={handleComment} />
                    ))}
                </div>
            </div>
        </div>
    );
};

export default PostDetail;
