# AI Chatbot Project

This is a multi-component chatbot application that supports advanced features, including multimodal chat with images and data analysis by querying CSV files via a dedicated MCP server.
Demo: https://youtu.be/uV_kBuPEWGk
## ✨ Features

* **Image Chat:** Engage in conversations about images.
* **CSV Data Chat:** Ask questions and analyze data from CSV files.
* **Modular Architecture:** The project is separated into a `frontend`, `backend`, and a dedicated `excel_mcp` server for data processing.

## 📂 Project Structure

The repository is organized into three main components:

* `/backend`: The main chatbot API and logic (e.g., FastAPI, WebSocket handling).
* `/frontend`: The web-based user interface (e.g., React, Vue, Svelte).
* `/excel_mcp`: The "MCP server" dedicated to CSV data processing.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
* [Node.js](https://nodejs.org/) (LTS version recommended)
* [pnpm](https://pnpm.io/installation) (Package manager for the frontend)
* [uv](https://github.com/astral-sh/uv) (A fast Python package installer and runner)

## 🚀 How to Run Locally

To run the full application, you will need to open **three separate terminal windows** (or tabs), one for each service.

---

### 1. Run the Backend

In your **first** terminal, run the main backend server:

```bash
# 1. Navigate to the backend directory
cd backend

# 2. Run the main application using uv
# (This assumes 'uv' is configured to find and install dependencies
# defined in your pyproject.toml or requirements.txt)
uv run main.py
```
*Your backend server should now be running.*

-----

### 2\. Run the Frontend

In your **second** terminal, run the web interface:

```bash
# 1. Navigate to the frontend directory
cd frontend

# 2. Install all necessary dependencies
pnpm install

# 3. Build the application for production
pnpm build

# 4. Start the production server
pnpm start
```

*Your frontend application should now be accessible in your browser (e.g., at `http://localhost:3000`).*

-----

### 3\. Run the MCP Server (for CSV Chat)

In your **third** terminal, run the dedicated CSV data processing server:

```bash
# 1. Navigate to the MCP server's directory
cd excel_mcp/mcp_excel_server

# 2. Run the server application using uv
uv run server.py
```

*Your MCP data server is now running and ready to handle requests from the backend.*

-----
