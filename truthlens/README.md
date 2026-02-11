# Streamlit and FastAPI Workspace

This project is a web application that consists of a frontend built with Streamlit and a backend powered by FastAPI. The frontend provides an interactive user interface, while the backend handles API requests and serves data.

## Project Structure

```
streamlit-fastapi-workspace
├── frontend
│   ├── requirements.txt
│   └── app.py
├── backend
│   ├── requirements.txt
│   ├── app
│   │   ├── main.py
│   │   └── routes.py
│   └── tests
│       └── test_main.py
├── .gitignore
└── README.md
```

## Setup Instructions

### Prerequisites

Make sure you have Python 3.7 or higher installed on your machine.

### Frontend Setup

1. Navigate to the `frontend` directory:
   ```
   cd frontend
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the Streamlit application:
   ```
   streamlit run app.py
   ```

### Backend Setup

1. Navigate to the `backend` directory:
   ```
   cd backend
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the FastAPI application:
   ```
   uvicorn app.main:app --reload
   ```

## Usage

- Access the Streamlit frontend at `http://localhost:8501`.
- Access the FastAPI backend at `http://localhost:8000`.

## Testing

To run the tests for the FastAPI application, navigate to the `backend/tests` directory and run:
```
pytest test_main.py
```

## License

This project is licensed under the MIT License. See the LICENSE file for more details.