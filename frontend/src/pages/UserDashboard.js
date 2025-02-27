import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Grid,
  Paper,
  Button,
  Box,
  List,
  ListItem,
  ListItemText,
  Divider,
  Card,
  CardContent,
  CardMedia,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import MovieIcon from '@mui/icons-material/Movie';
import PersonIcon from '@mui/icons-material/Person';
import { useNavigate } from 'react-router-dom';

const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  height: '100%',
}));

const UploadButton = styled(Button)(({ theme }) => ({
  marginTop: theme.spacing(2),
}));

function UserDashboard() {
  const navigate = useNavigate();
  const [userFilms, setUserFilms] = useState([]);
  const [userData, setUserData] = useState(null);

  useEffect(() => {
    // Fetch user data and films
    // This is a placeholder - implement actual API calls
    const fetchData = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          navigate('/login');
          return;
        }

        // Fetch user data
        const userResponse = await fetch('/api/user', {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
        const userData = await userResponse.json();
        setUserData(userData);

        // If user is a filmmaker, fetch their films
        if (userData.is_filmmaker) {
          const filmsResponse = await fetch('/api/user/films', {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          });
          const filmsData = await filmsResponse.json();
          setUserFilms(filmsData);
        }
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, [navigate]);

  const handleUpload = () => {
    // Implement film upload logic
    console.log('Upload film clicked');
  };

  const handleEditProfile = () => {
    // Implement profile edit logic
    console.log('Edit profile clicked');
  };

  return (
    <Container sx={{ py: 8 }}>
      <Typography variant="h4" gutterBottom>
        Welcome, {userData?.name || 'Filmmaker'}!
      </Typography>

      <Grid container spacing={4}>
        {/* Profile Section */}
        <Grid item xs={12} md={4}>
          <StyledPaper>
            <Typography variant="h6" gutterBottom>
              Profile
            </Typography>
            <List>
              <ListItem>
                <ListItemText
                  primary="Email"
                  secondary={userData?.email || 'Loading...'}
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Account Type"
                  secondary={userData?.is_filmmaker ? 'Filmmaker' : 'Viewer'}
                />
              </ListItem>
            </List>
            <Button
              variant="outlined"
              startIcon={<PersonIcon />}
              fullWidth
              onClick={handleEditProfile}
            >
              Edit Profile
            </Button>
          </StyledPaper>
        </Grid>

        {/* Filmmaker Section */}
        {userData?.is_filmmaker && (
          <Grid item xs={12} md={8}>
            <StyledPaper>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6">
                  My Films
                </Typography>
                <UploadButton
                  variant="contained"
                  startIcon={<CloudUploadIcon />}
                  onClick={handleUpload}
                >
                  Upload New Film
                </UploadButton>
              </Box>

              {userFilms.length > 0 ? (
                <Grid container spacing={3}>
                  {userFilms.map((film) => (
                    <Grid item xs={12} sm={6} key={film.id}>
                      <Card>
                        <CardMedia
                          component="img"
                          height="140"
                          image={film.thumbnail}
                          alt={film.title}
                        />
                        <CardContent>
                          <Typography variant="h6" gutterBottom>
                            {film.title}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Views: {film.views}
                          </Typography>
                          <Button
                            variant="outlined"
                            size="small"
                            startIcon={<MovieIcon />}
                            sx={{ mt: 1 }}
                            onClick={() => navigate(`/films/${film.id}`)}
                          >
                            View Film
                          </Button>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              ) : (
                <Typography color="text.secondary" align="center">
                  You haven't uploaded any films yet.
                </Typography>
              )}
            </StyledPaper>
          </Grid>
        )}

        {/* Viewer Section */}
        {!userData?.is_filmmaker && (
          <Grid item xs={12} md={8}>
            <StyledPaper>
              <Typography variant="h6" gutterBottom>
                Recently Watched
              </Typography>
              <Typography color="text.secondary" align="center">
                Your watch history will appear here.
              </Typography>
            </StyledPaper>
          </Grid>
        )}
      </Grid>
    </Container>
  );
}

export default UserDashboard;
