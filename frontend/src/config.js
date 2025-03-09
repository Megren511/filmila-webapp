const config = {
  development: {
    apiBaseUrl: 'http://localhost:8080/api'
  },
  production: {
    apiBaseUrl: 'https://sea-turtle-app-879b6.ondigitalocean.app/api'
  }
};

export default config[process.env.NODE_ENV || 'development'];
