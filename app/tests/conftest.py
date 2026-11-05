"""Fixtures compartidas para las pruebas de HU-01."""

import os

import pytest


@pytest.fixture
def url_api() -> str:
    """URL base de la API, configurable con la variable de entorno URL_API."""
    return os.environ.get("URL_API", "http://localhost:8000")


@pytest.fixture
def url_web() -> str:
    """URL base del frontend, configurable con la variable de entorno URL_WEB."""
    return os.environ.get("URL_WEB", "http://localhost:8080")
