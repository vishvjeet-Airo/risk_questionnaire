# Authentication Setup

This document describes the authentication system implemented for the Risk Questionnaire AI Scanner.

## Features

- User registration and login
- JWT-based authentication
- Password hashing with bcrypt
- Password reset functionality
- User role management
- SQLModel integration with SQLite database

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements_auth.txt
```

2. Create a `.env` file in the project root (optional):
```env
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=sqlite:///./risk_questionnaire.db
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Running the Application

1. Start the FastAPI server:
```bash
uvicorn main:app --reload
```

2. The API will be available at `http://localhost:8000`
3. API documentation will be available at `http://localhost:8000/docs`

## Authentication Endpoints

### 1. User Sign Up
- **POST** `/api/auth/signup`
- **Body**: `{"name": "John Doe", "email": "john@example.com", "password": "password123", "confirm_password": "password123"}`
- **Response**: `{"message": "User registered successfully"}`

### 2. User Sign In
- **POST** `/api/auth/signin`
- **Body**: `{"email": "john@example.com", "password": "password123"}`
- **Response**: `{"access_token": "jwt_token", "token_type": "bearer", "expires_in": 1800, "user": {...}}`

### 3. Forgot Password
- **POST** `/api/auth/forgot-password`
- **Body**: `{"email": "john@example.com"}`
- **Response**: `{"message": "Password reset email sent"}`

### 4. User Logout
- **POST** `/api/auth/logout`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `{"message": "Successfully logged out"}`

## Testing

Run the test script to verify all endpoints:
```bash
python test_auth.py
```

Make sure the FastAPI server is running before executing the test script.

## Database

The application uses SQLite by default. The database file will be created automatically at `./risk_questionnaire.db`.

### User Model
- `id`: Primary key
- `name`: User's full name
- `email`: Unique email address
- `hashed_password`: Bcrypt hashed password
- `role`: User role (admin/user)
- `is_active`: Account status
- `created_at`: Account creation timestamp
- `updated_at`: Last update timestamp
- `last_login`: Last login timestamp

## Security Features

- Passwords are hashed using bcrypt
- JWT tokens for stateless authentication
- Token expiration (30 minutes by default)
- Password confirmation validation
- Email format validation
- User account activation status

## Configuration

All configuration is handled through the `app/core/config.py` file. Key settings:

- `secret_key`: JWT signing key
- `algorithm`: JWT algorithm (HS256)
- `access_token_expire_minutes`: Token expiration time
- `database_url`: Database connection string

## Next Steps

1. Implement email sending for password reset
2. Add user profile management endpoints
3. Implement refresh token mechanism
4. Add rate limiting for authentication endpoints
5. Add audit logging for security events
