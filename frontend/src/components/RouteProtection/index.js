import { Navigate } from "react-router-dom";

import { useAuth } from "../../contexts/AuthContext"


export const PublicRoute = ({ children }) => {
    const { user } = useAuth();

    return user ? <Navigate to="/rankings" replace/> : children;
}


export const ProtectedRoute = ({ children }) => {
    const { user } = useAuth();

    return user ? children : <Navigate to="/login" replace/>;
}
