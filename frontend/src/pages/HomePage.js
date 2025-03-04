import React from 'react';
import { Container, Typography, Grid, Card, CardContent, CardMedia, Button } from '@mui/material';
import { styled } from '@mui/material/styles';

const HeroSection = styled('div')(({ theme }) => ({
  backgroundImage: 'linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url(https://source.unsplash.com/random/1920x1080/?film)',
  backgroundSize: 'cover',
  backgroundPosition: 'center',
  color: 'white',
  padding: theme.spacing(15, 0),
  textAlign: 'center',
  marginBottom: theme.spacing(6),
}));

const StyledCard = styled(Card)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  transition: 'transform 0.2s',
  '&:hover': {
    transform: 'scale(1.03)',
  },
}));

const featuredFilms = [
  {
    title: 'The Silent Echo',
    director: 'Sarah Chen',
    image: 'https://source.unsplash.com/random/800x600/?movie,cinema,1',
    description: 'A thought-provoking journey through silence and sound.',
  },
  {
    title: 'Urban Dreams',
    director: 'Michael Torres',
    image: 'https://source.unsplash.com/random/800x600/?movie,cinema,2',
    description: 'The story of hope in the heart of the city.',
  },
  {
    title: "Nature's Whisper",
    director: 'Emma Wilson',
    image: 'https://source.unsplash.com/random/800x600/?movie,cinema,3',
    description: 'A mesmerizing documentary about hidden wonders.',
  },
];

function HomePage() {
  return (
    <>
      <HeroSection>
        <Container>
          <Typography variant="h2" component="h1" gutterBottom>
            Welcome to Filmila
          </Typography>
          <Typography variant="h5" paragraph>
            Discover and support independent filmmakers
          </Typography>
          <Button variant="contained" color="primary" size="large">
            Explore Films
          </Button>
        </Container>
      </HeroSection>

      <Container>
        <Typography variant="h3" component="h2" gutterBottom align="center" sx={{ mb: 6 }}>
          Featured Films
        </Typography>
        <Typography variant="h5" component="h3" gutterBottom align="center" sx={{ mb: 4 }}>
          Coming Soon
        </Typography>
        <Grid container spacing={4}>
          {featuredFilms.map((film, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <StyledCard>
                <CardMedia
                  component="img"
                  height="300"
                  image={film.image}
                  alt={film.title}
                />
                <CardContent>
                  <Typography gutterBottom variant="h5" component="h2">
                    {film.title}
                  </Typography>
                  <Typography variant="subtitle1" color="text.secondary" gutterBottom>
                    Directed by {film.director}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {film.description}
                  </Typography>
                </CardContent>
              </StyledCard>
            </Grid>
          ))}
        </Grid>

        <div style={{ textAlign: 'center', margin: '4rem 0' }}>
          <Typography variant="h4" gutterBottom>
            Are you a filmmaker?
          </Typography>
          <Typography variant="subtitle1" paragraph>
            Share your vision with the world. Upload your films and reach a global audience.
          </Typography>
          <Button variant="outlined" color="primary" size="large">
            Start Uploading
          </Button>
        </div>
      </Container>
    </>
  );
}

export default HomePage;