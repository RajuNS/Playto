import React, { useState } from 'react';
import { MessageSquare, ThumbsUp } from 'lucide-react';
import api from '../api';

const Comment = ({ comment, currentUser, onReply }) => {
    const [showReplyForm, setShowReplyForm] = useState(false);
    const [replyContent, setReplyContent] = useState("");
    const [liked, setLiked] = useState(comment.user_has_liked);
    const [likesCount, setLikesCount] = useState(comment.likes_count);

    const handleLike = async () => {
        try {
            const res = await api.post(`vote/comment/${comment.id}/`);
            if (res.data.status === 'liked') {
                setLiked(true);
                setLikesCount(prev => prev + 1);
            } else if (res.data.status === 'unliked') {
                setLiked(false);
                setLikesCount(prev => prev - 1);
            }
        } catch (err) {
            console.error("Like failed", err);
        }
    };

    const handleSubmitReply = (e) => {
        e.preventDefault();
        onReply(comment.id, replyContent);
        setReplyContent("");
        setShowReplyForm(false);
    };

    return (
        <div className="pl-4 border-l-2 border-gray-200 mt-4">
            <div className="bg-gray-50 p-3 rounded-lg">
                <div className="flex justify-between items-start">
                    <span className="font-semibold text-sm text-gray-800">{comment.author.username}</span>
                    <span className="text-xs text-gray-500">{new Date(comment.created_at).toLocaleString()}</span>
                </div>
                <p className="text-gray-700 my-2">{comment.content}</p>
                <div className="flex space-x-4 text-xs text-gray-500">
                    <button onClick={handleLike} className={`flex items-center space-x-1 hover:text-blue-500 ${liked ? 'text-blue-600 font-bold' : ''}`}>
                        <ThumbsUp size={14} />
                        <span>{likesCount}</span>
                    </button>
                    {currentUser && (
                        <button onClick={() => setShowReplyForm(!showReplyForm)} className="flex items-center space-x-1 hover:text-blue-500">
                            <MessageSquare size={14} />
                            <span>Reply</span>
                        </button>
                    )}
                </div>

                {showReplyForm && (
                    <form onSubmit={handleSubmitReply} className="mt-2 flex space-x-2">
                        <input
                            type="text"
                            className="flex-1 p-1 border rounded text-sm"
                            placeholder="Write a reply..."
                            value={replyContent}
                            onChange={e => setReplyContent(e.target.value)}
                            required
                        />
                        <button type="submit" className="bg-blue-600 text-white px-3 py-1 rounded text-sm">Post</button>
                    </form>
                )}
            </div>

            {comment.replies && comment.replies.map(reply => (
                <Comment key={reply.id} comment={reply} currentUser={currentUser} onReply={onReply} />
            ))}
        </div>
    );
};

export default Comment;
