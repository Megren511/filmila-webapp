import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  Button,
  CircularProgress,
  Alert,
} from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import { loadStripe } from '@stripe/stripe-js';
import {
  Elements,
  CardElement,
  useStripe,
  useElements,
} from '@stripe/react-stripe-js';

const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLIC_KEY);

// Payment form component
function PaymentForm({ film, onSuccess, onError }) {
  const stripe = useStripe();
  const elements = useElements();
  const [processing, setProcessing] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    
    if (!stripe || !elements) {
      return;
    }

    setProcessing(true);

    try {
      const response = await fetch('/api/create-payment-intent', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          film_id: film.id,
        }),
      });

      const data = await response.json();
      
      const { error, paymentIntent } = await stripe.confirmCardPayment(data.clientSecret, {
        payment_method: {
          card: elements.getElement(CardElement),
          billing_details: {
            name: 'User Name',
          },
        },
      });

      if (error) {
        onError(error.message);
      } else if (paymentIntent.status === 'succeeded') {
        onSuccess();
      }
    } catch (err) {
      onError('Payment failed. Please try again.');
    } finally {
      setProcessing(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <Box sx={{ mb: 2 }}>
        <CardElement
          options={{
            style: {
              base: {
                fontSize: '16px',
                color: '#424770',
                '::placeholder': {
                  color: '#aab7c4',
                },
              },
              invalid: {
                color: '#9e2146',
              },
            },
          }}
        />
      </Box>
      <Button
        type="submit"
        variant="contained"
        color="primary"
        disabled={!stripe || processing}
        fullWidth
      >
        {processing ? 'Processing...' : `Pay $${film.price}`}
      </Button>
    </form>
  );
}

function WatchFilm() {
  const { filmId } = useParams();
  const navigate = useNavigate();
  const [film, setFilm] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [hasPurchased, setHasPurchased] = useState(false);

  useEffect(() => {
    fetchFilmDetails();
    checkPurchaseStatus();
  }, [filmId]);

  const fetchFilmDetails = async () => {
    try {
      const response = await fetch(`/api/films/${filmId}`);
      if (!response.ok) throw new Error('Film not found');
      const data = await response.json();
      setFilm(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const checkPurchaseStatus = async () => {
    try {
      const response = await fetch(`/api/purchases/check/${filmId}`);
      const data = await response.json();
      setHasPurchased(data.purchased);
    } catch (err) {
      console.error('Error checking purchase status:', err);
    }
  };

  if (loading) {
    return (
      <Container sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
        <Button
          variant="contained"
          onClick={() => navigate('/')}
          sx={{ mt: 2 }}
        >
          Return to Home
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Paper sx={{ p: 4 }}>
        {hasPurchased ? (
          <Box>
            <Typography variant="h4" gutterBottom>
              {film.title}
            </Typography>
            <Box sx={{ position: 'relative', paddingTop: '56.25%', mt: 2 }}>
              <video
                controls
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: '100%',
                  height: '100%',
                }}
                src={`/api/watch/${filmId}`}
              />
            </Box>
            <Typography variant="body1" sx={{ mt: 2 }}>
              {film.description}
            </Typography>
          </Box>
        ) : (
          <Box>
            <Typography variant="h4" gutterBottom>
              Purchase "{film.title}"
            </Typography>
            <Typography variant="h6" color="primary" sx={{ mb: 2 }}>
              Price: ${film.price}
            </Typography>
            <Typography variant="body1" sx={{ mb: 3 }}>
              {film.description}
            </Typography>
            <Elements stripe={stripePromise}>
              <PaymentForm
                film={film}
                onSuccess={() => setHasPurchased(true)}
                onError={setError}
              />
            </Elements>
          </Box>
        )}
      </Paper>
    </Container>
  );
}

export default WatchFilm;
