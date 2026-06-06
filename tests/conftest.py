import pytest
from unittest.mock import MagicMock
from datetime import datetime


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