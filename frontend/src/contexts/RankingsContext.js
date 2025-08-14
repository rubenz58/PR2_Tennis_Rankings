import React, {
    createContext,
    useContext,
    useState,
    useEffect,
} from "react";

import { useAuth } from "./AuthContext";

// Create the context
const RankingsContext = createContext();

// Create hook to easily use context
export const useRankings = () => {
    const context = useContext(RankingsContext);
    if (!context) {
        throw new Error('useRankings must be used within RankingsProvider');
    }
    return context; 
};

// Create the provider (Component that holds the data)
export const RankingsProvider = ({ children }) => {

    const { user, loading: authLoading, token } = useAuth();

    // State for authentication
    const [players, setPlayers] = useState({});
    const [nextOffset, setNextOffset] = useState(0);
    const [limit, setLimit] = useState(20);
    const [hasMore, setHasMore] = useState(false);
    const [loadingPlayers, setLoadingPlayers] = useState(false);
    
    // Get environment var for API calls
    const API_BASE = process.env.REACT_APP_API_BASE_URL || "";

    // CHECK FOR EXISTING PLAYERS on first page load --> ON EACH PAGE RELOAD
    useEffect(() => { // useEffect itself can't be async

        if (authLoading || !user) return;
        fetchPlayers(0, 20);

    }, [user, authLoading]);

    const getNewPlayers = async() => {
        console.log("Getting new players");
        fetchPlayers(nextOffset, limit);
    }

    const fetchPlayers = async (offset, limit) => {
        if (loadingPlayers) return; // Don't call if already loading
        setLoadingPlayers(true);

        // Have to include token since it's a protected route
        if (token) {
            try {
                const response = await fetch(
                    `${API_BASE}/rankings/players?offset=${offset}&limit=${limit}`, {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                });

                // Valid response -> Save players and offset info
                if (response.ok) {
                    // console.log("Got players");
                    const data = await response.json();

                    const playersObject = {};
                    data.players.forEach(player => {
                        playersObject[player.ranking] = player;
                    });
                    setPlayers(prevPlayers => ({
                        ...prevPlayers,  // Keep existing players
                        ...playersObject // Add new players
                    }));

                    setLimit(data.pagination.limit);
                    setNextOffset(data.pagination.next_offset);
                    setHasMore(data.pagination.has_more);
                } else {
                    // Communication was successful, but not allowed
                    // Ex. Not authorized to access
                    console.error("Bad response:", response.status);
                }
            } catch (error) {
                // This is network error. Couldn't get a reponse.
                console.error("Couldn't retrieve players", error);
            }
        }
        setLoadingPlayers(false);
    };


    // THIS IS WHAT COMPONENTS CAN ACCESS
    const value = {
        players,
        nextOffset, 
        limit,
        hasMore,
        getNewPlayers,
        loadingPlayers,
    };

    return (
        <RankingsContext.Provider value={value}>
            {children}
        </RankingsContext.Provider>
    );
};