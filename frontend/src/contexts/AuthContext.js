import React, {
    createContext,
    useContext,
    useState,
    useEffect,
} from "react";

// Create the context
const AuthContext = createContext();

// Create hook to easily use context
export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within AuthProvider');
    }
    return context; 
};

// Create the provider (Component that holds the data)
export const AuthProvider = ({ children }) => {

    // State for authentication
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(null);
    const [loading, setLoading] = useState(true);
    const [oAuthLoading, setOAuthLoading] = useState(false);

    // Get environment var for API calls
    const API_BASE = process.env.REACT_APP_API_BASE_URL || "";
    // const CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID;

    // CHECK FOR EXISTING LOGIN ON EACH PAGE RELOAD
    useEffect(() => { // useEffect itself can't be async
        // console.log("Loading application");
        
        const checkExistingAuth = async () => {

            if (user) return;  // Skip if user already exists

            const stored_token = localStorage.getItem('token');

            if (stored_token) {
                try {
                    // Verify token is still valid by calling /me endpoint
                    const response = await fetch(`${API_BASE}/api/auth/me`, {
                        headers: {
                            'Authorization': `Bearer ${stored_token}`,
                            'Content-Type': 'application/json'
                        }
                    });

                    // Token is valid -> User gets logged in
                    if (response.ok) {
                        const data = await response.json();
                        setUser(data.user);
                        setToken(stored_token);
                    } else {
                        // Token is invalid, remove it
                        localStorage.removeItem('token');
                    }
                } catch (error) {
                    console.error('Auth check failed:', error);
                    localStorage.removeItem('token');
                }
            }

            setLoading(false);
        };

        checkExistingAuth();

    }, []); // Empty dependency array. Run once on app start

    // Fetches Google Auth Url from BKND.
    const loginWithGoogle = async() => {
        console.log("google login attempt");
        setLoading(true);
        setOAuthLoading(true);

        try {
            // 'await' pauses the function at this line
            // Browser and other parts of website (user clicking etc)
            // can keep going.
            const response = await fetch(`${API_BASE}/api/auth/google/login`);
            const { auth_url } = await response.json();

            // Redirect to data["auth_url"]
            // console.log("Would redirect to:", auth_url);

            window.location.href = auth_url;
        } catch (error) {
            // Network error
            return { success: false, error: "Network error occurred" };
        }
    }

    const signupWithGoogle = async() => {
        console.log("google signup attempt");
    }

    // LOGIN FUNCTION
    const login = async (credentials) => {
        setLoading(true);

        try {
            // 'await' pauses the function at this line
            // Browser and other parts of website (user clicking etc)
            // can keep going.
            const response = await fetch(`${API_BASE}/api/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(credentials)
            });

            const data = await response.json();

            if (response.ok) {
                // Login successful - User State updated.
                setUser(data.user);
                setToken(data.token);
                localStorage.setItem('token', data.token);
                return { success: true, data };
            } else {
                // Login failed
                return { success: false, error: data.error };
            }
        } catch (error) {
            // Network error
            return { success: false, error: "Network error occurred" };
        } finally {
            setLoading(false); // Hide loading state
        }
    }

    const signup = async (userData) => {
        setLoading(true);

        try {
            // 'await' pauses the function at this line
            // Browser and other parts of website (user clicking etc)
            // can keep going.
            const response = await fetch(`${API_BASE}/api/auth/signup`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(userData)
            });

            const data = await response.json();

            if (response.ok) {
                // Login successful - User State updated.
                setUser(data.user);
                setToken(data.token);
                localStorage.setItem('token', data.token);
                return { success: true, data };
            } else {
                // Login failed
                return { success: false, error: data.error };
            }
        } catch (error) {
            // Network error
            return { success: false, error: "Network error occurred" };
        } finally {
            setLoading(false); // Hide loading state
        }
    }

    const logout = async () => {
        setUser(null);
        setToken(null);
        localStorage.removeItem('token');
    }

    // THIS IS WHAT COMPONENTS CAN ACCESS
    const value = {
        user, // Current user object
        token, // JWT string token
        loading, // Boolean for loading states - spinners while loading
        setUser,
        setToken,
        setLoading,
        login, // func.
        signup, // func.
        logout, // func.
        loginWithGoogle,
        signupWithGoogle,
        oAuthLoading,
        setOAuthLoading,
    };


    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};