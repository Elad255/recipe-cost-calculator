# 🧑‍🍳 Recipe Cost Calculator API

[![CI](https://github.com/Elad255/recipe-cost-calculator/actions/workflows/ci.yml/badge.svg)](https://github.com/Elad255/recipe-cost-calculator/actions)

**A REST API that helps restaurant owners track ingredient prices, build recipes, and instantly calculate the real cost per dish and profit margin.**

---

## The Problem

Most small-to-medium restaurants have no idea what each dish actually costs to make. Chefs set prices by gut feeling, and a dish that seems profitable might actually be losing money. When ingredient prices change (tomatoes go up 20% this month), nobody recalculates the menu — leading to invisible losses.

## The Solution

Recipe Cost Calculator lets restaurant owners:
- **Track ingredients** with real-time prices and categories
- **Build recipes** by adding ingredients with exact quantities
- **Auto-calculate costs** — total cost, cost per serving, and profit margin update automatically
- **Analyze profitability** — find which dishes make money and which don't
- **Track price history** — see how ingredient prices changed over time and how that affects recipe costs
- **Search & filter** — find ingredients by category, price range, or name with full pagination

---

## Tech Stack

- **Backend:** Python, FastAPI
- **Database:** PostgreSQL with SQLAlchemy ORM
- **Migrations:** Alembic
- **Auth:** JWT tokens with bcrypt password hashing
- **Testing:** pytest (54 tests — unit + integration)
- **CI/CD:** GitHub Actions
- **Containerization:** Docker & docker-compose

---

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login and get JWT token |
| GET | `/auth/me` | Get current user info |

### Ingredients
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ingredients/` | Create an ingredient |
| GET | `/ingredients/` | List ingredients (with filter, search, sort, pagination) |
| GET | `/ingredients/{id}` | Get one ingredient |
| PUT | `/ingredients/{id}` | Update an ingredient (auto-records price history) |
| DELETE | `/ingredients/{id}` | Delete an ingredient |

### Recipes
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/recipes/` | Create a recipe |
| GET | `/recipes/` | List recipes (with filter, search, sort, pagination) |
| GET | `/recipes/{id}` | Get recipe with calculated costs |
| PUT | `/recipes/{id}` | Update a recipe |
| DELETE | `/recipes/{id}` | Delete a recipe |
| POST | `/recipes/{id}/ingredients` | Add ingredient to recipe |
| DELETE | `/recipes/{id}/ingredients/{ing_id}` | Remove ingredient from recipe |

### Analysis
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/recipes/analysis/summary` | Overview of all recipes with costs and margins |
| GET | `/recipes/analysis/low-margin` | Flag recipes below profit threshold |
| GET | `/recipes/analysis/cost-breakdown/{id}` | Detailed cost breakdown per ingredient |

### Price History
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/price-history/ingredient/{id}` | Price change history with date filtering |
| GET | `/price-history/recent` | Most recent price changes across all ingredients |

---

## Key Features

### Auto Cost Calculation
When you add ingredients to a recipe, the API automatically calculates:
- **Total cost** — sum of all ingredient costs (price × quantity)
- **Cost per serving** — total cost ÷ number of servings
- **Profit margin** — ((selling price − cost per serving) / selling price) × 100

### Smart Filtering & Pagination
All list endpoints support:
- Filter by category, price range, or name search
- Sort by any field (ascending or descending)
- Pagination with page number, page size, and total count

### Price History Tracking
Every time an ingredient's price changes, the old price is automatically saved with a timestamp. You can query price history by date range to see trends.

### Custom Error Handling
Clean, consistent error responses with specific error codes:
```json
{
  "error": "ingredient_not_found",
  "message": "Ingredient with ID 7 does not exist"
}
```

---

## Quick Start

### Prerequisites
- Docker and docker-compose installed

### Run the project
```bash
git clone https://github.com/Elad255/recipe-cost-calculator.git
cd recipe-cost-calculator
docker compose up --build
```

The API will be available at `http://localhost:8000`

Interactive API docs at `http://localhost:8000/docs`

### Run tests
```bash
docker compose exec app pytest tests/ -v
```

---

## Example Usage

### 1. Register and Login
```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "chef@kitchen.com", "password": "shakshuka123"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "chef@kitchen.com", "password": "shakshuka123"}'
```

### 2. Add Ingredients
```bash
curl -X POST http://localhost:8000/ingredients/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Tomatoes", "category": "Vegetables", "unit": "kg", "price_per_unit": 8.90}'
```

### 3. Create a Recipe and Add Ingredients
```bash
# Create recipe
curl -X POST http://localhost:8000/recipes/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Shakshuka", "category": "Main Course", "servings": 4, "selling_price": 52.00}'

# Add ingredient to recipe
curl -X POST http://localhost:8000/recipes/1/ingredients \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"ingredient_id": 1, "quantity": 0.5}'
```

The response includes auto-calculated costs:
```json
{
  "name": "Shakshuka",
  "total_cost": 4.45,
  "cost_per_serving": 1.11,
  "profit_margin": 97.86
}
```

---

## Project Structure
recipe-cost-calculator/
├── app/
│   ├── models/          # Database models (User, Ingredient, Recipe, etc.)
│   ├── schemas/         # Pydantic schemas for request/response validation
│   ├── routers/         # API endpoint handlers
│   ├── utils/           # Auth, dependencies, custom exceptions
│   ├── config.py        # Environment-based configuration
│   ├── database.py      # Database connection
│   └── main.py          # FastAPI app entry point
├── tests/               # Unit + integration tests (54 tests)
├── alembic/             # Database migrations
├── .github/workflows/   # CI/CD pipeline
├── Dockerfile
├── docker-compose.yml
└── requirements.txt

---

## What I Learned Building This

- Designing many-to-many database relationships (recipes ↔ ingredients)
- Professional error handling with custom exception classes
- Search, filter, sort, and pagination for production-ready APIs
- Business logic endpoints that compute insights from data
- Unit testing with MagicMock for isolated logic testing
- Integration testing with TestClient for end-to-end API testing
- Price history tracking with date-range queries
- CI/CD pipeline with GitHub Actions
- Environment-based configuration management

---

## License

