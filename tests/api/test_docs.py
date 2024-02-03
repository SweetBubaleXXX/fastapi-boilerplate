from fastapi import status
from fastapi.testclient import TestClient


def test_docs(client: TestClient):
    response = client.get("/docs")
    assert response.status_code == status.HTTP_200_OK
