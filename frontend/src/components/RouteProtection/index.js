import { Navigate } from "react-router-dom";

import { useAuth } from "../../contexts/AuthContext"


export const PublicRoute = ({ children }) => {
    const { user } = useAuth();

    // console.log("PublicRoute triggered - user:", user ? "logged in" : "not logged in");
    // console.log("Public: Current path:", window.location.pathname);

    return user ? <Navigate to="/rankings" replace/> : children;
}


export const ProtectedRoute = ({ children }) => {
    const { user, loading } = useAuth();

    // console.log("ProtectedRoute triggered - user:", user ? "logged in" : "not logged in");
    // console.log("Private: Current path:", window.location.pathname);

    if (loading) {
    return <div>Loading...</div>; // Or your loading spinner
  }

    return user ? children : <Navigate to="/login" replace/>;
}
