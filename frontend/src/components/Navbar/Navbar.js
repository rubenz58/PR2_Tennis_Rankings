import { useAuth } from "../../contexts/AuthContext";
import { Link } from 'react-router-dom';


import './Navbar.css';


const Navbar = () => {

    const { user, logout } = useAuth();

    return (
        <nav className="navbar">
            {/* <h1 className="navbar-title">Tennis Rankings</h1> */}
            <Link to="/rankings" className="navbar-title-link">
                <h1 className="navbar-title">Tennis Rankings</h1>
            </Link>
            
            {user ? (
                <div className="navbar-user">
                <span className="navbar-user-welcome">
                    Welcome, <span className="navbar-user-name">{user.name}</span>!
                </span>
                <button onClick={logout} className="navbar-logout-btn">
                    Logout
                </button>
                </div>
            ) : (
                <div className="navbar-empty"></div>
            )}
        </nav>
    );
}

export default Navbar;