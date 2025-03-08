import React from 'react';
import { AppBar, Toolbar, Typography, Button, Container } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

function Navbar() {
  return (
    <AppBar position="static" color="transparent" elevation={0}>
      <Container>
        <Toolbar disableGutters>
          <Typography
            variant="h6"
            component={RouterLink}
            to="/"
            sx={{
              flexGrow: 1,
              textDecoration: 'none',
              color: 'inherit',
              fontWeight: 'bold',
            }}
          >
            Filmila
          </Typography>
          <Button color="inherit" component={RouterLink} to="/films">
            Browse Films
          </Button>
          <Button color="inherit" component={RouterLink} to="/upload">
            Upload
          </Button>
          <Button color="inherit" component={RouterLink} to="/login">
            Login
          </Button>
          <Button
            variant="contained"
            color="primary"
            component={RouterLink}
            to="/register"
            sx={{ ml: 2 }}
          >
            Sign Up
          </Button>
        </Toolbar>
      </Container>
    </AppBar>
  );
}

export default Navbar;
