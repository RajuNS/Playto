import React, { useEffect, useState } from 'react';
import api from '../api';

const Leaderboard = () => {
    const [users, setUsers] = useState([]);

    useEffect(() => {
        const fetchLeaderboard = async () => {
            try {
                const res = await api.get('leaderboard/');
                setUsers(res.data);
            } catch (err) {
                console.error("Failed to fetch leaderboard", err);
            }
        };

        fetchLeaderboard();
        const interval = setInterval(fetchLeaderboard, 30000); // Refresh every 30s
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="bg-white p-4 rounded-lg shadow-md w-full md:w-64">
            <h3 className="font-bold text-lg mb-4 border-b pb-2">Top 5 (24h)</h3>
            <ul>
                {users.length === 0 && <li className="text-gray-500 text-sm">No activity yet.</li>}
                {users.map((user, index) => (
                    <li key={index} className="flex justify-between py-2 border-b last:border-0">
                        <span className="font-medium text-gray-700">{index + 1}. {user.username}</span>
                        <span className="font-bold text-blue-600">{user.score}</span>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default Leaderboard;
