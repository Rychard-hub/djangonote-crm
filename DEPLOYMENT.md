# Django CRM Production Deployment Guide

## Overview
This guide covers deploying the Django CRM to production using Docker, PostgreSQL, Redis, and Nginx.

## Prerequisites
- Docker and Docker Compose
- Domain name
- SSL certificates (Let's Encrypt recommended)
- Server with at least 2GB RAM

## Environment Setup

### 1. Clone and Configure
```bash
git clone <your-repo>
cd Django-CRM
```

### 2. Environment Variables
Copy the example environment file and configure:
```bash
cp .env.example .env
```

Edit `.env` with your production values:
```bash
# Generate a new secret key
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Set your values
DJANGO_SECRET_KEY=your-generated-secret-key
DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgres://username:password@db:5432/crm_db
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 3. SSL Certificates
Generate SSL certificates using Let's Encrypt:
```bash
# Install certbot
sudo apt install certbot

# Generate certificates
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Copy certificates to project directory
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ./ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ./ssl/key.pem
sudo chown $USER:$USER ./ssl/*.pem
```

## Deployment

### 1. Build and Start Services
```bash
# Build and start all services
docker-compose -f docker-compose.production.yml up --build -d

# View logs
docker-compose -f docker-compose.production.yml logs -f
```

### 2. Initialize Database
```bash
# Run migrations
docker-compose -f docker-compose.production.yml exec web python manage.py migrate

# Create superuser (optional)
docker-compose -f docker-compose.production.yml exec web python manage.py createsuperuser

# Collect static files
docker-compose -f docker-compose.production.yml exec web python manage.py collectstatic --noinput
```

### 3. Verify Deployment
Check that all services are running:
```bash
docker-compose -f docker-compose.production.yml ps
```

Test the application:
- Visit `https://yourdomain.com/admin/`
- Test API endpoints at `https://yourdomain.com/api/`

## Service Management

### View Logs
```bash
# All services
docker-compose -f docker-compose.production.yml logs -f

# Specific service
docker-compose -f docker-compose.production.yml logs -f web
docker-compose -f docker-compose.production.yml logs -f celery
```

### Update Application
```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose -f docker-compose.production.yml up --build -d

# Run migrations if needed
docker-compose -f docker-compose.production.yml exec web python manage.py migrate
```

### Backup Database
```bash
# Create backup
docker-compose -f docker-compose.production.yml exec db pg_dump -U crm_user crm_db > backup.sql

# Restore backup
docker-compose -f docker-compose.production.yml exec -T db psql -U crm_user crm_db < backup.sql
```

## Monitoring

### Health Checks
All services include health checks. Monitor with:
```bash
docker-compose -f docker-compose.production.yml ps
```

### Logs Rotation
Set up log rotation for Docker logs:
```bash
# Add to /etc/logrotate.d/docker-containers
/var/lib/docker/containers/*/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
}
```

## Security Considerations

### 1. Firewall
```bash
# Allow only necessary ports
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### 2. Regular Updates
```bash
# Update Docker images regularly
docker-compose -f docker-compose.production.yml pull
docker-compose -f docker-compose.production.yml up -d
```

### 3. SSL Certificate Renewal
Set up automatic renewal:
```bash
# Add to crontab
0 12 * * * /usr/bin/certbot renew --quiet && docker-compose -f /path/to/Django-CRM/docker-compose.production.yml restart nginx
```

## Performance Optimization

### 1. Database Optimization
- Add indexes to frequently queried fields
- Use connection pooling
- Monitor slow queries

### 2. Caching
- Redis is configured for caching
- Consider CDN for static files
- Enable browser caching headers

### 3. Application Scaling
- Increase worker count based on CPU cores
- Use load balancer for multiple web servers
- Consider read replicas for database

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check DATABASE_URL in .env
   - Verify database container is running
   - Check network connectivity

2. **Static Files Not Loading**
   - Run `collectstatic` command
   - Check Nginx configuration
   - Verify file permissions

3. **Celery Tasks Not Running**
   - Check Redis connection
   - Verify Celery worker logs
   - Check task registration

### Debug Commands
```bash
# Enter container shell
docker-compose -f docker-compose.production.yml exec web bash

# Check Django settings
docker-compose -f docker-compose.production.yml exec web python manage.py diffsettings

# Test database connection
docker-compose -f docker-compose.production.yml exec web python manage.py dbshell
```

## Production Checklist

Before going live, ensure:

- [ ] SECRET_KEY is set and secure
- [ ] DEBUG = False
- [ ] ALLOWED_HOSTS is configured
- [ ] Database is PostgreSQL (not SQLite)
- [ ] SSL certificates are installed
- [ ] Environment variables are set
- [ ] Backup strategy is in place
- [ ] Monitoring is configured
- [ ] Security headers are enabled
- [ ] Rate limiting is configured
- [ ] Log rotation is set up

## Support

For issues:
1. Check logs: `docker-compose logs`
2. Verify configuration: Check .env file
3. Test services individually
4. Check resource usage: `docker stats`
