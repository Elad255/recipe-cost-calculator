class RecipeAppException(Exception):
    def __init__(self, status_code: int, error: str, message: str):
        self.status_code = status_code
        self.error = error
        self.message = message
        super().__init__(message)


class IngredientNotFound(RecipeAppException):
    def __init__(self, ingredient_id: int):
        super().__init__(
            status_code=404,
            error="ingredient_not_found",
            message=f"Ingredient with ID {ingredient_id} does not exist"
        )


class DuplicateIngredient(RecipeAppException):
    def __init__(self, name: str):
        super().__init__(
            status_code=400,
            error="duplicate_ingredient",
            message=f"Ingredient '{name}' already exists"
        )


class NotOwner(RecipeAppException):
    def __init__(self, resource: str):
        super().__init__(
            status_code=403,
            error="not_owner",
            message=f"You don't have permission to access this {resource}"
        )

class RecipeNotFound(RecipeAppException):
    def __init__(self, recipe_id: int):
        super().__init__(
            status_code=404,
            error="recipe_not_found",
            message=f"Recipe with ID {recipe_id} does not exist"
        )