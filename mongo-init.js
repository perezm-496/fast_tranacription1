// MongoDB initialization script
// This script runs when the MongoDB container starts for the first time

// Switch to the elise_db database
db = db.getSiblingDB('elise_db');

// Create a user for the elise_db database
db.createUser({
  user: 'elise',
  pwd: 'elise_can_open_doors',
  roles: [
    {
      role: 'readWrite',
      db: 'elise_db'
    }
  ]
});

// Create collections that will be used by the application
db.createCollection('patients');
db.createCollection('consultations');
db.createCollection('temp_files');

// Create indexes for better performance
db.consultations.createIndex({ "consultation_id": 1 }, { unique: true });
db.temp_files.createIndex({ "file_id": 1 }, { unique: true });

print('MongoDB initialization completed successfully!'); 