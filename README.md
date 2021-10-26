# Forumi backend

This is a simple Discussion Forum.

## Table of Content

- [Forumi backend](#forumi-backend)
  - [Table of Content](#table-of-content)
  - [Technologies](#technologies)
  - [How to run this project on your local machine](#how-to-run-this-project-on-your-local-machine)
  - [API Documentation](#api-documentation)
  - [How to run tests](#how-to-run-tests)

## Technologies

1. Python
2. Django Rest Framework
3. OpenAPI
4. Celery
5. Redis

## How to run this project on your local machine

1. Clone this repo:

    ```bash
    git clone https://github.com/damephena/forumi.git
    ```

2. Create your own remote and local branch:

    ```bash
    git checkout -b NEW_BRANCH_NAME
    ```

3. Create a new virtual environment for this project. *Virtualenv* and *anaconda* are popular choices.

    ***Please make sure to create a new environment for this project.***
    Kindly visit Python Environment and Package Manager sites to download your preferred choice.

4. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

5. Copy `.example.env` to `.env` file and substitute values:

    ```bash
    cp .example.env .env
    ```

    ```env
    SECRET_KEY = "YOUR_SECRET_KEY"
    DEBUG= YOUR_DEBUG_BOOLEAN
    ```

6. Setup your POSTGRES locally. And subsitute POSGRES variables to your local `.env` file.
7. Start your Postgres locally:

   ```bash
   sudo services postgres start
   ```

8. Setup REDIS server locally. Redis typically runs on port <redis://localhost:6379>
9. Start your Redis server:

    ```bash
    redis-server
    ```

10. Migrate existing files:

    ```bash
    python3 manage.py migrate
    ```

11. Run Celery:

    ```bash
    celery -A mul.celery worker -l info
    ```

12. To visit Forumi in your browser at port <http://localhost:8000>, start Forumi (Python) server:

    ```bash
    python3 manage.py runserver
    ```

That's all! Hack away. Visit <http://localhost:8000/> to view interactive API documentation of this repo.

## API Documentation

- OpenAPI (Swagger): For _Interactive API documentation_, visit <http://localhost:8000/>
- Redoc: For text documentation, visit <http://localhost:8000/redoc/>


## How to run tests

1. You can successfully run pytest locally:

    ```bash
    python manage.py test
    ```

That's it! See how many tests passed.
