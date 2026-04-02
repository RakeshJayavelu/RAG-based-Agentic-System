
***

# Asynchronous Agentic RAG Architecture


## 🚀 Tech Stack

* **Web Framework:** Django / Django REST Framework
* **Agentic Orchestration:** LangGraph
* **Vector Database:** PostgreSQL with `pgvector` 
* **State Management & Queue:** Redis
* **Embeddings:** SentenceTransformers 
* **Local LLM:** Ollama (`mistral`)
* **PDF Parsing:** PyMuPDF 

---

## ⚙️ Prerequisites

Before you begin, ensure you have the following installed and running on your system:
* Python 3.10+
* PostgreSQL 15+
* Redis Server
* [Ollama](https://ollama.com/) (with the `mistral` model pulled)

---

## 🛠️ Installation & Setup

**1. Clone the repository and navigate to the directory:**
```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
```

**2. Create and activate a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

**3. Install the dependencies:**
```bash
pip install -r requirements.txt
```

**4. Set up the Database:**
Ensure your PostgreSQL server is running. Create a database (e.g., `ragdb2`) and enable the vector extension:
```sql
CREATE DATABASE ragdb2;
\c ragdb2
CREATE EXTENSION IF NOT EXISTS vector;
```

**5. Apply Database Migrations:**
```bash
python manage.py makemigrations
python manage.py migrate
```

**6. Start Local Dependencies:**
Make sure Ollama and Redis are running in the background:
```bash
# Start Redis (depends on your OS)
redis-server

# Ensure Ollama has the Mistral model
ollama pull mistral
ollama serve
```

---

## 🏃‍♂️ Running the Application with Terminal Chatbot Client

To test the agent's performance and system metrics in isolation without building a full frontend, this project includes a dedicated terminal testing client. 

This client allows you to interact with the LLM in real-time, monitor request latency (verifying the asynchronous offloading), and track mathematical drift.

**How to use the client:**

You will need to run the server and the client simultaneously in two separate terminal windows.

**Terminal 1 (Start the Backend):**
```bash
# From the root of your project
python manage.py runserver
```

**Terminal 2 (Start the Client):**
```bash
# Navigate to the testing folder
cd "terminal chatbot"
python chatbot.py
```

**Available Client Commands:**
Once the chatbot is running, you can chat directly with the LLM or use the following system commands:
* `/health` - Checks the live status of the Django server, PostgreSQL database, and Ollama connection.
* `/metrics` (or `/stats`) - Displays the P50 latency, average cosine similarity, and real-time alerts for vector normalization drift.
* `exit` (or `quit`) - Ends the session.


## 📡 API Endpoints

### 1. Health Check
* **GET** `/api/health/`
* Checks the connection status of the Django app, PostgreSQL database, and local Ollama instance.

### 2. Ingest Documents
* **POST** `/api/ingest/`
* **Body:** `{"directory_path": "/absolute/path/to/your/pdfs"}`
* Parses all PDFs in the directory, chunks the text, calculates embeddings (with mathematical normalization), and saves them to the HNSW index.

### 3. Query the Agent
* **POST** `/api/query/`
* **Body:** `{"question": "What is the architecture of..."}`
* Triggers the LangGraph workflow to retrieve context via semantic search, generate an answer using Mistral, and calculate vector drift metrics.

### 4. Metrics Dashboard
* **GET** `/api/metrics/`
* Returns system health and performance stats, including P50/P95 latency, average cosine similarity, and real-time alerts for mathematical drift.
