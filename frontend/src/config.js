const config = {
  apiUrl: process.env.NODE_ENV === 'production' 
    ? 'https://sea-turtle-app-879b6.ondigitalocean.app/api' // Production API URL
    : 'http://localhost:8080/api'  // Development API URL
};

export default config;
