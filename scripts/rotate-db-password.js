const { MongoClient } = require('mongodb');
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

async function rotatePassword() {
    try {
        // Generate a new secure password
        const newPassword = crypto.randomBytes(32).toString('base64')
            .replace(/[+/=]/g, '')  // Remove special chars
            .substring(0, 24);      // Keep reasonable length

        const uri = process.env.MONGODB_URI;
        const client = new MongoClient(uri);

        await client.connect();
        
        // Update the user's password in MongoDB
        const db = client.db('admin');
        await db.command({
            updateUser: "megrenfilms",
            pwd: newPassword
        });

        // Update .env file with new connection string
        const envPath = path.join(__dirname, '..', '.env');
        let envContent = fs.readFileSync(envPath, 'utf8');
        
        // Replace old connection string with new one
        const newUri = process.env.MONGODB_URI.replace(
            /mongodb\+srv:\/\/megrenfilms:([^@]+)@/,
            `mongodb+srv://megrenfilms:${newPassword}@`
        );
        
        envContent = envContent.replace(
            /MONGODB_URI=.*/,
            `MONGODB_URI=${newUri}`
        );

        fs.writeFileSync(envPath, envContent);

        console.log('Password rotated successfully!');
        console.log('New connection string has been updated in .env');
        
        await client.close();
    } catch (error) {
        console.error('Error rotating password:', error);
        process.exit(1);
    }
}

rotatePassword();
