# Docker Setup for Event Situational Awareness

This document explains how to run the Event Situational Awareness application using Docker.

## Prerequisites

- Docker Engine 20.10+ installed
- Docker Compose 1.29+ installed
- Google Gemini API key configured in `.env` file

## Quick Start

1. **Clone and navigate to the project directory**
   ```bash
   git clone <repository-url>
   cd Event_Situational_Awareness
   ```

2. **Configure environment variables**
   ```bash
   cp .env.template .env
   # Edit .env file and add your GOOGLE_API_KEY
   ```

3. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Open your browser to: http://localhost:8501
   - The Streamlit dashboard will be available

## Docker Services

### Main Application (`event-awareness`)
- **Image**: Built from local Dockerfile
- **Port**: 8501 (Streamlit application)
- **Volumes**: 
  - `./data:/app/data` - Persistent data storage
  - `./videos:/app/videos` - Video files for processing
  - `./.env:/app/.env` - Environment configuration
- **Dependencies**: Redis for caching

### Redis Cache (`redis`)
- **Image**: redis:7-alpine
- **Port**: 6379 (Redis server)
- **Volume**: `redis-data` for persistent cache storage
- **Purpose**: Improves performance for repeated queries

## Docker Commands

### Build and Start Services
```bash
# Build and start all services in detached mode
docker-compose up --build -d

# View logs
docker-compose logs -f event-awareness

# Stop services
docker-compose down

# Stop and remove volumes (careful: deletes data)
docker-compose down -v
```

### Development Commands
```bash
# Rebuild only the main application
docker-compose build event-awareness

# Start only the main service
docker-compose up event-awareness

# Execute commands in running container
docker-compose exec event-awareness bash

# View resource usage
docker-compose top
```

### Troubleshooting Commands
```bash
# Check service health
docker-compose ps

# View configuration
docker-compose config

# Check logs for errors
docker-compose logs event-awareness
docker-compose logs redis

# Restart services
docker-compose restart
```

## File Structure

```
Event_Situational_Awareness/
├── Dockerfile              # Main application container
├── docker-compose.yml      # Multi-service orchestration
├── .dockerignore           # Files to exclude from build
├── .env                    # Environment variables (create from .env.template)
├── data/                   # Persistent data (mounted as volume)
├── videos/                 # Video files (mounted as volume)
└── ...
```

## Environment Variables

The following environment variables can be configured in `.env`:

- `GOOGLE_API_KEY`: Your Google Gemini API key (required)

## Volumes and Persistence

- **Application Data**: `./data` directory is mounted to persist analysis results
- **Videos**: `./videos` directory is mounted to access video files
- **Redis Data**: Named volume `redis-data` persists cache between restarts

## Health Checks

Both services include health checks:
- **Main App**: HTTP check on Streamlit health endpoint
- **Redis**: Redis ping command

## Security Features

- Non-root user execution in main container
- Read-only mounting of sensitive files
- Network isolation with custom bridge network

## Scaling and Production

For production deployment:

1. **Use external Redis**:
   ```yaml
   # Remove redis service and update event-awareness environment
   environment:
     - REDIS_URL=redis://your-external-redis:6379
   ```

2. **Add reverse proxy** (nginx, traefik):
   ```yaml
   # Add labels for automatic SSL and routing
   labels:
     - "traefik.enable=true"
     - "traefik.http.routers.event-awareness.rule=Host(`yourdomain.com`)"
   ```

3. **Resource limits**:
   ```yaml
   deploy:
     resources:
       limits:
         memory: 2G
         cpus: '1.0'
   ```

## Common Issues

1. **Permission denied on Docker socket**:
   ```bash
   sudo usermod -aG docker $USER
   # Log out and back in
   ```

2. **Port already in use**:
   ```bash
   # Change port mapping in docker-compose.yml
   ports:
     - "8502:8501"  # Use different external port
   ```

3. **Out of memory**:
   ```bash
   # Add memory limits or increase Docker memory allocation
   docker system prune  # Clean up unused containers/images
   ```

4. **API key not working**:
   - Verify `.env` file exists and contains valid `GOOGLE_API_KEY`
   - Check container logs: `docker-compose logs event-awareness`

## Monitoring

Monitor the application with:
```bash
# Resource usage
docker stats

# Container health
docker-compose ps

# Application logs
docker-compose logs -f --tail=100 event-awareness