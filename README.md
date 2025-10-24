# AI Chatbot Project

This is a multi-component chatbot application that supports advanced features, including multimodal chat with images and data analysis by querying CSV files via a dedicated MCP server.

Demo: [https://youtu.be/uV_kBuPEWGk](https://youtu.be/uV_kBuPEWGk)

## ✨ Features

* **Image Chat:** Engage in conversations about images.
* **CSV Data Chat:** Ask questions and analyze data from CSV files.
* **Modular Architecture:** The system is divided into a `frontend`, a `backend`, and a dedicated `excel_mcp` server for structured data processing.

## 🏗️ System Overview

<img width="1386" height="684" alt="diagram" src="https://github.com/user-attachments/assets/892afe74-8849-4e06-84c7-6e2f53f81679" />

## 📂 Project Structure

The repository consists of three core components:

* `/backend`: Main chatbot API and orchestration logic (FastAPI, WebSocket handling).
* `/frontend`: Web-based user interface (React).
* `/excel_mcp`: “MCP server” for data analysis and interaction with CSV files.

## 📋 Prerequisites

Before running the project locally, ensure that the following tools are installed:

* [Node.js](https://nodejs.org/) (LTS version recommended)
* [pnpm](https://pnpm.io/installation) (Package manager for the frontend)
* [uv](https://github.com/astral-sh/uv) (Fast Python package installer and runner)
* [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) (for containerized deployment)

---

## 🚀 How to Run Locally (Manual Setup)

If you prefer to run each service manually, use **three separate terminal windows** (or tabs).

### 1. Backend

```bash
# Navigate to backend directory
cd backend

# Run the backend server
uv run main.py
```

Your backend server should now be running.

---

### 2. Frontend

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
pnpm install

# Build and start the application
pnpm build
pnpm start
```

The frontend will be available at [http://localhost:3000](http://localhost:3000).

---

### 3. Excel MCP Server

```bash
# Navigate to the MCP server directory
cd excel_mcp/mcp_excel_server

# Start the MCP server
uv run server.py
```

The MCP server will now be ready to handle backend requests.

---

## 🐳 Run with Docker Compose (Recommended)

You can run all services together using **Docker Compose**, which automatically builds and connects the containers in a shared network.

```bash
# Build and start all services
docker compose up --build
```

This command will start:

* **frontend**: accessible at [http://localhost:3000](http://localhost:3000)
* **backend**: internal service handling chat logic
* **excel_mcp**: dedicated server for Excel data processing

To stop all containers, use:

```bash
docker compose down
```

If you modify source code and need to rebuild, run:

```bash
docker compose up --build
```


## 🧩 Environment Configuration

The project uses a `.env` file located in the root directory.
Currently, it only requires one variable:

```
OPENAI_API_KEY=your_openai_api_key_here
```

Docker Compose automatically loads this file and shares the variable with all containers.
Ensure the key is valid before starting the services.

---
