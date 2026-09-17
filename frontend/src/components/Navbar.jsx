import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import FolderIcon from '@mui/icons-material/Folder';
import HomeIcon from '@mui/icons-material/Home';
import SearchIcon from '@mui/icons-material/Search';

const Navbar = () => {
  return (
    <AppBar position="static">
      <Toolbar>
        <FolderIcon sx={{ mr: 2 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Resume Repository
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button 
            color="inherit" 
            component={RouterLink} 
            to="/"
            startIcon={<HomeIcon />}
          >
            Home
          </Button>
          <Button 
            color="inherit" 
            component={RouterLink} 
            to="/resumes"
            startIcon={<FolderIcon />}
          >
            Resumes
          </Button>
          <Button 
            color="inherit" 
            component={RouterLink} 
            to="/match"
            startIcon={<SearchIcon />}
          >
            Match
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
