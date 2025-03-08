import React from 'react';
import { Container, Typography, Grid, Card, CardContent, Box, Button } from '@mui/material';
import { styled } from '@mui/material/styles';
import { Link } from 'react-router-dom';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import MonetizationOnIcon from '@mui/icons-material/MonetizationOn';

const StyledCard = styled(Card)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  padding: theme.spacing(3),
  transition: 'transform 0.2s',
  '&:hover': {
    transform: 'scale(1.03)',
  },
}));

const DashboardSection = styled('div')(({ theme }) => ({
  padding: theme.spacing(4, 0),
}));

function FilmmakerDashboard() {
  const mockRevenue = {
    totalRevenue: 1250.00,
    monthlyRevenue: 450.00,
    totalViews: 325,
  };

  return (
    <Container>
      <DashboardSection>
        <Typography variant="h4" component="h1" gutterBottom>
          Filmmaker Dashboard
        </Typography>
        
        <Grid container spacing={4}>
          <Grid item xs={12} md={6}>
            <StyledCard>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <MonetizationOnIcon fontSize="large" color="primary" />
                  <Typography variant="h5" ml={2}>Revenue Overview</Typography>
                </Box>
                <Typography variant="body1" gutterBottom>
                  Total Revenue: ${mockRevenue.totalRevenue.toFixed(2)}
                </Typography>
                <Typography variant="body1" gutterBottom>
                  Monthly Revenue: ${mockRevenue.monthlyRevenue.toFixed(2)}
                </Typography>
                <Typography variant="body1">
                  Total Views: {mockRevenue.totalViews}
                </Typography>
              </CardContent>
            </StyledCard>
          </Grid>

          <Grid item xs={12} md={6}>
            <StyledCard>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <UploadFileIcon fontSize="large" color="primary" />
                  <Typography variant="h5" ml={2}>Upload New Film</Typography>
                </Box>
                <Typography variant="body1" gutterBottom>
                  Share your creative work with the world. Upload your film and set your price.
                </Typography>
                <Box mt={2}>
                  <Button
                    component={Link}
                    to="/upload"
                    variant="contained"
                    color="primary"
                    startIcon={<UploadFileIcon />}
                  >
                    Upload Film
                  </Button>
                </Box>
              </CardContent>
            </StyledCard>
          </Grid>
        </Grid>
      </DashboardSection>
    </Container>
  );
}

export default FilmmakerDashboard;
