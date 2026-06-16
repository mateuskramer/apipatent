# Patent AI Lab API — Developer Guide

This repository contains the backend REST API for the **Patent AI Lab** project, built using FastAPI. It provides programmatic access to patent metadata, semantic similarity searches, term networks, trend indicators, dictionary management, and predictive models.

---

## 1. Production Deployment

The API is fully deployed and live in production:
* **Production Base URL:** `https://apipatent.onrender.com`
* **Live Interactive Documentation (Swagger):** `https://apipatent.onrender.com/docs`
* **Live ReDoc Documentation:** `https://apipatent.onrender.com/redoc`

> [!NOTE]
> The production instance is hosted on Render (Free Tier). If the API has not been accessed for 15 minutes, the server goes to sleep. The first request after a sleeping period will trigger a **cold start** (taking ~50 seconds to boot up), which may occasionally result in a temporary `502 Bad Gateway` error. Subsequent requests will be extremely fast (~5 seconds for large queries).

---

## 2. Capabilities & Features

The API provides high-performance server-side data processing and analytics, offloading heavy calculations from client applications:

1. **Semantic Similarity Searches:** Performs real-time cosine similarity computations across the entire patent embedding catalog on the server.
2. **Co-occurrence Network Graphs:** Builds multi-layered relationships between technology terms, yielding ready-to-render graph nodes and edges.
3. **Innovation Holes Analysis (Sparse Opportunities):** Applies sparse matrix multiplications (`scipy.sparse`) to discover terms that never co-occur on the same patent but share technical neighbors.
4. **Trend Indicators:** Calculates growth rate, patent density, discipline fusion, and semantic shift for technical terms.
5. **Time-Series Forecasting:** Serves predictive counts estimated by the Temporal Fusion Transformer (TFT) model.

---

## 3. Local Development

### 3.1. Prerequisites
Ensure you have Python 3.10+ installed and a copy of the `.env` database configuration file.

### 3.2. Installation
Navigate to the API folder and install dependencies:
```bash
cd api
pip install -r requirements.txt
```

### 3.3. Running Locally
Start the development server with hot-reload enabled:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Once started, you can access the local Swagger documentation at `http://127.0.0.1:8000/docs`.

---

## 4. Authentication

Sensitive endpoints (such as `/dictionary` POST/PUT/DELETE operations) require authentication. 
* Configure an `API_KEY` value in your environment variables.
* Authenticate by sending the API Key inside the **`X-API-Key`** header.

**Example Python request header:**
```python
headers = {
    "X-API-Key": "your_secure_api_key_here",
    "Accept": "application/json"
}
```

---

## 5. Core API Endpoints

All requests support and recommend the use of Gzip compression headers:
```http
Accept-Encoding: gzip
```

### 5.1. Patents & Semantics

#### `GET /patents`
Fetches a list of patents.
* **Query Parameters:**
  * `exclude_embeddings` (bool, default `false`): Set to `true` to omit the heavy float array embeddings, reducing response size by 98%.
* **Response:** List of patent records.

#### `GET /patents/{patent_id}/similar`
Calculates and returns similar patents to a given patent ID based on semantic vector similarity.
* **Path Parameters:**
  * `patent_id` (str): The unique string ID of the patent (e.g. `US-11520110-B2` or a numerical database ID like `61411`).
* **Query Parameters:**
  * `limit` (int, default `10`): Maximum similar patents to return.
* **Python Usage Example:**
  ```python
  import requests

  url = "https://apipatent.onrender.com/patents/61411/similar"
  response = requests.get(url, headers={"Accept-Encoding": "gzip"})
  similar_patents = response.json()

  for patent in similar_patents:
      print(f"[{patent['similarity']:.4f}] {patent['id']} - {patent['title']}")
  ```

---

### 5.2. Terms & Co-occurrence Networks

#### `GET /terms`
Lists all technical terms extracted in the catalog.

#### `GET /terms/{term}/network`
Generates a co-occurrence network graph surrounding a root term. 
* **Query Parameters:**
  * `depth` (int, default `3`): Graph traversal depth layer.
  * `limit` (int, default `5`): Maximum co-occurring branches per node.
* **Python Usage Example:**
  ```python
  import requests
  import networkx as nx

  url = "https://apipatent.onrender.com/terms/deep learning/network"
  res = requests.get(url, params={"depth": 2, "limit": 5})
  network_data = res.json()

  # Reconstruct the graph locally
  G = nx.Graph()
  for node in network_data["nodes"]:
      G.add_node(node["id"], layer=node["layer"])
  for edge in network_data["edges"]:
      G.add_edge(edge["source"], edge["target"], weight=edge["weight"])

  print(f"Network built with {G.number_of_nodes()} nodes.")
  ```

#### `GET /terms/{term}/opportunities`
Calculates "Innovation Holes" (sparse associations) using scipy sparse matrices. Returns terms that share neighbors but never co-occur.
* **Query Parameters:**
  * `limit` (int, default `20`): Maximum recommendations.
* **Response:**
  ```json
  [
    {
      "term": "reinforcement learning",
      "bridge_strength": 14,
      "common_neighbors_score": 0.045
    }
  ]
  ```

---

### 5.3. Analytics, Trends & Predictions

#### `GET /ranking`
Retrieves a ranked list of terms ordered by `future_score` (combining Growth, Density, Fusion, and Semantic Shift).

#### `GET /terms/{term}/indicators`
Retrieves the individual quantitative trend indicators for a specific term:
* **Growth %:** Growth rate.
* **Density:** Unique patent counts.
* **Fusion:** Connectivity to other disciplines.
* **Shift %:** Semantic mutation.

#### `GET /predictions/{term}`
Retrieves future time-series forecasting (optimistic, pessimistic, and expected value counts) predicted by the Temporal Fusion Transformer (TFT) model.
