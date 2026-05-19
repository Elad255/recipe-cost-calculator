from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.routers import auth
from app.routers import ingredients
from app.utils.exceptions import RecipeAppException

app = FastAPI(
    title="Recipe Cost Calculator API",
    description="Track ingredient prices, build recipes, and calculate dish costs and profit margins.",
    version="1.0.0"
)


@app.exception_handler(RecipeAppException)
async def recipe_app_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error,
            "message": exc.message
        }
    )


app.include_router(auth.router)
app.include_router(ingredients.router)


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "recipe-cost-calculator"}