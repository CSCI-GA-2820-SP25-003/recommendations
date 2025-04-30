# NYU DevOps Project: Recommendations

[![CI](https://github.com/CSCI-GA-2820-SP25-003/recommendations/actions/workflows/ci.yml/badge.svg)](https://github.com/CSCI-GA-2820-SP25-003/recommendations/actions)

[![codecov](https://codecov.io/gh/CSCI-GA-2820-SP25-003/recommendations/branch/master/graph/badge.svg)](https://codecov.io/gh/CSCI-GA-2820-SP25-003/recommendations)

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

## Automatic Setup

The best way to use this repo is to start your own repo using it as a git template. To do this just press the green **Use this template** button in GitHub and this will become the source for your repository.

## Manual Setup
"hello world"

You can also clone this repository and then copy and paste the starter code into your project repo folder on your local computer. Be careful not to copy over your own `README.md` file so be selective in what you copy.

There are 4 hidden files that you will need to copy manually if you use the Mac Finder or Windows Explorer to copy files from this folder into your repo folder.

These should be copied using a bash shell as follows:

```bash
    cp .gitignore  ../<your_repo_folder>/
    cp .flaskenv ../<your_repo_folder>/
    cp .gitattributes ../<your_repo_folder>/
```

## Contents

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
pyproject.toml      - Poetry list of Python libraries required by your code

service/                   - service python package
├── __init__.py            - package initializer
├── config.py              - configuration parameters
├── models.py              - module with business models
├── routes.py              - module with service routes
└── common                 - common code package
    ├── cli_commands.py    - Flask command to recreate all tables
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/                     - test cases package
├── __init__.py            - package initializer
├── factories.py           - Factory for testing with fake objects
├── test_cli_commands.py   - test suite for the CLI
├── test_models.py         - test suite for business models
└── test_routes.py         - test suite for service routes
```

## Database

The internal database has the following structure:

- `id` (int): Internal identifier, primary key
- `product_id` (int): ID of the product being recommended for
- `customer_id` (int): ID of the customer for whom the recommendation was made
- `recommend_type` (str < 63): Type of recommendation (e.g., up-sell, cross-sell, down-sell)
- `recommend_product_id` (int): ID of the recommended product
- `rec_success` (int): Number of times the recommendation was accepted

The `id` field is automatically generated internally and should not be provided in request bodies.

## Recommendation Response JSON

The format of the recommendation JSON returned by API responses is:

- `id` (int): Internal identifier
- `product_id` (int): ID of the product being recommended for
- `customer_id` (int): ID of the customer for whom the recommendation was made
- `recommend_type` (str): Type of recommendation (e.g., up-sell, cross-sell, down-sell)
- `recommend_product_id` (int): ID of the recommended product
- `rec_success` (int): Number of times the recommendation was accepted

## Recommendation Request JSON

The format of the recommendation JSON expected by `POST` and `PUT` requests is:

- `product_id` (int): ID of the product being recommended for (required)
- `customer_id` (int): ID of the customer for whom the recommendation is made (required)
- `recommend_type` (str): Type of recommendation (e.g., up-sell, cross-sell, down-sell) (required)
- `recommend_product_id` (int): ID of the recommended product (required)
- `rec_success` (int): Initial success count (required)

The `id` field should **not** be included in request bodies.

## Available API Endpoints

All routes return JSON responses and accept JSON request bodies where applicable. Routes return HTTP 200 OK unless otherwise specified (or HTTP 4xx/5xx in case of errors).

### GET /

Returns general information about the service.

Example response:

```json
{
    "name": "Recommendation Demo REST API Service",
    "paths": "http://127.0.0.1:8080/recommendations",
    "version": "1.0"
}
```

### GET /recommendations

List all recommendations in the database. Supports optional query parameters to filter results:

- `product_id` (int): Filter by product ID
- `customer_id` (int): Filter by customer ID
- `recommend_type` (str): Filter by recommendation type
- `recommend_product_id` (int): Filter by recommended product ID

Always returns a collection (empty if no matches found).

Example response:

```json
[
    {
        "id": 1,
        "product_id": 100,
        "customer_id": 200,
        "recommend_type": "up-sell",
        "recommend_product_id": 300,
        "rec_success": 12
    },
    {
        "id": 2,
        "product_id": 101,
        "customer_id": 201,
        "recommend_type": "cross-sell",
        "recommend_product_id": 301,
        "rec_success": 5
    }
]
```

### GET /recommendations/{recommendation_id}

Retrieve a specific recommendation by ID. Returns HTTP 404 Not Found if no such recommendation exists.

Example response for `/recommendations/1`:

```json
{
    "id": 1,
    "product_id": 100,
    "customer_id": 200,
    "recommend_type": "up-sell",
    "recommend_product_id": 300,
    "rec_success": 12
}
```

### POST /recommendations

Create a new recommendation.

#### Example request:

```json
{
    "product_id": 100,
    "customer_id": 200,
    "recommend_type": "up-sell",
    "recommend_product_id": 300,
    "rec_success": 0
}
```

#### Example response (HTTP 201 Created):

```json
{
    "id": 1,
    "product_id": 100,
    "customer_id": 200,
    "recommend_type": "up-sell",
    "recommend_product_id": 300,
    "rec_success": 0
}
```

### PUT /recommendations/{recommendation_id}

Update an existing recommendation.

#### Example request:

```json
{
    "product_id": 100,
    "customer_id": 200,
    "recommend_type": "up-sell",
    "recommend_product_id": 300,
    "rec_success": 1
}
```

#### Example response:

```json
{
    "id": 1,
    "product_id": 100,
    "customer_id": 200,
    "recommend_type": "up-sell",
    "recommend_product_id": 300,
    "rec_success": 1
}
```

### DELETE /recommendations/{recommendation_id}

Delete a recommendation by ID. Always returns HTTP 204 No Content, even if the recommendation didn’t exist.

## Testing

To run the test suite, use the `Makefile` inside the container:

```bash
make install
make test
```

This will execute all unit and integration tests using `pytest` and generate a coverage report.

## Health Check

### GET /health

Quick check to verify the service is running.

Example response:

```json
{
    "status": 200,
    "message": "Healthy"
}
```

## Development

To set up your development environment:

1. Clone the repository.
2. Install dependencies:
```bash
make install
```
3. Run the service:
```bash
flask run
```

---

## Database Initialization

The database schema is automatically created on startup if it doesn’t exist. For development, you can also reset the database manually using:

```bash
flask shell
>>> from service import models
>>> models.db.drop_all()    // Optional: if you need to reset the schema
>>> models.db.create_all()
```

---

## Postgres Deployment

This project includes a Kubernetes-based deployment of a PostgreSQL database to provide persistent storage for the Recommendation microservice.
All Kubernetes-related configurations are located in the ./k8s directory:
```
k8s/
├── deployment.yaml               # App deployment
├── service.yaml                  # App service
├── ingress.yaml                  # Ingress route
└── postgres/
    ├── postgres-deployment.yaml  # PostgreSQL StatefulSet
    └── postgres-service.yaml     # PostgreSQL service
```

#### How to Deploy (Locally with K3s)

Start a local K3s cluster (via Makefile):
```
make cluster
```

Build and push the app image:
```
make build
make push
```

Apply PostgreSQL and app manifests:
```
kubectl apply -f k8s/postgres
kubectl apply -f k8s
```

Check deployment status:
```
kubectl get pods
kubectl get svc
kubectl get ingress
```

#### How to Test
For local deployments, add the following to `/etc/hosts` on your computer. This is the address listed when run `kubectl get ingress`.
```
127.0.0.1 recommendation.local
```

Health Check (once deployed):
```
curl http://recommendation.local/health
# Response: {"message":"Healthy","status":200}
```

Verify PostgreSQL is up:
```
kubectl exec -it postgres-0 -- psql -U postgres
\c recommendation
SELECT * FROM recommendation;
# \l                 -- list databases
# \dt                -- list tables (after app writes)
# \c                 -- connect to a table
```


## License

Copyright (c) 2016, 2025 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
