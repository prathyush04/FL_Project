# Spring Boot Backend

This directory contains the core backend API for the Federated Learning project, built with **Java 21** and **Spring Boot 3**. 
It handles user authentication, data management, and orchestration between the frontend and the ML service.

## Technologies Used
- **Java 21**
- **Spring Boot 3.x**
  - **Spring Web MVC**: REST API development.
  - **Spring Data JPA**: Database interactions and ORM.
  - **Spring Security**: Authentication and authorization.
- **JWT (JSON Web Tokens)**: Secure, stateless user authentication.
- **Flyway**: Database migration and version control.
- **H2 Database / MySQL**: In-memory DB for development/testing or MySQL for production.
- **MapStruct & Lombok**: Reducing boilerplate code for DTO mappings and getters/setters.
- **Maven**: Build tool and dependency management.

## Project Structure Overview
- **`src/main/java/com/fl/backend/`**: Contains the main application code (Controllers, Services, Repositories, Security Config, Entities).
- **`src/main/resources/`**: Configuration files (`application.yml` or `application.properties`) and Flyway migration scripts.
- **`pom.xml`**: Maven dependency configuration.

## Setup & Running

1. **Prerequisites:** Ensure you have Java 21 and Maven installed.

2. **Build the project:**
   Navigate to this directory and run:
   ```bash
   ./mvnw clean install
   ```

3. **Run the application:**
   ```bash
   ./mvnw spring-boot:run
   ```
   The server will start on the configured port (default is usually `8080`).

## Documentation
- The project includes **Swagger / OpenAPI** integration. Once the application is running, you can access the API documentation at `http://localhost:8080/swagger-ui.html`.
- See `POSTMAN_GUIDE.md` for information on importing and using the provided Postman collection for API testing.
- See `HLD_Part3_Backend.docx` for high-level architectural details of the backend.
