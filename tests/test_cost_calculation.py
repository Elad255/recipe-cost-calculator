import pytest
from unittest.mock import MagicMock
from app.routers.recipes import build_recipe_response
from app.routers.analysis import calculate_recipe_summary


class TestBuildRecipeResponse:

    def test_calculates_total_cost(self, sample_recipe, mock_db):
        result = build_recipe_response(sample_recipe, mock_db)
        # Tomatoes: 0.5 * 8.90 = 4.45
        # Eggs: 4 * 3.50 = 14.00
        # Total: 18.45
        assert result.total_cost == 18.45

    def test_calculates_cost_per_serving(self, sample_recipe, mock_db):
        result = build_recipe_response(sample_recipe, mock_db)
        # Total 18.45 / 4 servings = 4.61
        assert result.cost_per_serving == 4.61

    def test_calculates_profit_margin(self, sample_recipe, mock_db):
        result = build_recipe_response(sample_recipe, mock_db)
        # Selling price 52.0, cost per serving 4.61
        # (52.0 - 4.61) / 52.0 * 100 = 91.13
        assert result.profit_margin == 91.13

    def test_recipe_with_no_ingredients(self, mock_db):
        recipe = MagicMock()
        recipe.id = 2
        recipe.name = "Empty Recipe"
        recipe.description = None
        recipe.category = "Other"
        recipe.servings = 1
        recipe.selling_price = 30.0
        recipe.owner_id = 1
        recipe.created_at = MagicMock()
        recipe.updated_at = MagicMock()
        recipe.recipe_ingredients = []

        result = build_recipe_response(recipe, mock_db)
        assert result.total_cost == 0
        assert result.cost_per_serving == 0
        assert result.ingredients == []

    def test_recipe_with_no_selling_price(self, sample_recipe, mock_db):
        sample_recipe.selling_price = None

        result = build_recipe_response(sample_recipe, mock_db)
        assert result.profit_margin is None
        assert result.total_cost == 18.45

    def test_ingredients_list_in_response(self, sample_recipe, mock_db):
        result = build_recipe_response(sample_recipe, mock_db)
        assert len(result.ingredients) == 2
        assert result.ingredients[0].ingredient_name == "Tomatoes"
        assert result.ingredients[0].cost == 4.45
        assert result.ingredients[1].ingredient_name == "Eggs"
        assert result.ingredients[1].cost == 14.0


class TestCalculateRecipeSummary:

    def test_summary_calculates_cost(self, sample_recipe):
        result = calculate_recipe_summary(sample_recipe)
        assert result.total_cost == 18.45
        assert result.cost_per_serving == 4.61

    def test_summary_calculates_margin(self, sample_recipe):
        result = calculate_recipe_summary(sample_recipe)
        assert result.profit_margin == 91.13

    def test_summary_without_selling_price(self, sample_recipe):
        sample_recipe.selling_price = None
        result = calculate_recipe_summary(sample_recipe)
        assert result.profit_margin is None

    def test_summary_with_zero_servings(self, sample_recipe):
        sample_recipe.servings = 0
        result = calculate_recipe_summary(sample_recipe)
        assert result.cost_per_serving == 0