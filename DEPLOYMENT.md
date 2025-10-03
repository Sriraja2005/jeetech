# Deployment Guide

This guide explains how to deploy your Django e-commerce project to various hosting platforms.

## Prerequisites

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**
   - Copy `.env.example` to `.env`
   - Update the values according to your hosting environment

## Hosting Platform Options

### 1. Heroku Deployment

1. **Install Heroku CLI**
2. **Login to Heroku**
   ```bash
   heroku login
   ```

3. **Create Heroku App**
   ```bash
   heroku create your-app-name
   ```

4. **Set Environment Variables**
   ```bash
   heroku config:set SECRET_KEY="your-secret-key"
   heroku config:set DEBUG=False
   heroku config:set ALLOWED_HOSTS="your-app-name.herokuapp.com"
   heroku config:set DJANGO_SETTINGS_MODULE="backend.settings_production"
   ```

5. **Add PostgreSQL Database**
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```

6. **Deploy**
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

### 2. Render.com Deployment (Recommended)

1. **Connect GitHub Repository** to Render.com
2. **Create Web Service** from your repository
3. **Set Environment Variables** in Render dashboard:
   ```env
   SECRET_KEY=your-production-secret-key-here
   DEBUG=False
   ALLOWED_HOSTS=jeetech.onrender.com
   CSRF_TRUSTED_ORIGINS=https://jeetech.onrender.com
   DJANGO_SETTINGS_MODULE=backend.settings_production
   ```

4. **Add PostgreSQL Database** from Render services
5. **Set Build Command**: `pip install -r requirements.txt`
6. **Set Start Command**: `gunicorn backend.wsgi:application`
7. **Deploy** - Render will automatically deploy on git push

### 3. Railway Deployment

1. **Connect GitHub Repository**
2. **Set Environment Variables** in Railway dashboard:
   - `SECRET_KEY`
   - `DEBUG=False`
   - `ALLOWED_HOSTS=your-domain.railway.app`
   - `CSRF_TRUSTED_ORIGINS=https://your-domain.railway.app`
   - `DJANGO_SETTINGS_MODULE=backend.settings_production`

3. **Add PostgreSQL Database** from Railway marketplace

### 3. DigitalOcean App Platform

1. **Create App** from GitHub repository
2. **Configure Environment Variables**
3. **Add Managed Database** (PostgreSQL)
4. **Deploy**

### 4. AWS Elastic Beanstalk

1. **Install EB CLI**
2. **Initialize EB Application**
   ```bash
   eb init
   ```

3. **Create Environment**
   ```bash
   eb create production
   ```

4. **Set Environment Variables** in EB console

## Environment Variables for Production

### Required Variables
```env
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
DJANGO_SETTINGS_MODULE=backend.settings_production
DATABASE_URL=postgresql://user:password@host:port/database
```

### Optional Variables
```env
# Static Files
STATIC_ROOT=staticfiles
STATIC_URL=/static/

# Security (HTTPS)
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# CORS
CORS_ALLOW_ALL_ORIGINS=False
CORS_ALLOWED_ORIGINS=https://yourdomain.com

# Redis Cache
REDIS_URL=redis://localhost:6379/0

# Error Monitoring
SENTRY_DSN=your-sentry-dsn

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
```

## Database Migration

After deployment, run migrations:
```bash
# For Heroku
heroku run python manage.py migrate

# For other platforms, use their CLI or console
python manage.py migrate
```

## Static Files Collection

```bash
# Collect static files
python manage.py collectstatic --noinput
```

## Create Superuser

```bash
# For Heroku
heroku run python manage.py createsuperuser

# For other platforms
python manage.py createsuperuser
```

## Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Configure proper `ALLOWED_HOSTS`
- [ ] Use PostgreSQL database
- [ ] Set up proper `SECRET_KEY`
- [ ] Configure static files serving
- [ ] Set up HTTPS (SSL certificates)
- [ ] Configure error monitoring (Sentry)
- [ ] Set up database backups
- [ ] Configure caching (Redis)
- [ ] Test all functionality in production

## Monitoring and Maintenance

1. **Error Monitoring**: Use Sentry for real-time error tracking
2. **Performance Monitoring**: Monitor database queries and response times
3. **Database Backups**: Set up automated backups
4. **Security Updates**: Keep dependencies updated
5. **Log Monitoring**: Monitor application logs for issues

## Troubleshooting

### Common Issues

1. **Static Files Not Loading**
   - Ensure `STATIC_ROOT` is set correctly
   - Run `collectstatic` command
   - Check WhiteNoise configuration

2. **Database Connection Issues**
   - Verify `DATABASE_URL` format
   - Check database credentials
   - Ensure database is accessible

3. **CORS Issues**
   - Configure `CORS_ALLOWED_ORIGINS`
   - Check middleware order
   - Verify frontend domain

4. **CSRF Verification Failed**
   - Add your domain to `CSRF_TRUSTED_ORIGINS`
   - Ensure HTTPS is used in production
   - Check that forms include `{% csrf_token %}`
   - Verify `ALLOWED_HOSTS` includes your domain

5. **SSL/HTTPS Issues**
   - Configure security settings properly
   - Check certificate installation
   - Verify redirect settings

## Support

For deployment issues, check:
1. Platform-specific documentation
2. Django deployment documentation
3. Application logs
4. Database connection logs
