# Haven Storefront

A responsive Django e-commerce demo for considered home goods. It includes a browsable product catalog, category/search filtering, product details, a session-backed shopping bag, checkout, saved orders, and Django admin management.

## Run locally

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_products
python manage.py runserver
```

Open `http://127.0.0.1:8000/`. This is a Django application: the VS Code Live Server extension only serves static files and cannot render Django templates or run the backend. The simplest Windows startup is to double-click `run_storefront.bat`; it applies migrations, seeds the catalog, and starts Django. In VS Code, you can also choose **Django: Haven storefront** from **Run and Debug** (F5). The Django admin is at `/admin/`; create an admin user with `python manage.py createsuperuser`.

The sample catalog contains 20 products, with five items in each category: Objects, Textiles, Lighting, and Table. Rerun `python manage.py seed_products` after updating the sample catalog; it safely updates existing sample records by slug.

Checkout creates a pending order in SQLite and does not collect payment. Product photos are stored locally under `static/catalog/products/`; display fonts are loaded from Google Fonts and require an internet connection. Before deployment, set a secure `SECRET_KEY`, turn off `DEBUG`, configure `ALLOWED_HOSTS`, and use a production database and payment provider.

## Tests

```powershell
python manage.py test
```
