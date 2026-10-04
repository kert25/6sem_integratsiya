# Dockerized Node.js Express PostgreSQL API

This project is a simple CRUD API built with **Node.js**, **Express**, and **PostgreSQL**, containerized using **Docker** and orchestrated with **Docker Compose**.

---

## Purpose

I created this project primarily to **learn Docker containerization** and **practice working with PostgreSQL databases** inside Docker containers. It helped me understand:

- How to run multi-service applications using Docker Compose  
- Connecting a Node.js backend to a PostgreSQL database inside containers  
- Persisting database data using Docker volumes  
- Writing basic REST API routes for database operations  

---

## Project Structure

- `server.js` — Express server handling API routes for managing schools  
- `db.js` — PostgreSQL connection pool configuration  
- `Dockerfile` — Builds the Node.js app container  
- `docker-compose.yml` — Defines and runs the PostgreSQL and Node.js containers together  
- `test.rest` — REST client requests to test API endpoints  

