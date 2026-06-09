import pytest
from unittest.mock import MagicMock
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db
from app.models.models import Base


import os

_base_url = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@db:5432/recipe_cost_db")
TEST_DATABASE_URL = _base_url.replace("/recipe_cost_db", "/recipe_cost_test_db")
engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def test_db():
    Base.metadata.create_all(bind=engine)
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def registered_user(client):
    response = client.post("/auth/register", json={
        "email": "chef@kitchen.com",
        "password": "shakshuka123"
    })
    return response.json()


@pytest.fixture
def auth_headers(client):
    client.post("/auth/register", json={
        "email": "chef@kitchen.com",
        "password": "shakshuka123"
    })
    response = client.post("/auth/login", json={
        "email": "chef@kitchen.com",
        "password": "shakshuka123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def second_user_headers(client):
    client.post("/auth/register", json={
        "email": "chef2@kitchen.com",
        "password": "falafel456"
    })
    response = client.post("/auth/login", json={
        "email": "chef2@kitchen.com",
        "password": "falafel456"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# === MOCK FIXTURES (kept from Day 7 for unit tests) ===

@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def sample_user():
    user = MagicMock()
    user.id = 1
    user.email = "chef@kitchen.com"
    user.hashed_password = "fakehashed123"
    user.created_at = datetime(2026, 1, 1)
    return user


@pytest.fixture
def sample_ingredient():
    ingredient = MagicMock()
    ingredient.id = 1
    ingredient.name = "Tomatoes"
    ingredient.category = "Vegetables"
    ingredient.unit = "kg"
    ingredient.price_per_unit = 8.90
    ingredient.owner_id = 1
    ingredient.created_at = datetime(2026, 1, 1)
    ingredient.updated_at = datetime(2026, 1, 1)
    return ingredient


@pytest.fixture
def sample_ingredient_2():
    ingredient = MagicMock()
    ingredient.id = 2
    ingredient.name = "Eggs"
    ingredient.category = "Dairy"
    ingredient.unit = "pieces"
    ingredient.price_per_unit = 3.50
    ingredient.owner_id = 1
    ingredient.created_at = datetime(2026, 1, 1)
    ingredient.updated_at = datetime(2026, 1, 1)
    return ingredient


@pytest.fixture
def sample_recipe(sample_ingredient, sample_ingredient_2):
    ri1 = MagicMock()
    ri1.ingredient = sample_ingredient
    ri1.quantity = 0.5

    ri2 = MagicMock()
    ri2.ingredient = sample_ingredient_2
    ri2.quantity = 4

    recipe = MagicMock()
    recipe.id = 1
    recipe.name = "Shakshuka"
    recipe.description = "Classic Israeli breakfast"
    recipe.category = "Main Course"
    recipe.servings = 4
    recipe.selling_price = 52.0
    recipe.owner_id = 1
    recipe.created_at = datetime(2026, 1, 1)
    recipe.updated_at = datetime(2026, 1, 1)
    recipe.recipe_ingredients = [ri1, ri2]
    return recipe