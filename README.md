# Toxicity Moderation System

> Real-time AI-powered content moderation — detect, log, and visualize toxic comments at scale.

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![ONNX](https://img.shields.io/badge/ONNX-Optimized-005CED?style=flat-square&logo=onnx&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## Overview

The **Toxicity Moderation System** is a production-ready pipeline that classifies user-generated text in real time. It combines a DistilBERT-based ONNX model, a FastAPI inference backend, and an interactive Streamlit dashboard — giving you instant toxicity scores, persistent moderation logs, and live analytics all in one place.

---

## Features

- **Real-time toxicity detection** via optimized ONNX inference
- **FastAPI backend** with clean REST endpoints
- **Live Streamlit dashboard** — feed, metrics, alerts, and export
- **Hugging Face model hosting** (DistilBERT tokenizer + ONNX classifier)
- **SQLite / PostgreSQL** moderation result storage
- **Export results** as CSV, JSON, or Excel
- **Railway + Streamlit Cloud** deployment ready

---

## Project Structure

```
toxicity-moderation/
├── app.py                     # FastAPI backend
├── dashboard.py               # Streamlit dashboard
├── database.py                # DB models & helpers
├── moderation.db              # SQLite database (local)
├── requirements-api.txt       # Backend dependencies
├── requirements-dashboard.txt # Dashboard dependencies
└── README.md
```

---

## Model

| Component  | Details                          |
|------------|----------------------------------|
| Tokenizer  | DistilBERT (Hugging Face)        |
| Classifier | ONNX-optimized binary classifier |
| Hosting    | Hugging Face Hub                 |
| Output     | `toxic_probability` (0.0 – 1.0) |

---

## API Reference

### Health Check

```http
GET /
```

```json
{ "message": "Toxicity API is running" }
```

---

### Predict Toxicity

```http
POST /predict?text=<your text here>
```

| Parameter | Type   | Description            |
|-----------|--------|------------------------|
| `text`    | string | Input text to classify |

**Example:**

```bash
curl -X POST "https://your-api-url/predict?text=you are stupid"
```

**Response:**

```json
{
  "text": "you are stupid",
  "toxic_probability": 0.94,
  "prediction": "toxic"
}
```

---

### Get Moderation Logs

```http
GET /results
```

Returns all stored moderation results from the database.

---

## Running Locally

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd toxicity-moderation
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

---

### Backend

```bash
pip install -r requirements-api.txt
uvicorn app:app --reload
```

Runs at `http://127.0.0.1:8000`

---

### Dashboard

```bash
pip install -r requirements-dashboard.txt
streamlit run dashboard.py
```

Runs at `http://localhost:8501`

---

## Deployment

### Backend — Railway

1. Push the project to GitHub.
2. Create a new Railway project and connect your repository.
3. Set the start command:

```bash
uvicorn app:app --host 0.0.0.0 --port $PORT
```

---

### Dashboard — Streamlit Cloud

1. Create a new app on [Streamlit Cloud](https://streamlit.io/cloud).
2. Connect your GitHub repository.
3. Set the main file to `dashboard.py`.
4. Point to `requirements-dashboard.txt` for dependencies.

---

## CORS Configuration

CORS is enabled in `app.py` for cross-origin access:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

> **Note:** For production, replace `"*"` with your specific allowed origins.

---

## Dashboard Metrics

| Metric             | Description                        |
|--------------------|------------------------------------|
| Total Comments     | All analyzed inputs                |
| Toxic Comments     | Flagged as toxic                   |
| Safe Comments      | Classified as safe                 |
| Toxicity Rate      | Percentage of toxic content        |
| Avg Toxicity Score | Mean probability score             |
| Burst Alerts       | Real-time spike detection          |

---

## Roadmap

- [ ] PostgreSQL integration
- [ ] Authentication and user roles
- [ ] WebSocket live updates
- [ ] Kafka streaming support
- [ ] Docker and Kubernetes support
- [ ] Grafana and ML monitoring
- [ ] Multi-label toxicity categories (hate speech, threat, insult, etc.)

---

## Tech Stack

| Layer      | Technology                          |
|------------|-------------------------------------|
| Backend    | FastAPI, ONNX Runtime, Transformers |
| ML Model   | DistilBERT, PyTorch, Hugging Face   |
| Database   | SQLite / PostgreSQL                 |
| Frontend   | Streamlit, Pandas, Custom CSS       |
| Deployment | Railway, Streamlit Cloud            |

---

## Author

**Sunidhi**

---
