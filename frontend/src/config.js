const config = {
  apiUrl: process.env.NODE_ENV === 'production' 
    ? '/api' // Production API URL
    : '/api'  // Development API URL (will be proxied to http://localhost:8080/api)
};

export default config;
