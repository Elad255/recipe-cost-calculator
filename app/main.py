from fastapi import FastAPI

app = FastAPI(
    title="Recipe Cost Calculator API",
    description="Track ingredient prices, build recipes, and calculate dish costs and profit margins.",
    version="1.0.0"
)


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "recipe-cost-calculator"}