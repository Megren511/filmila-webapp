const config = {
  development: {
    apiBaseUrl: 'http://localhost:8080/api'
  },
  production: {
    apiBaseUrl: 'https://filmila-webapp.onrender.com/api'
  }
};

export default config[process.env.NODE_ENV || 'development'];
