import React, { useState } from 'react';
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardMedia,
  Button,
  TextField,
  Box,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { useNavigate } from 'react-router-dom';

const StyledCard = styled(Card)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  transition: 'transform 0.2s',
  '&:hover': {
    transform: 'scale(1.02)',
  },
}));

const FilmImage = styled(CardMedia)({
  paddingTop: '56.25%', // 16:9 aspect ratio
});

// Temporary data - replace with API call
const films = [
  {
    id: 1,
    title: 'The Silent Echo',
    filmmaker: 'Sarah Chen',
    genre: 'Drama',
    duration: '15 min',
    description: 'A thought-provoking journey through silence and sound.',
    image: 'https://source.unsplash.com/random/800x600/?movie,1',
  },
  {
    id: 2,
    title: 'Urban Dreams',
    filmmaker: 'Michael Torres',
    genre: 'Documentary',
    duration: '20 min',
    description: 'The story of hope in the heart of the city.',
    image: 'https://source.unsplash.com/random/800x600/?movie,2',
  },
  // Add more films as needed
];

const genres = ['All', 'Drama', 'Comedy', 'Documentary', 'Animation', 'Experimental'];
const durations = ['All', 'Under 10 min', '10-20 min', '20-30 min', 'Over 30 min'];

function FilmsPage() {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedGenre, setSelectedGenre] = useState('All');
  const [selectedDuration, setSelectedDuration] = useState('All');

  const handleFilmClick = (filmId) => {
    navigate(`/films/${filmId}`);
  };

  // Filter films based on search term and filters
  const filteredFilms = films.filter((film) => {
    const matchesSearch = film.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      film.filmmaker.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesGenre = selectedGenre === 'All' || film.genre === selectedGenre;
    const matchesDuration = selectedDuration === 'All'; // Add duration logic as needed
    return matchesSearch && matchesGenre && matchesDuration;
  });

  return (
    <Container sx={{ py: 8 }}>
      <Typography variant="h3" component="h1" gutterBottom align="center">
        Explore Short Films
      </Typography>

      {/* Search and Filter Section */}
      <Box sx={{ mb: 6 }}>
        <Grid container spacing={3} alignItems="center">
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Search films"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Genre</InputLabel>
              <Select
                value={selectedGenre}
                label="Genre"
                onChange={(e) => setSelectedGenre(e.target.value)}
              >
                {genres.map((genre) => (
                  <MenuItem key={genre} value={genre}>{genre}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Duration</InputLabel>
              <Select
                value={selectedDuration}
                label="Duration"
                onChange={(e) => setSelectedDuration(e.target.value)}
              >
                {durations.map((duration) => (
                  <MenuItem key={duration} value={duration}>{duration}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Box>

      {/* Films Grid */}
      <Grid container spacing={4}>
        {filteredFilms.map((film) => (
          <Grid item key={film.id} xs={12} sm={6} md={4}>
            <StyledCard onClick={() => handleFilmClick(film.id)}>
              <FilmImage
                image={film.image}
                title={film.title}
              />
              <CardContent>
                <Typography gutterBottom variant="h6" component="h2">
                  {film.title}
                </Typography>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  by {film.filmmaker}
                </Typography>
                <Box sx={{ mb: 2 }}>
                  <Chip label={film.genre} size="small" sx={{ mr: 1 }} />
                  <Chip label={film.duration} size="small" />
                </Box>
                <Typography variant="body2" color="text.secondary">
                  {film.description}
                </Typography>
              </CardContent>
            </StyledCard>
          </Grid>
        ))}
      </Grid>

      {filteredFilms.length === 0 && (
        <Box sx={{ textAlign: 'center', mt: 4 }}>
          <Typography variant="h6" color="text.secondary">
            No films found matching your criteria
          </Typography>
        </Box>
      )}
    </Container>
  );
}

export default FilmsPage;
