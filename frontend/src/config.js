const config = {
  apiUrl: process.env.NODE_ENV === 'production' 
    ? 'https://www.filmila.com/api'
    : 'http://localhost:5000/api',
  stripePublicKey: process.env.REACT_APP_STRIPE_PUBLIC_KEY
};

export default config;
