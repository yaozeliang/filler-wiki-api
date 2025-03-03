# Filler Wiki API

A FastAPI-based REST API for managing a knowledge base of filler products.

## Technology Stack

- **Framework:** FastAPI
- **Database:** MongoDB Atlas
- **Authentication:** JWT (JSON Web Tokens)
- **Python Version:** 3.10+
- **Package Manager:** PDM

## Features

- **Authentication System**
  - User registration with password validation
  - JWT token-based authentication
  - Secure password hashing with bcrypt
  - Role-based access control foundation

- **Brand Management**
  - CRUD operations for filler brands
  - Filtering and searching capabilities
  - Export data in multiple formats (JSON, CSV, Excel)
  - Pagination support

- **Security**
  - Password complexity validation
  - Environment-based configuration
  - Proper error handling
  - Comprehensive logging

## Prerequisites

- Python 3.10 or higher
- PDM (Python package manager)
- MongoDB Atlas account or local MongoDB instance
- Docker (optional)



## API Documentation

Once the server is running, you can access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Authentication Flow

1. Register a new user:
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Test123!@#"
  }'
```

2. Get an access token:
```bash
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=Test123!@#"
```

3. Use the token for authenticated endpoints:
```bash
curl -X GET "http://localhost:8000/brands" \
  -H "Authorization: Bearer your_access_token_here"
```

## Project Structure

```
filler-wiki-api/
├── app/
│   ├── core/
│   │   ├── auth.py          # Authentication logic
│   │   ├── config.py        # Configuration settings
│   │   ├── crud.py          # Database operations
│   │   ├── database.py      # Database connection
│   │   ├── description.py   # API description
│   │   ├── enums.py         # Enumerations
│   │   ├── logging.py       # Logging configuration
│   │   ├── models/          # Pydantic models
│   │   └── security.py      # Security utilities
│   ├── routes/
│   │   ├── auth.py          # Authentication routes
│   │   └── brand.py         # Brand routes
│   └── main.py              # Application entry point
├── scripts/
│   └── init_collections.py  # Database initialization
├── logs/                    # Log files
├── .env                     # Environment variables
├── .gitignore               # Git ignore file
├── pyproject.toml           # PDM project file
└── README.md                # Project documentation
```

## Deployment

### Docker

```bash
docker build -t filler-wiki-api .
docker run -p 8000:8000 -e JWT_SECRET_KEY=your_secret filler-wiki-api
```

### Cloud Deployment

For cloud deployment, make sure to:
1. Store JWT_SECRET_KEY in your cloud provider's secret management
2. Configure MongoDB connection string for production
3. Set ENVIRONMENT=production

## License

[MIT](LICENSE)

## Support

For technical support, please contact:
- **Developer**: Zeliang YAO
- **Email**: zeliang.yao_filler@2925.com
- **Website**: [hephaestus.fr](https://hephaestus.fr)
