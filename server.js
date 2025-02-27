const express = require('express');
const path = require('path');
const { MongoClient } = require('mongodb');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
require('dotenv').config();

const app = express();

// Middleware
app.use(express.json());
app.use(express.static(path.join(__dirname, 'frontend/build')));

// MongoDB connection
const uri = process.env.MONGODB_URI;
if (!uri) {
  console.error('MONGODB_URI is not defined in .env file');
  process.exit(1);
}

console.log('Attempting to connect to MongoDB...');
const client = new MongoClient(uri);

async function connectToMongo() {
  try {
    await client.connect();
    console.log('Connected to MongoDB Atlas successfully');
    
    // Test the connection by listing databases
    const adminDb = client.db('admin');
    const result = await adminDb.command({ ping: 1 });
    console.log('MongoDB connection test result:', result);
    
  } catch (error) {
    console.error('Error connecting to MongoDB:', error);
    process.exit(1);
  }
}

connectToMongo();

// Registration endpoint
app.post('/api/register', async (req, res) => {
  try {
    const { email, password, is_filmmaker } = req.body;
    const db = client.db('filmila');
    const users = db.collection('users');

    // Check if user already exists
    const existingUser = await users.findOne({ email });
    if (existingUser) {
      return res.status(400).json({ message: 'User already exists' });
    }

    // Hash password
    const salt = await bcrypt.genSalt(10);
    const hashedPassword = await bcrypt.hash(password, salt);

    // Create new user
    const result = await users.insertOne({
      email,
      password: hashedPassword,
      isFilmmaker: is_filmmaker,
      createdAt: new Date()
    });

    // Create JWT token
    const token = jwt.sign(
      { userId: result.insertedId, isFilmmaker: is_filmmaker },
      process.env.JWT_SECRET || 'your-secret-key',
      { expiresIn: '24h' }
    );

    res.status(201).json({ token });
  } catch (error) {
    console.error('Registration error:', error);
    res.status(500).json({ message: 'Server error during registration' });
  }
});

// Login endpoint
app.post('/api/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    const db = client.db('filmila');
    const users = db.collection('users');

    // Find user by email
    const user = await users.findOne({ email });
    if (!user) {
      return res.status(400).json({ message: 'Invalid email or password' });
    }

    // Check password
    const isValidPassword = await bcrypt.compare(password, user.password);
    if (!isValidPassword) {
      return res.status(400).json({ message: 'Invalid email or password' });
    }

    // Create JWT token
    const token = jwt.sign(
      { userId: user._id, isFilmmaker: user.isFilmmaker },
      process.env.JWT_SECRET || 'your-secret-key',
      { expiresIn: '24h' }
    );

    res.json({ token });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ message: 'Server error during login' });
  }
});

// Handle any requests that don't match the above
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'frontend/build/index.html'));
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
