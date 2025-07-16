# MongoDB Docker Setup

This document describes the MongoDB configuration for the FastAPI application using Docker Compose.

## Configuration Overview

The application now uses MongoDB running in a Docker container with the following setup:

### Docker Services

1. **MongoDB Container** (`mongo`):
   - Image: `mongo:latest`
   - Port: `27017:27017`
   - Database: `elise_db`
   - Username: `elise`
   - Password: `elise_can_open_doors`

2. **Redis Container** (`redis`):
   - Image: `redis:latest`
   - Port: `6379:6379`

3. **FastAPI Container** (`fastapi`):
   - Depends on both MongoDB and Redis
   - Uses environment variables from `.env` file

### Environment Variables

Update your `.env` file with the following MongoDB configuration:

```env
MONGO_URI=mongodb://elise:elise_can_open_doors@mongo:27017/elise_db?authSource=elise_db
MONGO_DB_NAME=elise_db
ROOT_PATH=/elise
```

### Database Initialization

The MongoDB container automatically runs the `mongo-init.js` script on first startup, which:

1. Creates the `elise_db` database
2. Creates a user with read/write permissions
3. Creates the required collections:
   - `patients`
   - `consultations`
   - `temp_files`
4. Sets up indexes for better performance

### Running the Application

#### Development Mode
```bash
docker-compose up --build
```

#### Production Mode (with HTTPS)
```bash
docker-compose -f docker-compose.https.yml up --build
```

### Connecting to MongoDB

#### From within Docker containers:
- Host: `mongo` (service name)
- Port: `27017`
- Database: `elise_db`
- Username: `elise`
- Password: `elise_can_open_doors`

#### From host machine:
- Host: `localhost`
- Port: `27017`
- Database: `elise_db`
- Username: `elise`
- Password: `elise_can_open_doors`

### Testing the Connection

You can test the MongoDB connection using the provided test script:

```bash
python test_mongo.py
```

### Data Persistence

MongoDB data is persisted using Docker volumes:
- Volume name: `mongo_data`
- Location: `/data/db` inside the container

### Security Notes

1. The MongoDB container is configured with authentication enabled
2. The default credentials should be changed in production
3. Consider using Docker secrets for sensitive data in production
4. The MongoDB port is exposed to the host for development purposes

### Troubleshooting

1. **Connection refused**: Ensure the MongoDB container is running
2. **Authentication failed**: Check the credentials in the `.env` file
3. **Database not found**: The database is created automatically on first startup
4. **Permission denied**: Ensure the MongoDB initialization script ran successfully

### Production Considerations

For production deployment:

1. Change default passwords
2. Use Docker secrets for sensitive data
3. Configure MongoDB with proper security settings
4. Set up regular backups
5. Consider using MongoDB Atlas or a managed MongoDB service
6. Remove port exposure to host if not needed 