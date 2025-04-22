// Navbar.jsx
import { Link } from 'react-router-dom';
import DescriptionIcon from '@mui/icons-material/Description';
import './Navbar.css';

const Navbar = () => {
    return (
        <nav className="navbar">
            <div className="navbar-container">
                <Link to="/" className="navbar-brand">
                    <DescriptionIcon style={{ marginRight: '8px' }} />
                    REPHUB
                </Link>
                <div className="navbar-links">
                    <Link to="/" className="navbar-link">Home</Link>
                    <Link to="/resumes" className="navbar-link">Resumes</Link>
                    <Link to="/jobs" className="navbar-link">Jobs</Link>
                    <Link to="/match" className="navbar-link">Match</Link>
                </div>
            </div>
        </nav>
    );
};

export default Navbar;