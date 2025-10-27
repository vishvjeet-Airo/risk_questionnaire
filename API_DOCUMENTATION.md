# Risk Questionnaire AI Scanner API Documentation

## Base URL
```
{Not Deployed}

if running on locally:
http://localhost:8000/api
```

## Authentication
All endpoints (except auth endpoints) require authentication via Bearer token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

---

## Authentication Endpoints

### 1. User Sign In
**POST** `/auth/signin`

**Description:** Authenticate user and return JWT token

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

**Status Codes:**
- `200` - Success
- `401` - Invalid credentials
- `422` - Validation error

---

### 2. User Sign Up
**POST** `/auth/signup`

**Description:** Register a new user account

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "user@example.com",
  "password": "password123",
  "confirm_password": "password123"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

**Status Codes:**
- `201` - User created successfully
- `400` - Email already exists
- `422` - Validation error

---

### 3. Forgot Password
**POST** `/auth/forgot-password`

**Description:** Send password reset email

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "Password reset email sent"
}
```

**Status Codes:**
- `200` - Email sent successfully
- `404` - Email not found
- `422` - Validation error

---

### 4. User Logout
**POST** `/auth/logout`

**Description:** Invalidate user session

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized

---

## Dashboard Endpoints

### 5. Dashboard Statistics
**GET** `/dashboard/stats`

**Description:** Get dashboard statistics including total clients, completed questionnaires, and unique questions

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "total_clients": 150,
  "completed_questionnaires": 89,
  "draft_questionnaires": 12,
  "unique_questions": 45,
  "total_uploads": 234
}
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized

---

### 6. Draft Questionnaires
**GET** `/dashboard/draft_questionnaires`

**Description:** Get paginated list of draft questionnaires

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 10)
- `search` (optional): Search by client name or questionnaire title
- `date_from` (optional): Filter from date (ISO format)
- `date_to` (optional): Filter to date (ISO format)

**Response:**
```json
{
  "questionnaires": [
    {
      "id": 1,
      "client_name": "ABC Corp",
      "title": "Risk Assessment Q1 2024",
      "sectors": ["Technology", "Finance"],
      "technologies": ["AI", "Cloud"],
      "created_at": "2024-01-15T10:30:00Z",
      "status": "draft"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 25,
    "pages": 3
  }
}
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized

---

### 7. Completed Questionnaires
**GET** `/dashboard/completed_questionnaires`

**Description:** Get paginated list of completed questionnaires

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 10)
- `search` (optional): Search by client name or questionnaire title
- `date_from` (optional): Filter from date (ISO format)
- `date_to` (optional): Filter to date (ISO format)

**Response:**
```json
{
  "questionnaires": [
    {
      "id": 2,
      "client_name": "XYZ Ltd",
      "title": "Security Risk Assessment",
      "sectors": ["Healthcare", "Technology"],
      "technologies": ["Blockchain", "IoT"],
      "completed_at": "2024-01-20T14:45:00Z",
      "status": "completed"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 89,
    "pages": 9
  }
}
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized

---

## Feedback Endpoint

### 8. Submit Feedback
**POST** `/feedback`

**Description:** Submit user feedback (low priority feature)

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "type": "bug_report", // "bug_report", "feature_request", "general"
  "subject": "Issue with questionnaire upload",
  "description": "Detailed description of the issue",
  "priority": "medium" // "low", "medium", "high"
}
```

**Response:**
```json
{
  "message": "Feedback submitted successfully",
  "feedback_id": 123
}
```

**Status Codes:**
- `201` - Feedback submitted
- `400` - Invalid feedback type
- `401` - Unauthorized
- `422` - Validation error

---

## Knowledge Base Endpoints

### 9. Upload Historical Documents
**POST** `/knowledge_base/upload`

**Description:** Upload historical documents (Excel files) with associated sectors and technologies

**Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Request Body (Form Data):**
- `file`: Excel file (required)
- `sectors`: JSON array of sectors (required)
- `technologies`: JSON array of technologies (required)
- `description`: Document description (optional)

**Example:**
```
file: [Excel file]
sectors: ["Technology", "Finance", "Healthcare"]
technologies: ["AI", "Cloud Computing", "Blockchain"]
description: "Q4 2023 Risk Assessment Data"
```

**Response:**
```json
{
  "message": "Document uploaded successfully",
  "document_id": 456,
  "processed_sectors": ["Technology", "Finance", "Healthcare"],
  "processed_technologies": ["AI", "Cloud Computing", "Blockchain"],
  "file_size": "2.5MB",
  "uploaded_at": "2024-01-15T10:30:00Z"
}
```

**Status Codes:**
- `201` - Document uploaded successfully
- `400` - Invalid file format or missing data
- `401` - Unauthorized
- `413` - File too large
- `422` - Validation error

---

## Questionnaire Endpoints

### 10. Upload Questionnaire
**POST** `/questionnaire/upload`

**Description:** Upload questionnaire file with matching criteria for sectors and technologies

**Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Request Body (Form Data):**
- `file`: Questionnaire file (required)
- `sectors`: JSON array of sectors (required)
- `technologies`: JSON array of technologies (required)
- `topk`: Matching priority (required)
  - `1`: Both sectors and technologies must match
  - `2`: Sector must match, technology matching is optional
  - `3`: Neither sectors nor technologies need to match
