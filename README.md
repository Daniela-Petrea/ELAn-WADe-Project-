# **ELAn-WADe-Project**  
### Esoteric Language API  

This project provides a REST API for exploring and querying details about esoteric programming languages. It integrates with a SPARQL endpoint to fetch data, computes embeddings for semantic similarity, and includes endpoints for querying, searching, and exploring relationships between languages.

---

## Tags

- project
- infoiasi
- wade
- web

---

## Table of Contents

- [About the Project](#about-the-project)
- [API Endpoints](#api-endpoints)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## About the Project

ELAn-WADe-Project is designed to offer a structured way to explore esoteric programming languages, their properties, and relationships using semantic similarity and a knowledge graph.

---

## **API Endpoints**

### 1. **Homepage**
- **Endpoint:** `/`
- **Method:** `GET`  
- **Description:** Renders the homepage.

---

### 2. **Language Details**
- **Endpoint:** `/languages/<lang_name>`  
- **Method:** `GET`  
- **Description:** Fetches detailed information about a specific esoteric language.  
- **Response:** Includes properties, values, and similar languages.

---

### 3. **Search Languages**
- **Endpoint:** `/languages/search`  
- **Method:** `GET`  
- **Query Parameters:**  
  - `name`: Search term.  
  - `page`: Page number (default: 1).  
  - `limit`: Number of results per page (default: 12).  
- **Description:** Searches languages based on the provided name.  
- **Response:** List of matching languages with metadata.

---

### 4. **Get Unique Years**
- **Endpoint:** `/languages/years`  
- **Method:** `GET`  
- **Description:** Fetches a list of unique years when languages were released.

---

### 5. **Get Unique Designers**
- **Endpoint:** `/languages/designers`  
- **Method:** `GET`  
- **Description:** Fetches a list of unique designers.

---

### 6. **Filtered Language Details**
- **Endpoint:** `/languages/details`  
- **Method:** `GET`  
- **Query Parameters:**  
  - `year`: Filter by year.  
  - `designer`: Filter by designer.  
  - `page`: Page number (default: 1).  
  - `limit`: Number of results per page (default: 12).  
- **Description:** Fetches filtered language details.

---

### 7. **Compute Embeddings**
- **Endpoint:** `/compute_embeddings`  
- **Method:** `GET`  
- **Description:** Computes or loads entity embeddings for the ontology.  
- **Response:** Message indicating success.

---

### 8. **Get Similar Languages**
- **Endpoint:** `/get_similar_languages`  
- **Method:** `POST`  
- **Request Body:**  
  **Data format:**
  ```json
  {
    "given_language": "<language_URI>"
  }
- **Description:** Fetches languages similar to the given one based on semantic similarity.
- **Response:** List of similar languages with scores

---

## Getting Started

### Prerequisites
- Python 3.8+
- Flask
- Flask-CORS
- Flasgger
- NumPy
- Requests
- SPARQLWrapper
- Scikit-learn
- SentenceTransformers
- SPARQL Endpoint Configuration

### Installation
1. Clone the repo:
   ```sh
   git clone https://github.com/yourusername/ELAn-WADe-Project.git
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Run the application:
   ```sh
   python app.py
   ```

## Usage

Send API requests using tools like `curl` or Postman, or integrate it into an application.

Example:
```sh
curl -X GET http://localhost:5000/languages/Piet
```
---

## **Coverage Report**
The test coverage report can be found in the coverage.xml file in the project directory.