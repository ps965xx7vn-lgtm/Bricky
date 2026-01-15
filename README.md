# Bricky

A Django-based e-commerce platform with integrated Telegram bot support.

## Project Structure

### Backend (`/backend`)

The main Django application with the following apps:

#### **Core** (`/core`)
- Main application handling base functionality
- Contains templates for pages and legal documents
- Custom template filters and tags
- Contact messages and newsletter subscriptions
- Help categories and articles

#### **Store** (`/store`)
- Product catalog and category management
- Shopping cart functionality
- Product status tracking
- Templates for storefront pages

#### **Orders** (`/orders`)
- Order management and processing
- Order status tracking
- UUID-based order identification
- Signal handlers for order events
- Order templates and views

#### **Users** (`/users`)
- Custom user model (CustomUser)
- User authentication and profile management
- Email verification system
- Telegram ID integration
- User-related forms and templates

#### **Notifications** (`/notifications`)
- Notification system
- Newsletter subscription management
- Email notification templates

#### **Telegram Bot** (`/tgbot`)
- Telegram bot integration (`bot.py`)
- Bot commands and handlers

## Key Features

- Custom user model with Telegram ID support
- Shopping cart with multiple items
- Product categorization
- Order management with status tracking
- Email verification system
- Newsletter subscription
- Help/FAQ system
- Contact form
- User authentication and profiles
- Telegram bot integration

## Installation

1. Clone the repository
2. Install dependencies from `pyproject.toml`
3. Navigate to the backend directory
4. Run migrations:
   ```
   python manage.py migrate
   ```
5. Create a superuser:
   ```
   python manage.py createsuperuser
   ```
6. Collect static files:
   ```
   python manage.py collectstatic
   ```

## Running the Application

```bash
cd backend
python manage.py runserver
```

The application will be available at `http://localhost:8000/`

## Database

SQLite database is used for development (`db.sqlite3`)

## Media Files

- Product images: `/media/products/`
- Category images: `/media/categories/`
- User profile pictures: `/media/user_pictures/`

## Static Files

Static files are organized by app in the `/static/` directory and compiled to `/staticfiles/` for production.
