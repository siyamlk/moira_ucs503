# MOIRA

### Academic Elective & Backlog Advisory Platform

> **Every choice draws a path. Find your way forward.**

MOIRA is a full-stack academic advisory platform designed to help
undergraduate students make informed academic decisions.

It transforms a student’s **interests and career goals** into ranked,
explainable elective recommendations and prioritizes pending **backlog
courses** based on estimated CGPA impact. The platform is backed by real
university course-scheme and faculty data.

------------------------------------------------------------------------

## Overview

Students often have to search through course documents, academic
regulations, faculty information, and peer advice before deciding which
electives to take or which backlogs to clear first.

MOIRA brings these inputs together in one platform and provides:

- Personalized elective recommendations
- Explainable recommendation reasoning
- Deterministic backlog prioritization
- Estimated CGPA impact
- Faculty discovery based on specialization
- Persistent student profiles
- Secure JWT-based authentication

------------------------------------------------------------------------

## Key Features

### Authentication

- User signup and login
- JWT-based authentication
- Bcrypt password hashing
- Protected application routes
- Persistent sessions

### Student Profile

Students can maintain: - Current semester - CGPA - Completed credits -
Career goal - Areas of interest

Profile information is persisted and used by the recommendation system.

### Elective Advisor

The Elective Advisor:

1.  Accepts structured interests, career goals, and free-text input.
2.  Normalizes the input into predefined interest and career tags.
3.  Scores available electives against the interpreted profile.
4.  Returns ranked recommendations.
5.  Provides an explanation for each recommendation.
6.  Identifies faculty whose specializations match the recommended
    course topics.

### Backlog Advisor

The Backlog Advisor: - Stores pending backlog courses. - Estimates the
CGPA change associated with clearing each course. - Assigns priority
levels: **CRITICAL, HIGH, MODERATE**. - Ranks courses according to the
magnitude of their estimated CGPA impact.

> **Note:** The backlog calculation is a documented prototype estimate
> and is not an official university CGPA calculation.

### Faculty Directory

- Searchable faculty directory
- Faculty name and designation
- Specialization information
- Email where available
- Office room information where available

------------------------------------------------------------------------

## Real Academic Data

MOIRA is designed around real academic data rather than fabricated
demonstration content.

| Dataset                |                      Current Coverage |
|------------------------|--------------------------------------:|
| Professional Electives |               96 real CSE/COE courses |
| CSE Faculty            |                   211 faculty members |
| ECE Faculty            |                    65 faculty members |
| Course Information     | Real course codes, titles and credits |

The elective dataset was transcribed from official **2025 B.E. CSE and
COE course-scheme documents**, covering Professional Elective Baskets
I–IV.

The faculty dataset was collected from official department directories.

Additional branch data can be added through the existing seed-data
pipeline. Mechanical, Civil, and ENC data are not currently included.

Where source data is unavailable, MOIRA deliberately leaves the field
empty instead of inventing information.

------------------------------------------------------------------------

## System Architecture

MOIRA follows a deliberately simple two-tier architecture suitable for a
Software Engineering Lab project.

``` text
┌──────────────────────────────┐
│        React Frontend        │
│ React · TypeScript · Vite    │
│ Tailwind · Router · Axios    │
└──────────────┬───────────────┘
               │
          HTTPS / JSON
          JWT Bearer Token
               │
               ▼
┌──────────────────────────────┐
│        FastAPI Backend       │
│                              │
│ Routes → Services → Models   │
│ Recommendation Engine        │
│ Authentication & Validation  │
└──────────────┬───────────────┘
               │
               │ SQLAlchemy
               ▼
┌──────────────────────────────┐
│          PostgreSQL          │
│                              │
│ Student Profiles             │
│ Electives & Backlogs         │
│ Faculty Data                 │
└──────────────────────────────┘
```

### Request Flow

For an elective recommendation:

``` text
Student Input
     ↓
React Form
     ↓
electiveService.recommend()
     ↓
POST /api/electives/recommend
     ↓
Input Normalization
     ↓
Recommendation Service
     ↓
Rule-Based Scoring
     ↓
Faculty Matching
     ↓
Ranked Recommendations
     ↓
React UI
```

### Backend Structure

The backend follows a layered structure:

- **Routes** handle HTTP requests and responses.
- **Schemas** define API request/response contracts.
- **Services** contain application-level business logic.
- **Recommendation** contains scoring, career matching, and explanation
  logic.
