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
- [Roadmap](#roadmap)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)
- 
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
### 9. **Compare Languages**
- **Endpoint:** `/languages/compare`
- **Method:** `POST`
- **Request Body:**
  ```json
  {
    "given_language": "0815",
    "similar_language": "123"
  }
- **Description:** Compares two esoteric languages and provides a report on their similarities and differences. 
- **Response:** A comparison report between two esoteric languages, detailing the differences in properties such as the release year, with the similarity status (e.g., "Different") indicating how the values compare.

### 10. **Get Ontology Details**
- **Endpoint:** `/ontology`
- **Method:** `GET`
- **Description:** Fetches the ontology of the esoteric languages.  
- **Response:** The full ontology with categories, relationships, and entities in a machine-readable format. 

## Roadmap

The development of the **ELAn-WADe-Project** followed a structured process. Below is a summary of the key steps we took, along with improvements based on feedback:

1. **Data Retrieval and Ontology Population**  
   - In the folder **retrieving_data_and_populating_ontology**, we detail how we parsed an XML dump from the esolang site. This XML contained information about esoteric programming languages, which we extracted and stored in a CSV format.
   - We then populated the **ELAN.rdf** ontology, created in Protegé, with data extracted from the CSV. This process involved structuring the information from the CSV into RDF format and enhancing it with additional details.

2. **Ontology Enrichment with DBpedia**  
   - After populating the initial ontology, we enriched it by adding more information from **DBpedia**. This provided further context and detail about the esoteric languages, which helped improve the quality of the data for semantic querying.

3. **SPARQL Query Development**  
   - Once the ontology was populated and enriched, we began writing **SPARQL queries** to interrogate the data. These queries allow us to fetch detailed information about the languages, including their properties and relationships with other languages.

4. **Feedback and Improvements**  
   - After receiving valuable feedback from a seminar, we made several improvements to our project:
     - **Frontend Contrast:** Adjusted the contrast for better readability and user experience.
     - **Abstract for Each Language:** Added an abstract for each esoteric language to provide more context.
     - **Links to Esolang Site:** We provided links to the esolang website for further exploration.
     - **Comparison of Similar Languages:** We added the ability to compare languages with similar properties in a tabular format.
     - **Interactive Concepts:** We made it possible for users to click on concepts like "Turing" and view a description of the concept.

5. **Future Work & Considerations**  
   - **Scalability**: The current architecture works well for a lightweight web app. However, if future expansion is needed, we plan to:
     - Add **authentication** for user accounts and personalized experiences.

   - **Performance**: 
     - **SPARQL Queries**: We aim to optimize SPARQL queries for faster data retrieval.
     - **Caching**: To avoid redundant queries and reduce load times, we will implement **caching** techniques, especially for frequently queried data.

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
curl -X GET http://localhost:5000/language/Malbolge
```
---

## **Coverage Report**
The test coverage report can be found in the coverage.xml file in the project directory.


## Contributing

Feel free to submit issues and pull requests. For any feature requests, bug fixes, or improvements, please create a new issue in the GitHub repository.

---

## License

This project is licensed under the MIT License.

---

## Contact

For questions or feedback, please contact the project maintainer:

- Name: Petrea Daniela, Pușcașu Bogdan
- GitHub: [https://github.com/Daniela-Petrea/ELAn-WADe-Project-](https://github.com/Daniela-Petrea/ELAn-WADe-Project-)