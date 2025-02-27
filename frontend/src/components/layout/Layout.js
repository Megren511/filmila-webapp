import React from 'react';
import { AppBar, Toolbar, Typography, Button, Container, Box } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { styled } from '@mui/material/styles';

const StyledAppBar = styled(AppBar)(({ theme }) => ({
  backgroundColor: theme.palette.background.default,
  color: theme.palette.text.primary,
  boxShadow: 'none',
  borderBottom: `1px solid ${theme.palette.divider}`,
}));

const Logo = styled(Typography)(({ theme }) => ({
  fontWeight: 700,
  color: theme.palette.primary.main,
  textDecoration: 'none',
  '&:hover': {
    color: theme.palette.primary.dark,
  },
}));

const NavButton = styled(Button)(({ theme }) => ({
  marginLeft: theme.spacing(2),
}));

const Footer = styled('footer')(({ theme }) => ({
  backgroundColor: theme.palette.background.paper,
  padding: theme.spacing(6, 0),
  marginTop: 'auto',
  borderTop: `1px solid ${theme.palette.divider}`,
}));

function Layout({ children }) {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <StyledAppBar position="static">
        <Toolbar>
          <RouterLink to="/" style={{ textDecoration: 'none', flexGrow: 1 }}>
            <Logo variant="h6">Filmila</Logo>
          </RouterLink>
          <NavButton component={RouterLink} to="/" color="inherit">
            Home
          </NavButton>
          <NavButton component={RouterLink} to="/films" color="inherit">
            Films
          </NavButton>
          <NavButton component={RouterLink} to="/login" color="inherit">
            Login
          </NavButton>
          <NavButton
            component={RouterLink}
            to="/signup"
            variant="contained"
            color="primary"
          >
            Sign Up
          </NavButton>
        </Toolbar>
      </StyledAppBar>

      <Box component="main" sx={{ flexGrow: 1 }}>
        {children}
      </Box>

      <Footer>
        <Container maxWidth="lg">
          <Box sx={{ display: 'flex', justifyContent: 'center', gap: 4 }}>
            <Button component={RouterLink} to="/about" color="inherit">
              About Us
            </Button>
            <Button component={RouterLink} to="/contact" color="inherit">
              Contact
            </Button>
            <Button component={RouterLink} to="/terms" color="inherit">
              Terms of Service
            </Button>
            <Button component={RouterLink} to="/privacy" color="inherit">
              Privacy Policy
            </Button>
          </Box>
        </Container>
      </Footer>
    </Box>
  );
}

export default Layout;
