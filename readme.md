# 🚀 Porsche911 Microservices

This project is a microservices-based architecture with authentication, user management, and portfolio management, leveraging** ****FastAPI**,** ****PostgreSQL**,** ****Docker**, and** ****Grafana for monitoring**.

## 📜 Table of Contents

1. [Overview]()
2. [Technologies Used]()
3. [Setup]()
4. [Running the Services]()
5. [API Endpoints]()
6. [Database Migrations]()
7. [Logging and Monitoring]()
8. [Testing]()
9. [Troubleshooting]()

---

## 1️⃣ Overview

This project consists of multiple microservices:

* **Auth Service**: Manages user authentication (JWT-based)
* **User Service**: Handles user profiles, portfolios, and highlights
* **Database**: PostgreSQL as the main data storage
* **Monitoring**: Grafana, Loki, and Prometheus for logs and metrics

## 2️⃣ Technologies Used

* **Python 3.11**, FastAPI
* **PostgreSQL 13**
* **SQLAlchemy** + Alembic (migrations)
* **Docker, Docker Compose**
* **Prometheus, Grafana, Loki** (Monitoring & Logging)

## 3️⃣ Setup

### Prerequisites:

1. Install** ****Docker** and** ****Docker Compose**
2. Clone this repository:
   ```
   git clone https://github.com/your-repo/porsche911.git
   cd porsche911
   ```

## 4️⃣ Running the Services

1. Start the microservices and monitoring stack:
   ```
   docker-compose up --build
   ```
2. To stop the services:
   ```
   docker-compose down --volumes
   ```

## 5️⃣ API Endpoints

### 🔑 Auth Service:

* **Register User:** `<span>POST /auth/register</span>`
* **Login:** `<span>POST /auth/login</span>`
* **Refresh Token:** `<span>POST /auth/refresh</span>`

### 👤 User Service:

* **Get Current User:** `<span>GET /users/me</span>`
* **Update User Profile:** `<span>PUT /users/me</span>`
* **Delete User:** `<span>DELETE /users/me</span>`
* **Get User Portfolio:** `<span>GET /users/{username}/portfolio</span>`
* **Add Portfolio:** `<span>POST /users/me/portfolio</span>`
* **Update Portfolio:** `<span>PUT /users/me/portfolio/{portfolio_id}</span>`
* **Delete Portfolio:** `<span>DELETE /users/me/portfolio/{portfolio_id}</span>`
* **Add Highlight:** `<span>POST /users/portfolio/{portfolio_id}/highlights</span>`
* **Remove Highlight:** `<span>DELETE /users/portfolio/{portfolio_id}/highlights/{highlight_id}</span>`

## 6️⃣ Database Migrations

To run migrations:

```
cd UserService
alembic upgrade head
```

To create a new migration:

```
alembic revision --autogenerate -m "Migration message"
alembic upgrade head
```

## 7️⃣ Logging and Monitoring

* **Grafana** runs on** **`<span>http://localhost:3000</span>`
  * Default login:** **`<span>admin / admin</span>`
  * Connected to Prometheus & Loki for monitoring logs
* **Prometheus** UI:** **`<span>http://localhost:9090</span>`
* **Loki (Log Aggregation):** `<span>http://localhost:3100</span>`

## 8️⃣ Testing

To run unit tests inside Docker:

```
docker-compose exec user-service pytest
```

To run tests locally:

```
pytest tests/
```

## 9️⃣ Troubleshooting

* **Database Connection Issues:**
  ```
  docker-compose down --volumes && docker-compose up --build
  ```
* **Rebuild Services:**
  ```
  docker-compose up --force-recreate --build
  ```

---

### 🚀 Happy Coding! 🚀
