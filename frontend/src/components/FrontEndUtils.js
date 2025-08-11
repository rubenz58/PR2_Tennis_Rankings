import { Link } from "react-router-dom";
import { useRef, useEffect } from "react";

import { useAuth } from "../contexts/AuthContext";
import { useRankings } from "../contexts/RankingsContext";


export const LoadingSpinner = () => {
    return <div>Loading...</div>;
}

// components/NotFound/NotFound.js
export const NotFound = () => {
  const { user } = useAuth();
  
  return (
    <div style={{ textAlign: 'center', padding: '2rem' }}>
      <h1>404 - Page Not Found</h1>
      <p>The page you're looking for doesn't exist.</p>
      {user ? (
        <Link to="/dashboard">Go to Dashboard</Link>
      ) : (
        <Link to="/login">Go to Login</Link>
      )}
    </div>
  );
};

export const useInfiniteScroll = () => {
  const observerRef = useRef();
  const { hasMore, getNewPlayers, loadingPlayers } = useRankings();

  useEffect(() => {
    // IntersectionObserver watches an element to signal when it
    // becomes visible.
    const observer = new IntersectionObserver(
      (entries) => {
        // When target element becomes visible
        if(entries[0].isIntersecting && hasMore && !loadingPlayers) {
          getNewPlayers(); // Call Load More
        }
      },
      {threshold: 0.1} // Triggers when 10% of element is visible
    );
    if (observerRef.current) {
      observer.observe(observerRef.current);
    }

    return() => observer.disconnect(); // Cleanup
  }, [hasMore, loadingPlayers, getNewPlayers]);

  return observerRef; // Return ref to attach to trigger element
}