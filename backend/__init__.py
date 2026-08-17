"""Project TRIAD Backend API Package."""

from backend.app import app, create_app
from backend.data_service import DataService

__all__ = ["app", "create_app", "DataService"]
