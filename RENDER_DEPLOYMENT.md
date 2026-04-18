# 🚀 Rendering Deployment Guide (Free Tier)

Your Django app is now optimized for deploying to **Render.com free tier** without SQLite.

## Prerequisites

- GitHub account with your repository
- Render account (free tier)
- PostgreSQL database on Render

## Step-by-Step Deployment

## Render Commands (Use Exactly These)

- **Build Command**
  ```bash
  pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
  ```

- **Start Command**
  ```bash
  gunicorn market_nearby.wsgi:application
  ```

### 1. Create PostgreSQL Database on Render

1. Go to [render.com](https://render.com)
2. Click "New +" → "PostgreSQL"
3. Set database name, user, and password
4. Choose free tier
5. Note down: Host, Port, Username, Password, Database name

### 2. Deploy Web Service

1. Go to Render dashboard
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Set the following:
   - **Name**: market-nearby (or your choice)
   - **Environment**: Python 3
   - **Build Command**:
     ```
     pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
     ```
   - **Start Command**:
     ```
     gunicorn market_nearby.wsgi:application
     ```

### 3. Set Environment Variables on Render

In the Render dashboard, add these environment variables:

```
DB_NAME=<database_name_from_postgres>
DB_USER=<username_from_postgres>
DB_PASSWORD=<password_from_postgres>
DB_HOST=<host_from_postgres>
DB_PORT=5432
ALLOWED_HOSTS=yourdomain.onrender.com,www.yourdomain.onrender.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.onrender.com,https://www.yourdomain.onrender.com
DEBUG=False
SECURE_SSL_REDIRECT=True
```

### 4. Deploy

1. Click "Create Web Service"
2. Render will automatically deploy from your GitHub push
3. Check the logs for any errors

### 5. Access Your App

Once deployment is complete:
- Your app will be at: `https://yourdomain.onrender.com`
- Django admin at: `https://yourdomain.onrender.com/admin`

### 6. Create Superuser on Render

In Render dashboard, go to your Web Service → "Shell" and run:

```bash
python manage.py createsuperuser
```

## File Changes for Production

✅ Added **gunicorn** - production WSGI server
✅ Added **whitenoise** - efficient static file serving
✅ Added **dj-database-url** - database URL parsing
✅ Configured **ALLOWED_HOSTS** from environment
✅ Configured **CSRF_TRUSTED_ORIGINS** for security
✅ Added **WhiteNoise middleware** for static files
✅ Removed all SQLite references
✅ Added **render.yaml** configuration file

## Important Notes

- **No SQLite**: PostgreSQL is the only database supported
- **Static Files**: WhiteNoise handles serving static files efficiently
- **Security**: SSL redirect and HSTS enabled in production
- **Free Tier Limits**: 
  - Web service: 750 hours/month (essentially unlimited)
  - PostgreSQL: 90 days inactivity = auto-delete
  - Keep at least once monthly active to maintain DB

## Troubleshooting

### 500 Error on Deployment
Check logs in Render dashboard. Common issues:
- Wrong database credentials
- Missing environment variables
- Database not created yet

### Static Files Not Loading
WhiteNoise should handle this. If issues:
```
python manage.py collectstatic --noinput
```

### Database Connection Failed
Verify:
- PostgreSQL service is running
- Database credentials are correct
- Database is accessible from Render

## Local Development

For local dev, use `.env` file:
```bash
source .env
python manage.py runserver
```

## Advanced Customization

For more details, see:
- [Render Django Documentation](https://render.com/docs/deploy-django)
- [WhiteNoise Documentation](http://whitenoise.evans.io/)
