"""
WSGI entry point for production deployments (Render, Gunicorn, PythonAnywhere, Railway)
"""
from app import app

if __name__ == "__main__":
    app.run()