- `client_name`: Client name (required)
- `title`: Questionnaire title (optional)

**Example:**
```
file: [Questionnaire file]
sectors: ["Technology", "Finance"]
technologies: ["AI", "Machine Learning"]
topk: 2
client_name: "ABC Corporation"
title: "Q1 2024 Risk Assessment"
```

**Response:**
```json
{
  "message": "Questionnaire uploaded successfully",
  "questionnaire_id": 789,
  "matching_criteria": {
    "topk": 2,
    "sectors": ["Technology", "Finance"],
    "technologies": ["AI", "Machine Learning"]
  },
  "processing_status": "in_progress",
  "estimated_completion": "2024-01-15T11:00:00Z"
}
```

**Status Codes:**
- `201` - Questionnaire uploaded successfully
- `400` - Invalid file or missing required fields
- `401` - Unauthorized
- `413` - File too large
- `422` - Validation error

---

### 11. Update Questionnaire Response
**PUT** `/questionnaire/{id}`

**Description:** Update suggested answers for specific questions in a questionnaire

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Path Parameters:**
- `id`: Questionnaire ID (required)

**Request Body:**
```json
{{
  "question_id": "Q001",
  "suggested_answer": {
    "answer": "High risk due to outdated security protocols",
    "comments": "Recommend immediate security audit",
    "remarks": "Critical finding - requires urgent attention",
  }
}
}
```

**Response:**
```json
{
  "message": "Questionnaire updated successfully",
  "questionnaire_id": 789,
  "updated_question": "Q001",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Status Codes:**
- `200` - Updated successfully
- `400` - Invalid question ID or answer format
- `401` - Unauthorized
- `404` - Questionnaire not found
- `422` - Validation error

---

### 12. Retrain and Submit Questionnaire
**POST** `/questionnaire/retrain_and_submit/{id}`

**Description:** Retrain the AI model with suggested answers and submit the questionnaire

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `id`: Questionnaire ID (required)

**Response:**
```json
{
  "message": "Questionnaire retrained and submitted successfully",
  "questionnaire_id": 789,
  "retraining_status": "completed",
  "submitted_at": "2024-01-15T10:30:00Z",
  "knowledge_base_updated": true,
  "new_insights_added": 15
}
```

**Status Codes:**
- `200` - Retrained and submitted successfully
- `400` - No suggested answers to retrain with
- `401` - Unauthorized
- `404` - Questionnaire not found
- `422` - Validation error

---

### 13. Download Questionnaire
**GET** `/questionnaire/download/{id}`

**Description:** Download questionnaire with suggested answers

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `id`: Questionnaire ID (required)

**Query Parameters:**
- `format` (optional): Download format - "pdf", "excel", "json" (default: "pdf")

**Response:**
- **Success (200)**: File download (binary content)
- **Headers**: 
  - `Content-Type`: application/pdf, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, or application/json
  - `Content-Disposition`: attachment; filename="questionnaire_789.pdf"

**Status Codes:**
- `200` - File downloaded successfully
- `401` - Unauthorized
- `404` - Questionnaire not found
- `500` - File generation error

---

## Reference Data Endpoints

### 14. Get Sectors
**GET** `/sectors`

**Description:** Get list of available sectors

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "sectors": [
    "Technology",
    "Finance",
    "Healthcare",
    "Manufacturing",
    "Retail",
    "Education",
    "Government",
    "Energy",
    "Transportation",
    "Telecommunications"
  ],
  "total_count": 10
}
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized

---

### 15. Get Technologies
**GET** `/technologies`

**Description:** Get list of available technologies

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "technologies": [
    "Artificial Intelligence",
    "Machine Learning",
    "Cloud Computing",
    "Blockchain",
    "Internet of Things (IoT)",
    "Cybersecurity",
    "Data Analytics",
    "Mobile Applications",
    "Web Development",
    "DevOps"
  ],
  "total_count": 10
}
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized

---

### 16. Search Client
**GET** `/client/{client_name}`

**Description:** Search for client by name to check availability

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `client_name`: Client name to search (required)

**Response:**
```json
{
  "client_exists": true,
  "client_info": {
    "id": 123,
    "name": "ABC Corporation",
    "email": "contact@abccorp.com",
    "created_at": "2024-01-01T00:00:00Z",
    "total_questionnaires": 5
  }
}
```

**Status Codes:**
- `200` - Client found
- `404` - Client not found
- `401` - Unauthorized

---

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "error": "Bad Request",
  "message": "Invalid request parameters",
  "details": {
    "field": "email",
    "issue": "Invalid email format"
  }
}
```

### 401 Unauthorized
```json
{
  "error": "Unauthorized",
  "message": "Authentication required"
}
```

### 403 Forbidden
```json
{
  "error": "Forbidden",
  "message": "Insufficient permissions"
}
```

### 404 Not Found
```json
{
  "error": "Not Found",
  "message": "Resource not found"
}
```

### 422 Unprocessable Entity
```json
{
  "error": "Validation Error",
  "message": "Request validation failed",
  "details": [
    {
      "field": "password",
      "message": "Password must be at least 8 characters"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal Server Error",
  "message": "An unexpected error occurred"
}
```

---

