import { Routes, Route, Navigate } from "react-router-dom";
import { PublicRoute, ProtectedRoute } from "../RouteProtection";

import LoginForm from "./LoginForm/LoginForm";
import SignUpForm from "./SignUpForm/SignUpForm";
import GoogleCallback from "./GoogleCallback";
import { Rankings } from "../Rankings";
import { NotFound } from "../IntroComponents";
import { Dashboard } from "../Dashboard";


const MainContent = () => {

    return (
        <div className="main-content-container">
            <Routes>
                {/* Public Routes - redirect to dashboard if logged in */}
                <Route path='/login' element={
                    <PublicRoute>
                        <LoginForm />
                    </PublicRoute>
                }/>
                <Route path='/signup' element={
                    <PublicRoute>
                        <SignUpForm />
                    </PublicRoute>
                }/>

                <Route path='/auth/callback' element={
                    <PublicRoute>
                        <GoogleCallback />
                    </PublicRoute>
                }/>

                {/* Protected Routes - redirect to login if not logged in */}
                <Route path='/dashboard' element={
                    <ProtectedRoute>
                        <Dashboard />
                    </ProtectedRoute>
                }/>

                {/* Protected Routes - redirect to login if not logged in */}
                <Route path='/rankings' element={
                    <ProtectedRoute>
                        <Rankings />
                    </ProtectedRoute>
                }/>

                {/* Default redirects */}
                <Route path="/" element={<Navigate to="/dashboard" replace />} />

                <Route path="*" element={<NotFound />} />
            </Routes>
        </div>
    );
    
}

export default MainContent;