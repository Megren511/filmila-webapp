import React, { useState } from 'react';
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Box,
  MenuItem,
  Alert,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

const filmTypes = [
  'Short Film',
  'Documentary',
  'Animation',
  'Experimental',
  'Music Video',
  'Drama',
  'Comedy',
  'Horror',
];

function FilmUpload() {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    price: '',
    filmType: '',
    file: null,
    thumbnail: null,
  });
  const [status, setStatus] = useState({ type: '', message: '' });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleFileChange = (e, type) => {
    const file = e.target.files[0];
    setFormData((prev) => ({
      ...prev,
      [type]: file,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const formDataToSend = new FormData();
      Object.keys(formData).forEach(key => {
        formDataToSend.append(key, formData[key]);
      });

      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formDataToSend,
      });

      if (response.ok) {
        setStatus({
          type: 'success',
          message: 'Film uploaded successfully!',
        });
        setFormData({
          title: '',
          description: '',
          price: '',
          filmType: '',
          file: null,
          thumbnail: null,
        });
      } else {
        throw new Error('Upload failed');
      }
    } catch (error) {
      setStatus({
        type: 'error',
        message: 'Failed to upload film. Please try again.',
      });
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Paper sx={{ p: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Upload Your Film
        </Typography>

        {status.message && (
          <Alert severity={status.type} sx={{ mb: 2 }}>
            {status.message}
          </Alert>
        )}

        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
          <TextField
            fullWidth
            label="Film Title"
            name="title"
            value={formData.title}
            onChange={handleInputChange}
            margin="normal"
            required
          />

          <TextField
            fullWidth
            label="Description"
            name="description"
            value={formData.description}
            onChange={handleInputChange}
            margin="normal"
            multiline
            rows={4}
            required
          />

          <TextField
            fullWidth
            label="Price ($)"
            name="price"
            type="number"
            value={formData.price}
            onChange={handleInputChange}
            margin="normal"
            required
            inputProps={{ min: 0, step: 0.01 }}
          />

          <TextField
            fullWidth
            select
            label="Film Type"
            name="filmType"
            value={formData.filmType}
            onChange={handleInputChange}
            margin="normal"
            required
          >
            {filmTypes.map((type) => (
              <MenuItem key={type} value={type}>
                {type}
              </MenuItem>
            ))}
          </TextField>

          <Box sx={{ mt: 3, mb: 2 }}>
            <input
              accept="video/*"
              style={{ display: 'none' }}
              id="film-file"
              type="file"
              onChange={(e) => handleFileChange(e, 'file')}
            />
            <label htmlFor="film-file">
              <Button
                variant="contained"
                component="span"
                startIcon={<CloudUploadIcon />}
                fullWidth
              >
                Upload Film File
              </Button>
            </label>
            {formData.file && (
              <Typography variant="body2" sx={{ mt: 1 }}>
                Selected file: {formData.file.name}
              </Typography>
            )}
          </Box>

          <Box sx={{ mt: 2, mb: 2 }}>
            <input
              accept="image/*"
              style={{ display: 'none' }}
              id="thumbnail-file"
              type="file"
              onChange={(e) => handleFileChange(e, 'thumbnail')}
            />
            <label htmlFor="thumbnail-file">
              <Button
                variant="outlined"
                component="span"
                startIcon={<CloudUploadIcon />}
                fullWidth
              >
                Upload Thumbnail
              </Button>
            </label>
            {formData.thumbnail && (
              <Typography variant="body2" sx={{ mt: 1 }}>
                Selected thumbnail: {formData.thumbnail.name}
              </Typography>
            )}
          </Box>

          <Button
            type="submit"
            variant="contained"
            color="primary"
            size="large"
            fullWidth
            sx={{ mt: 3 }}
          >
            Upload Film
          </Button>
        </Box>
      </Paper>
    </Container>
  );
}

export default FilmUpload;
