# EV Charger OCPP Backend Module

This repository contains a backend module for managing Electric Vehicle (EV) chargers using the OCPP 1.6 JSON protocol. The project is built with Django, Django Channels, and Django REST Framework. It includes JWT-based authentication, a real-time frontend dashboard, and a standalone charger simulator.

---

## Table of Contents

- [Installation](#installation)
- [Modules Overview](#modules-overview)
  - [Authentication Module](#authentication-module)
  - [Chargers Module](#chargers-module)
  - [Frontend Module](#frontend-module)
  - [Simulator](#simulator)
- [Running the Application](#running-the-application)
- [Real-time Updates](#real-time-updates)
- [Additional Notes](#additional-notes)

---

## Installation

1. **Clone the Repository:**

   ```bash
   git clone <repository_url>
   cd <repository_directory>

2. **Build and Run with Docker Compose:**
   
   ```bash
   docker-compose build
   docker compose up
   ```
#### Note: The PostgreSQL server is configured to automatically start with a user having credentials:
##### Username: admin
##### Password: admin

3. **Access the Application:**
    ##### Once the containers are running, the server is available at:
    http://localhost:8000/
    
    ##### The frontend dashboard is available at:
    http://localhost:8000/ui/


## Modules Overview
### Authentication Module

The authentication module is implemented using JWT and provides the following endpoints:

- **Register:** `/api/auth/register/`
  - Accepts `username` and `password`.
  - Returns a success message and JWT tokens.

- **Login:** `/api/auth/login/`
  - Accepts `username` and `password`.
  - Returns a success message and JWT tokens.

- **Logout:** `/api/auth/logout/`
  - Requires an access token in the authorization header.

- **Refresh Token:** `/api/auth/refresh/`
  - Refreshes the JWT token.

### Chargers Module

The chargers module implements OCPP v1.6 features and handles communication with charging stations. Key components include:

- **Models:**
  - `Charger`: Represents a charging station.
  - `Transaction`: Represents a charging session.
  - `StatusLog`: Logs the status of charging stations.

- **Consumers:**
  - `ChargePoint`: Handles OCPP messages and updates the charging station status.
  - `OCPPConsumer`: Manages WebSocket connections for charging stations.

- **Views:**
  - `ChargerListAPIView`: Lists all charging stations.
  - `StartChargingAPIView`: Starts a charging session for a specific charging station.

- **Endpoints:**
  - `/api/chargers/`: Lists all charging stations.
  - `/api/chargers/start/<str:charge_point_id>/`: Starts a charging session.

## Frontend

The frontend provides a dashboard for monitoring and controlling charging stations. It includes:

- **WebSocket Consumer:** `FrontendConsumer` receives real-time updates from the backend and broadcasts them to the frontend.
- **Views:**
  - `dashboard`: Displays a list of all charging stations.
  - `charger_detail`: Displays detailed information about a specific charging station.
  - `run_simulator` and `stop_simulator`: Controls the charging station simulator.

- **HTML Templates:**
  - `login.html`: Login page.
  - `dashboard.html`: Dashboard for monitoring charging stations.
  - `charger_details.html`: Detailed view of a charging station.

## Simulator

The simulator script (`simulator.py`) simulates the behavior of a charging station for testing purposes. It connects to the server via WebSocket and sends OCPP messages to mimic real charging station interactions.
