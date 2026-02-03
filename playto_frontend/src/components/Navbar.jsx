import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../api';

const Navbar = ({ currentUser, setCurrentUser }) => {
    // Simple mock auth for prototype
    const handleLogin = (username) => {
        // In real app, this would be a POST /login
        // Here we just set state. Ideally we fetch user ID from backend or create if not exists.
        // For prototype simplicity, assuming users exist or we just use username.
        // But API needs Authentication header (Token/Session).
        // Let's assume Backend uses SessionAuthentication or Basic.
        // I configured IsAuthenticatedOrReadOnly.
        // I'll make a quick "login" endpoint or just Basic Auth header?
        // Let's use Basic Auth for simplicity in this prototype.
        const password = 'password'; // Mock password
        const token = btoa(`${username}:${password}`);
        api.defaults.headers.common['Authorization'] = `Basic ${token}`;
        setCurrentUser(username);
    };

    return (
        <nav className="bg-white shadow-md p-4">
            <div className="container mx-auto flex justify-between items-center">
                <Link to="/" className="text-xl font-bold text-blue-600">Playto Feed</Link>
                <div className="space-x-4">
                    {currentUser ? (
                        <span>Hello, {currentUser}</span>
                    ) : (
                        <div className="space-x-2">
                            <button onClick={() => handleLogin('alice')} className="px-3 py-1 bg-gray-200 rounded">Login as Alice</button>
                            <button onClick={() => handleLogin('bob')} className="px-3 py-1 bg-gray-200 rounded">Login as Bob</button>
                            <button onClick={() => handleLogin('charlie')} className="px-3 py-1 bg-gray-200 rounded">Login as Charlie</button>
                        </div>
                    )}
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
