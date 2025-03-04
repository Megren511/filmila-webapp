const config = {
  apiUrl: process.env.NODE_ENV === 'production' 
    ? 'https://filmila-webapp.onrender.com/api' // Production API URL
    : 'http://localhost:8080/api'  // Development API URL
};

export default config;
