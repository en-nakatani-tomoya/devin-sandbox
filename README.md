# FastAPI with Celery and Redis

This project implements a FastAPI application with Celery and Redis for background task processing.

## Features

- FastAPI API with a `/report` endpoint for submitting investigation requests
- Background processing using Celery with Redis as the message broker
- Docker Compose setup for easy deployment and development

## Getting Started

### Prerequisites

- Docker and Docker Compose

### Running the Application

1. Clone the repository
2. Start the services with Docker Compose:

```bash
docker-compose up --build
```

3. Access the API at http://localhost:8000
4. API documentation is available at http://localhost:8000/docs

## Architecture

- **FastAPI**: Handles HTTP requests and responses
- **Celery**: Processes background tasks
- **Redis**: Acts as a message broker and result backend for Celery

## Development

The project uses a mock OpenAI interface for development purposes. This can be replaced with the actual OpenAI API implementation when needed.
