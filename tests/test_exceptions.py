import pytest
from app.utils.exceptions import (
    IngredientNotFound,
    DuplicateIngredient,
    NotOwner,
    RecipeNotFound
)


class TestIngredientNotFound:

    def test_status_code(self):
        exc = IngredientNotFound(7)
        assert exc.status_code == 404

    def test_error_code(self):
        exc = IngredientNotFound(7)
        assert exc.error == "ingredient_not_found"

    def test_message_contains_id(self):
        exc = IngredientNotFound(7)
        assert "7" in exc.message


class TestDuplicateIngredient:

    def test_status_code(self):
        exc = DuplicateIngredient("Tomatoes")
        assert exc.status_code == 400

    def test_message_contains_name(self):
        exc = DuplicateIngredient("Tomatoes")
        assert "Tomatoes" in exc.message


class TestNotOwner:

    def test_status_code(self):
        exc = NotOwner("ingredient")
        assert exc.status_code == 403

    def test_message_contains_resource(self):
        exc = NotOwner("ingredient")
        assert "ingredient" in exc.message


class TestRecipeNotFound:

    def test_status_code(self):
        exc = RecipeNotFound(3)
        assert exc.status_code == 404

    def test_message(self):
        exc = RecipeNotFound(3)
        assert "3" in exc.message