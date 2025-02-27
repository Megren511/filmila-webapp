import React from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  Paper,
  Grid,
  Avatar,
  Chip,
  Divider,
} from '@mui/material';
import { useParams } from 'react-router-dom';
import { styled } from '@mui/material/styles';
import MonetizationOnIcon from '@mui/icons-material/MonetizationOn';
import ShareIcon from '@mui/icons-material/Share';

const VideoPlayer = styled(Paper)(({ theme }) => ({
  position: 'relative',
  paddingTop: '56.25%', // 16:9 aspect ratio
  backgroundColor: theme.palette.grey[900],
  marginBottom: theme.spacing(4),
}));

const VideoIframe = styled('iframe')({
  position: 'absolute',
  top: 0,
  left: 0,
  width: '100%',
  height: '100%',
  border: 0,
});

const FilmmakerCard = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  marginTop: theme.spacing(4),
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(2),
}));

function FilmDetailsPage() {
  const { id } = useParams();

  // Temporary data - replace with API call
  const film = {
    id,
    title: 'The Silent Echo',
    filmmaker: 'Sarah Chen',
    filmmakerAvatar: 'https://source.unsplash.com/random/100x100/?portrait',
    genre: 'Drama',
    duration: '15 min',
    description: `A thought-provoking journey through silence and sound. This short film explores the 
    relationship between urban isolation and human connection in the modern world. Through stunning 
    cinematography and a carefully crafted soundscape, the film takes viewers on an emotional journey 
    that questions our relationship with silence in an increasingly noisy world.`,
    videoUrl: 'https://www.youtube.com/embed/dQw4w9WgXcQ', // Replace with actual video URL
    price: 4.99,
    tags: ['Drama', 'Urban Life', 'Sound Design', 'Independent Film'],
  };

  const handleSupport = () => {
    // Implement payment/support logic
    console.log('Support filmmaker clicked');
  };

  const handleShare = () => {
    // Implement share logic
    console.log('Share clicked');
  };

  return (
    <Container maxWidth="lg" sx={{ py: 8 }}>
      <Typography variant="h3" component="h1" gutterBottom>
        {film.title}
      </Typography>

      <VideoPlayer elevation={3}>
        <VideoIframe
          src={film.videoUrl}
          title={film.title}
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
        />
      </VideoPlayer>

      <Grid container spacing={4}>
        <Grid item xs={12} md={8}>
          <Typography variant="h5" gutterBottom>
            About the Film
          </Typography>
          <Typography variant="body1" paragraph>
            {film.description}
          </Typography>

          <Box sx={{ my: 3 }}>
            {film.tags.map((tag) => (
              <Chip
                key={tag}
                label={tag}
                sx={{ mr: 1, mb: 1 }}
                variant="outlined"
              />
            ))}
          </Box>

          <Divider sx={{ my: 4 }} />

          <FilmmakerCard>
            <Avatar
              src={film.filmmakerAvatar}
              sx={{ width: 64, height: 64 }}
            />
            <Box>
              <Typography variant="subtitle1" fontWeight="bold">
                {film.filmmaker}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Independent Filmmaker
              </Typography>
            </Box>
          </FilmmakerCard>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Support the Filmmaker
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Your support helps independent filmmakers continue creating amazing content.
            </Typography>
            <Button
              variant="contained"
              color="primary"
              fullWidth
              startIcon={<MonetizationOnIcon />}
              onClick={handleSupport}
              sx={{ mb: 2 }}
            >
              Support for ${film.price}
            </Button>
            <Button
              variant="outlined"
              fullWidth
              startIcon={<ShareIcon />}
              onClick={handleShare}
            >
              Share Film
            </Button>
          </Paper>

          <Paper sx={{ p: 3, mt: 3 }}>
            <Typography variant="subtitle2" gutterBottom>
              Film Details
            </Typography>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2" color="text.secondary">
                Genre
              </Typography>
              <Typography variant="body2">
                {film.genre}
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="body2" color="text.secondary">
                Duration
              </Typography>
              <Typography variant="body2">
                {film.duration}
              </Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
}

export default FilmDetailsPage;
