# CoinWorld Scraper API

This is a Python-based API service that scrapes trending token data from Dexscreener.com. It uses FastAPI for the web server and Selenium with `selenium-stealth` for robust, evasive scraping.

## Features

-   **FastAPI**: High-performance asynchronous web framework.
-   **Selenium + Stealth**: Scrapes dynamic, JavaScript-heavy websites while avoiding bot detection.
-   **Caching**: In-memory TTL cache to reduce load and prevent scraping on every request.
-   **Dockerized**: Ready for easy deployment in any container-hosting environment.

## Setup & Running Locally

1.  **Prerequisites**:
    *   Python 3.8+
    *   Docker

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Variables:**
    Create a `.env` file from the `.env.example` and set your desired cache TTL.
    ```bash
    cp .env.example .env
    ```

5.  **Run the application:**
    ```bash
    uvicorn main:app --reload
    ```
    The API will be available at `http://127.0.0.1:8000`. You can access the auto-generated documentation at `http://127.0.0.1:8000/docs`.

## Running with Docker

1.  **Build the Docker image:**
    ```bash
    docker build -t coinworld-scraper .
    ```

2.  **Run the Docker container:**
    ```bash
    docker run -d -p 8000:8000 --name coinworld-scraper-container coinworld-scraper
    ```
    The API will be running and accessible at `http://localhost:8000`.

## API Endpoint

-   **GET `/trending/{chain}`**
    -   Description: Get trending tokens for a specific chain.
    -   Example: `http://localhost:8000/trending/solana`