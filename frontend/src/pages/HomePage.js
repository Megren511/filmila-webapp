import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Card,
  CardContent,
  CardMedia,
  Typography,
  Button,
  Box,
  Chip,
} from '@mui/material';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function HomePage() {
  const [films, setFilms] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchFilms = async () => {
      try {
        const response = await axios.get('/api/films');
        setFilms(response.data);
      } catch (error) {
        console.error('Error fetching films:', error);
      }
    };
    fetchFilms();
  }, []);

  const handleWatchClick = (filmId) => {
    navigate(`/watch/${filmId}`);
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom sx={{ mb: 4 }}>
        Featured Films
      </Typography>
      <Grid container spacing={4}>
        {films.map((film) => (
          <Grid item key={film.id} xs={12} sm={6} md={4}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardMedia
                component="img"
                height="200"
                image={film.thumbnail_path || '/placeholder.jpg'}
                alt={film.title}
              />
              <CardContent sx={{ flexGrow: 1 }}>
                <Typography gutterBottom variant="h5" component="h2">
                  {film.title}
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  {film.description}
                </Typography>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 2 }}>
                  <Chip label={film.film_type} color="primary" size="small" />
                  <Typography variant="h6" color="primary">
                    ${film.price}
                  </Typography>
                </Box>
                <Button
                  fullWidth
                  variant="contained"
                  color="primary"
                  onClick={() => handleWatchClick(film.id)}
                  sx={{ mt: 2 }}
                >
                  Watch Now
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
}

export default HomePage;
