# Backend Setup

## 1. Install MongoDB (macOS)

```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
# Verify: mongo --eval "db.runCommand({ connectionStatus: 1 })"
```

## 2. Python environment

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. Configure

```bash
cp .env.example .env
# .env already has dev defaults — no changes needed for local
```

## 4. Seed the database

```bash
python manage.py seed_data
# Re-seed cleanly:
python manage.py seed_data --flush
```

Default login: `admin@arihant.local` / `admin123`

## 5. Run the dev server

```bash
python manage.py runserver 8000
```

## API endpoints

| Method | URL | Auth | Description |
|--------|-----|------|-------------|
| POST | `/api/auth/login/` | ✗ | Returns access + refresh tokens |
| POST | `/api/auth/refresh/` | ✗ | Refresh access token |
| GET | `/api/auth/me/` | ✓ | Current user |
| PATCH | `/api/auth/me/update/` | ✓ | Update name / password |
| GET | `/api/products/` | ✓ | List products with filters |
| POST | `/api/products/create/` | ✓ | Create product |
| GET/PATCH/DELETE | `/api/products/<id>/` | ✓ | Single product |
| POST | `/api/products/<id>/adjust-stock/` | ✓ | Adjust stock by delta |
| GET | `/api/products/categories/` | ✓ | List categories |
| POST | `/api/products/categories/create/` | ✓ | Create category |
| PATCH/DELETE | `/api/products/categories/<id>/` | ✓ | Update/delete category |
| GET | `/api/products/brands/` | ✓ | List brands |
| GET | `/api/sales/` | ✓ | List sales (read-only) |
| GET | `/api/analytics/dashboard/` | ✓ | Dashboard KPIs |
| GET | `/api/analytics/pl/` | ✓ | P&L summary + trends |

### Product filter query params

```
?q=          text search (name, brand, sku, compatibleWith)
?category=   category id
?brands=     repeatable: ?brands=Spigen&brands=Ringke
?colors=     repeatable
?compat=     repeatable
?stock=      all | inStock | low | out
?price_min=  integer
?price_max=  integer
?sort_by=    name | priceAsc | priceDesc | stock | sales
?page=       1-based (default 1)
?page_size=  default 50, max 200
```

### Sales filter query params

```
?range=          days back from today (default 30)
?category=       category id
?payment_method= UPI | Cash | Card | all
?page=
?page_size=
```

### Auth header

```
Authorization: Bearer <access_token>
```