- **Models** represent PostgreSQL tables through SQLAlchemy.
- **Core** contains configuration and authentication/security utilities.
- **Seed** loads real academic data.

------------------------------------------------------------------------

## Recommendation Engine

MOIRA uses a **deterministic, rule-based recommendation engine** rather
than an ML model.

Free-text input is mapped to a fixed vocabulary of interest and career
tags using keyword matching.

Each elective receives a score from **0–100** based on:

| Component             |                 Weight |
|-----------------------|-----------------------:|
| Interest overlap      |                    45% |
| Career-goal alignment |                    30% |
| Topic overlap         |                    20% |
| Relevance bonus       | Small additional bonus |

The resulting recommendations are sorted and returned with an
explanation of why each course matched the student’s profile.

This approach keeps the system deterministic, explainable, easy to test,
and easy to modify.

Detailed logic is documented in
[`docs/RECOMMENDATION_LOGIC.md`](docs/RECOMMENDATION_LOGIC.md).

------------------------------------------------------------------------

## Backlog Prioritization

For each pending backlog, MOIRA estimates the potential CGPA change
using the student’s current CGPA and credit load, assuming a
conservative passing grade if the course is cleared.

Backlogs are then ranked according to the **magnitude of the estimated
CGPA swing**.

This makes the prioritization deterministic and gives students a
transparent reason for the ordering.

Detailed assumptions and the prototype formula are documented in
[`docs/BACKLOG_LOGIC.md`](docs/BACKLOG_LOGIC.md).

------------------------------------------------------------------------

## Tech Stack

| Layer              | Technologies                                                  |
|--------------------|---------------------------------------------------------------|
| **Frontend**       | React 18, TypeScript, Vite, Tailwind CSS, React Router, Axios |
| **Backend**        | Python, FastAPI, SQLAlchemy 2, Pydantic 2                     |
| **Authentication** | JWT, python-jose, bcrypt                                      |
| **Database**       | PostgreSQL                                                    |
| **Testing**        | pytest, TypeScript build checks                               |
| **CI**             | GitHub Actions                                                |

Docker, Kubernetes, and microservices are intentionally outside the
current scope to keep the project straightforward to run and reason
about.

------------------------------------------------------------------------

## Project Structure

``` text
moira/
│
├── frontend/
│   ├── public/                Static assets
│   └── src/
│       ├── components/        Reusable UI components
│       ├── pages/             Application screens
│       ├── services/          Axios API clients
│       ├── context/           Authentication state
│       └── utils/             Shared helpers
│
├── backend/
│   ├── app/
│   │   ├── core/              Configuration & security
│   │   ├── database/          SQLAlchemy setup
│   │   ├── models/            ORM models
│   │   ├── schemas/           API contracts
│   │   ├── routes/            FastAPI routers
│   │   ├── recommendation/    Recommendation engine
│   │   ├── services/          Business logic
│   │   └── seed/              Academic data & seed scripts
│   ├── tests/                 Backend tests
│   └── requirements.txt
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── DATABASE.md
│   ├── RECOMMENDATION_LOGIC.md
│   └── BACKLOG_LOGIC.md
│
└── .github/
    └── workflows/
        └── ci.yml
```

------------------------------------------------------------------------

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+

### 1. Set Up PostgreSQL

``` sql
CREATE USER moira_user WITH PASSWORD 'moira_password';
CREATE DATABASE moira OWNER moira_user;
```

### 2. Set Up the Backend

``` bash
cd backend
python -m venv .venv
```

**Windows Git Bash:**

``` bash
source .venv/Scripts/activate
```

**Windows PowerShell:**

``` powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

``` bash
pip install -r requirements.txt
```

Create the environment file:

``` bash
cp .env.example .env
```

Update `DATABASE_URL` and `JWT_SECRET` if required.

Seed the database:

``` bash
python -m app.seed.seed_data
```

Start the API:

``` bash
uvicorn app.main:app --reload --port 8000
```

Backend: `http://localhost:8000`

API docs: `http://localhost:8000/docs`

### 3. Set Up the Frontend

Open a new terminal:

``` bash
cd frontend
npm install
```

Create the environment file:

``` bash
cp .env.example .env
```

Set:

``` env
VITE_API_URL=http://localhost:8000/api
```

Start the development server:

``` bash
npm run dev
```

