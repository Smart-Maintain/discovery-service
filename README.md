# Discovery Service

The Discovery Service acts as the Service Registry for the SmartMaintain microservices architecture. It is built using **Spring Cloud Netflix Eureka**.

## Overview
All other microservices (Gateway, Identity, Equipment) register themselves with this service upon startup. This enables dynamic service discovery and load balancing without hardcoded IPs.

## Technical Details
- **Port:** `8761`
- **Framework:** Spring Boot 3.2, Spring Cloud 2023.0
- **Key Technology:** Eureka Server

## Running Locally
```bash
../mvnw spring-boot:run -DskipTests
```
Access the Eureka Dashboard at: `http://localhost:8761`
