import pytest


class TestCreateRecipe:

    def test_create_recipe_success(self, client, auth_headers):
        response = client.post("/recipes/", json={
            "name": "Shakshuka",
            "description": "Classic Israeli breakfast",
            "category": "Main Course",
            "servings": 4,
            "selling_price": 52.00
        }, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Shakshuka"
        assert data["servings"] == 4
        assert data["total_cost"] == 0
        assert data["ingredients"] == []

    def test_create_recipe_no_auth(self, client):
        response = client.post("/recipes/", json={
            "name": "Shakshuka",
            "category": "Main Course",
            "servings": 4
        })
        assert response.status_code == 401


class TestRecipeIngredients:

    def test_add_ingredient_to_recipe(self, client, auth_headers):
        ing_response = client.post("/ingredients/", json={
            "name": "Tomatoes",
            "category": "Vegetables",
            "unit": "kg",
            "price_per_unit": 8.90
        }, headers=auth_headers)
        ingredient_id = ing_response.json()["id"]

        recipe_response = client.post("/recipes/", json={
            "name": "Shakshuka",
            "category": "Main Course",
            "servings": 4,
            "selling_price": 52.00
        }, headers=auth_headers)
        recipe_id = recipe_response.json()["id"]

        response = client.post(f"/recipes/{recipe_id}/ingredients", json={
            "ingredient_id": ingredient_id,
            "quantity": 0.5
        }, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["ingredients"]) == 1
        assert data["ingredients"][0]["ingredient_name"] == "Tomatoes"
        assert data["ingredients"][0]["cost"] == 4.45
        assert data["total_cost"] == 4.45

    def test_full_recipe_cost_calculation(self, client, auth_headers):
        tom_response = client.post("/ingredients/", json={
            "name": "Tomatoes",
            "category": "Vegetables",
            "unit": "kg",
            "price_per_unit": 8.90
        }, headers=auth_headers)
        tom_id = tom_response.json()["id"]

        egg_response = client.post("/ingredients/", json={
            "name": "Eggs",
            "category": "Dairy",
            "unit": "pieces",
            "price_per_unit": 3.50
        }, headers=auth_headers)
        egg_id = egg_response.json()["id"]

        recipe_response = client.post("/recipes/", json={
            "name": "Shakshuka",
            "category": "Main Course",
            "servings": 4,
            "selling_price": 52.00
        }, headers=auth_headers)
        recipe_id = recipe_response.json()["id"]

        client.post(f"/recipes/{recipe_id}/ingredients", json={
            "ingredient_id": tom_id,
            "quantity": 0.5
        }, headers=auth_headers)

        response = client.post(f"/recipes/{recipe_id}/ingredients", json={
            "ingredient_id": egg_id,
            "quantity": 4
        }, headers=auth_headers)

        data = response.json()
        assert data["total_cost"] == 18.45
        assert data["cost_per_serving"] == 4.61
        assert data["profit_margin"] == 91.13
        assert len(data["ingredients"]) == 2

    def test_remove_ingredient_from_recipe(self, client, auth_headers):
        ing_response = client.post("/ingredients/", json={
            "name": "Tomatoes",
            "category": "Vegetables",
            "unit": "kg",
            "price_per_unit": 8.90
        }, headers=auth_headers)
        ingredient_id = ing_response.json()["id"]

        recipe_response = client.post("/recipes/", json={
            "name": "Shakshuka",
            "category": "Main Course",
            "servings": 4
        }, headers=auth_headers)
        recipe_id = recipe_response.json()["id"]

        client.post(f"/recipes/{recipe_id}/ingredients", json={
            "ingredient_id": ingredient_id,
            "quantity": 0.5
        }, headers=auth_headers)

        response = client.delete(
            f"/recipes/{recipe_id}/ingredients/{ingredient_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert len(response.json()["ingredients"]) == 0
        assert response.json()["total_cost"] == 0


class TestRecipeAuthorization:

    def test_cant_access_other_users_recipe(self, client, auth_headers, second_user_headers):
        recipe_response = client.post("/recipes/", json={
            "name": "Secret Recipe",
            "category": "Main Course",
            "servings": 2
        }, headers=auth_headers)
        recipe_id = recipe_response.json()["id"]

        response = client.get(f"/recipes/{recipe_id}", headers=second_user_headers)
        assert response.status_code == 403

    def test_cant_delete_other_users_recipe(self, client, auth_headers, second_user_headers):
        recipe_response = client.post("/recipes/", json={
            "name": "Secret Recipe",
            "category": "Main Course",
            "servings": 2
        }, headers=auth_headers)
        recipe_id = recipe_response.json()["id"]

        response = client.delete(f"/recipes/{recipe_id}", headers=second_user_headers)
        assert response.status_code == 403