Frontend: `http://localhost:5173`

### 4. Try the Application

A seeded demo account is available:

``` text
Email:    alex.chen@thapar.edu
Password: Demo@1234
```

The account includes a profile, interests, and sample backlogs for
testing the main workflows.

You can also create a new account through the application.

### 5. Run Tests

``` bash
cd backend
source .venv/Scripts/activate
pytest -v
```

The current test suite contains **19 backend tests** covering
authentication, profile handling, recommendation scoring/ranking, and
backlog prioritization/CGPA-impact calculations.

------------------------------------------------------------------------

## API Overview

Detailed API documentation is available in [`docs/API.md`](docs/API.md).

| Method | Endpoint                   | Purpose                  |
|--------|----------------------------|--------------------------|
| GET    | `/api/health`              | Health check             |
| POST   | `/api/auth/signup`         | Create account           |
| POST   | `/api/auth/login`          | Authenticate user        |
| GET    | `/api/auth/me`             | Get current user         |
| GET    | `/api/profile`             | Get student profile      |
| PUT    | `/api/profile`             | Update student profile   |
| GET    | `/api/electives`           | List electives           |
| GET    | `/api/electives/{id}`      | Get elective             |
| POST   | `/api/electives/recommend` | Generate recommendations |
| GET    | `/api/backlogs`            | List backlogs            |
| POST   | `/api/backlogs`            | Add backlog              |
| POST   | `/api/backlogs/prioritize` | Prioritize backlogs      |
| GET    | `/api/faculty`             | List/search faculty      |
| GET    | `/api/faculty/{id}`        | Get faculty member       |

------------------------------------------------------------------------

## Security

MOIRA uses JWT-based authentication for protected API routes.

``` text
Login / Signup
      ↓
JWT issued by backend
      ↓
Token stored by frontend
      ↓
Axios attaches Bearer token
      ↓
FastAPI validates token
      ↓
Protected endpoint
```

Passwords are stored using bcrypt hashing rather than plaintext storage.

Environment-specific secrets such as database credentials and
`JWT_SECRET` are kept outside the source code through `.env`
configuration.

------------------------------------------------------------------------

## Continuous Integration

GitHub Actions runs automated checks on pushes and pull requests.

The CI pipeline verifies:

- Backend dependencies
- Backend tests
- Frontend installation
- Frontend TypeScript/build checks

Workflow: [`.github/workflows/ci.yml`](.github/workflows/ci.yml)

------------------------------------------------------------------------

## Documentation

Additional technical documentation is available in the `docs/`
directory:

- [`ARCHITECTURE.md`](docs/ARCHITECTURE.md) - System architecture and
  testing strategy
- [`API.md`](docs/API.md) - API reference
- [`DATABASE.md`](docs/DATABASE.md) - Database schema
- [`RECOMMENDATION_LOGIC.md`](docs/RECOMMENDATION_LOGIC.md) -
  Recommendation scoring
- [`BACKLOG_LOGIC.md`](docs/BACKLOG_LOGIC.md) - Backlog prioritization
  and CGPA estimation

------------------------------------------------------------------------

## Known Limitations

- Currently loaded academic data covers CSE + COE electives and CSE +
  ECE faculty.
- Mechanical, Civil, and ENC data are not currently included.
- CSE faculty office-hours data is not available.
- Electives currently contain scheme-level information such as code,
  title, and credits rather than full syllabus/prerequisite data.
- Suggested faculty are matched dynamically using elective topics and
  faculty specialization.
- Backlog CGPA impact uses a documented prototype formula and should not
  be treated as an official university calculation.
- Elective enrollment/syllabus actions are currently placeholders
  because MOIRA is not connected to a university enrollment system.
- Deployment infrastructure such as Docker is outside the current
  project scope.

------------------------------------------------------------------------

## Project Status

**Status: Functional academic prototype**

Current core workflow:

``` text
Authentication
      ↓
Student Profile
      ↓
Elective Discovery
      ↓
Recommendation Engine
      ↓
Explainable Results

Backlog Management
      ↓
CGPA Impact Estimation
      ↓
Priority Ranking

Faculty Directory
      ↓
Specialization-Based Discovery
```

------------------------------------------------------------------------

## License

Educational project developed as part of a Software Engineering Lab
project.

<p align="center">
<strong>MOIRA</strong><br> Academic decision support for students.
</p>
