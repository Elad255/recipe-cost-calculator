import pytest


class TestCreateIngredient:

    def test_create_ingredient_success(self, client, auth_headers):
        response = client.post("/ingredients/", json={
            "name": "Tomatoes",
            "category": "Vegetables",
            "unit": "kg",
            "price_per_unit": 8.90
        }, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Tomatoes"
        assert data["category"] == "Vegetables"
        assert data["price_per_unit"] == 8.90

    def test_create_ingredient_no_auth(self, client):
        response = client.post("/ingredients/", json={
            "name": "Tomatoes",
            "category": "Vegetables",
            "unit": "kg",
            "price_per_unit": 8.90
        })
        assert response.status_code == 401

    def test_create_duplicate_ingredient(self, client, auth_headers):
        client.post("/ingredients/", json={
            "name": "Tomatoes",
            "category": "Vegetables",
            "unit": "kg",
            "price_per_unit": 8.90
        }, headers=auth_headers)

        response = client.post("/ingredients/", json={
            "name": "Tomatoes",
            "category": "Vegetables",
            "unit": "kg",
            "price_per_unit": 9.50
        }, headers=auth_headers)
        assert response.status_code == 400


class TestGetIngredients:

    def test_get_ingredients_empty(self, client, auth_headers):
        response = client.get("/ingredients/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_get_ingredients_with_data(self, client, auth_headers):
        client.post("/ingredients/", json={
            "name": "Tomatoes",
            "category": "Vegetables",
            "unit": "kg",
            "price_per_unit": 8.90
        }, headers=auth_headers)
        client.post("/ingredients/", json={
            "name": "Eggs",
            "category": "Dairy",
            "unit": "pieces",
            "price_per_unit": 3.50
        }, headers=auth_headers)

        response = client.get("/ingredients/", headers=auth_headers)
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

    def test_filter_by_category(self, client, auth_headers):
        client.post("/ingredients/", json={
            "name": "Tomatoes",
            "category": "Vegetables",
            "unit": "kg",
            "price_per_unit": 8.90
        }, headers=auth_headers)
        client.post("/ingredients/", json={
            "name": "Eggs",
            "category": "Dairy",
            "unit": "pieces",
            "price_per_unit": 3.50
        }, headers=auth_headers)

        response = client.get("/ingredients/?category=Vegetables", headers=auth_headers)
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["name"] == "Tomatoes"

    def test_search_by_name(self, client, auth_headers):
        client.post("/ingredients/", json={
            "name": "Tomatoes",
            "category": "Vegetables",
            "unit": "kg",
            "price_per_unit": 8.90
        }, headers=auth_headers)
        client.post("/ingredients/", json={
            "name": "Cherry Tomato",
            "category": "Vegetables",
            "unit": "kg",
            "price_per_unit": 12.00
        }, headers=auth_headers)
        client.post("/ingredients/", json={
            "name": "Eggs",
            "category": "Dairy",
            "unit": "pieces",
            "price_per_unit": 3.50
        }, headers=auth_headers)

        response = client.get("/ingredients/?search=tomato", headers=auth_headers)
        data = response.json()
        assert data["total"] == 2

    def test_pagination(self, client, auth_headers):
        for i in range(15):
            client.post("/ingredients/", json={
                "name": f"Ingredient {i}",
                "category": "Test",
                "unit": "kg",
                "price_per_unit": 1.00
            }, headers=auth_headers)

        response = client.get("/ingredients/?page=1&size=10", headers=auth_headers)
        data = response.json()
        assert len(data["items"]) == 10
        assert data["total"] == 15
        assert data["pages"] == 2

        response = client.get("/ingredients/?page=2&size=10", headers=auth_headers)
        data = response.json()
        assert len(data["items"]) == 5


class TestGetOneIngredient:

    def test_get_ingredient_success(self, client, auth_headers):
        create_response = client.post("/ingredients/", json={
            "name": "Tomatoes",
            "category": "Vegetables",
            "unit": "kg",
            "price_per_unit": 8.90
        }, headers=auth_headers)
        ingredient_id = create_response.json()["id"]

        response = client.get(f"/ingredients/{ingredient_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["name"] == "Tomatoes"

    def test_get_ingredient_not_found(self, client, auth_headers):
        response = client.get("/ingredients/999", headers=auth_headers)
        assert response.status_code == 404

    def test_get_other_users_ingredient(self, client, auth_headers, second_user_headers):
        create_response = client.post("/ingredients/", json={
            "name": "Secret Spice",
            "category": "Spices",
            "unit": "g",
            "price_per_unit": 50.00
        }, headers=auth_headers)
        ingredient_id = create_response.json()["id"]

        response = client.get(f"/ingredients/{ingredient_id}", headers=second_user_headers)
        assert response.status_code == 403


class TestUpdateIngredient:

    def test_update_ingredient_success(self, client, auth_headers):
        create_response = client.post("/ingredients/", json={
            "name": "Tomatoes",
            "category": "Vegetables",
            "unit": "kg",
            "price_per_unit": 8.90
        }, headers=auth_headers)
        ingredient_id = create_response.json()["id"]

        response = client.put(f"/ingredients/{ingredient_id}", json={
            "price_per_unit": 10.50
        }, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["price_per_unit"] == 10.50
        assert response.json()["name"] == "Tomatoes"


class TestDeleteIngredient:

    def test_delete_ingredient_success(self, client, auth_headers):
        create_response = client.post("/ingredients/", json={
            "name": "Tomatoes",
            "category": "Vegetables",
            "unit": "kg",
            "price_per_unit": 8.90
        }, headers=auth_headers)
        ingredient_id = create_response.json()["id"]

        response = client.delete(f"/ingredients/{ingredient_id}", headers=auth_headers)
        assert response.status_code == 200

        get_response = client.get(f"/ingredients/{ingredient_id}", headers=auth_headers)
        assert get_response.status_code == 404