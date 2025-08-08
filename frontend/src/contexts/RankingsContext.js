import React, {
    createContext,
    useContext,
    useState,
    useEffect,
} from "react";

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

    // State for authentication
    const [players, setPlayers] = useState({});
    const [nextOffset, setNextOffset] = useState(0);
    const [limit, setLimit] = useState(20);
    
    // Get environment var for API calls
    const API_BASE = process.env.REACT_APP_API_BASE_URL;

    // Debugging Tool
    useEffect(() => {
        console.log("Players state updated:", Object.keys(players).length, "players");
    }, [players]);

    // CHECK FOR EXISTING PLAYERS on first page load --> ON EACH PAGE RELOAD
    useEffect(() => { // useEffect itself can't be async
        const checkExistingPlayers = async () => {

            // Fetch first 20 players.
            // Have to include token since it's a protected route
            const stored_token = localStorage.getItem('token');

            if (stored_token) {
                try {
                    const response = await fetch(
                        `${API_BASE}/rankings/players?offset=${nextOffset}&limit=${limit}`, {
                        headers: {
                            'Authorization': `Bearer ${stored_token}`,
                            'Content-Type': 'application/json'
                        }
                    });

                    // Valid response -> Save players and offset info
                    if (response.ok) {
                        console.log("Got players");
                        const data = await response.json();

                        console.log(data);
                        // Have to assign the data to the players state variable.
                        for (const player of data.players) {
                            setPlayers(prevPlayers => ({
                                ...prevPlayers,
                                [player.ranking]: player
                            }));
                        }

                        console.log(players);

                        setLimit(data.pagination.limit);
                        setNextOffset(data.pagination.nextOffset);
                    } else {
                        // Not sure what the else case is
                        // Response came but isn't good.
                    }
                } catch (error) {
                    console.error("Couldn't retrieve players", error);
                }
            }
        };

        console.log("Players state updated:", players);
        console.log("NextOffset: ", nextOffset);


        checkExistingPlayers();

    }, []); // Empty dependency array. Run once on app start

    // THIS IS WHAT COMPONENTS CAN ACCESS
    const value = {
        players,
        nextOffset, 
        limit,
    };

    return (
        <RankingsContext.Provider value={value}>
            {children}
        </RankingsContext.Provider>
    );
};