// SignUpForm.js
import React, { useState } from "react";
import { Link } from "react-router-dom";

import { useAuth } from "../../../contexts/AuthContext";


import './SignUpForm.css';


const SignUpForm = () => {
    // Variables that will hold input information
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        name: '',
    });
    const [error, setError] = useState('');
    const { signup, loading, signupWithGoogle, loginWithGoogle } = useAuth();

    // As a user types, values displayed will change
    const handleChange = (e) => {
        setFormData({
            ...formData, // Takes previous data
            [e.target.name]: e.target.value // Wherever the user is typing gets updated
        });

        // Clear error when user starts typing
        if (error) setError('');
    };

    const handleSubmit = async (e) => {
        // Prevents the form from being submitted as an HTML form
        // Logic is handled here in JS
        // With HTML there would be a page redirect, whereas here we stay on the page
        e.preventDefault();

        const result = await signup(formData);

        if (!result.success) {
            setError(result.error);
        }
    };

    // GOOGLE SIGNUP
    const handleGoogleSignup = async() => {
        setError('');

        const result = await loginWithGoogle();

        if (result && !result.success) {
            setError(result.error);
        }
        // If successful, AuthContext updates user state automatically
    }

    return (
        <div className={`signup-container ${loading ? 'signup-container-loading' : ''}`}>
            <h2 className="signup-title">Sign Up</h2>

            {error && (
                <div className="error-message">
                        {error}
                </div>
            )}
            {/*<button
                type="button"
                onClick={handleGoogleSignup}
                disabled={loading}
                className={`google-login-btn ${loading ? 'google-login-btn-loading' : ""}`}
            >
                {!loading && <div className="google-icon"></div>}
                {loading ? "" : "Signup with Google"}
            </button>
            <div className="form-divider">
                <span>or</span>
            </div>*/}

            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label htmlFor="email" className="form-label">
                        Email:
                    </label>
                    <input
                        type="email" // Browser knows type. Additional validation
                        // This plus htmlFor -> Label clicks work
                        id="email" // Connects to htmlFor. 
                        name="email" // formData gets correct property names
                        value={formData.email}
                        onChange={handleChange}
                        required
                        className="form-input"
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="password" className="form-label">
                        Password:
                    </label>
                    <input
                        type="password"
                        id="password"
                        name="password"
                        value={formData.password}
                        onChange={handleChange}
                        required
                        className="form-input"
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="name" className="form-label">
                        Name:
                    </label>
                    <input
                        type="text" // Browser knows type. Additional validation
                        // This plus htmlFor -> Label clicks work
                        id="name" // Connects to htmlFor. 
                        name="name" // formData gets correct property names
                        value={formData.name}
                        onChange={handleChange}
                        required
                        className="form-input"
                    />
                </div>

                <button
                    type="submit"
                    disabled={loading}
                    className="signup-submit-button"
                >
                    {loading ? "Signing in..." : "Sign up"}
                </button>

                <div className="form-footer">
                    Already have an account?{' '}
                    <Link to="/login" className="signup-form-footer-link">
                        Login here
                    </Link>
                </div>
            </form>
        </div>
    );
};

export default SignUpForm;