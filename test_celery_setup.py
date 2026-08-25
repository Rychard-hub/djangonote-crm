"""
Celery setup testing script
"""

import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_project.settings')
django.setup()

def test_celery_config():
    """Test Celery configuration"""
    print("🔧 Testing Celery Configuration")
    print("=" * 50)
    
    try:
        # Test Celery app import
        from crm_project.celery import app as celery_app
        print("✅ Celery app imported successfully")
        
        # Test configuration
        print(f"✅ Celery broker: {celery_app.conf.broker_url}")
        print(f"✅ Celery result backend: {celery_app.conf.result_backend}")
        print(f"✅ Celery timezone: {celery_app.conf.timezone}")
        print(f"✅ Celery task serializer: {celery_app.conf.task_serializer}")
        
        # Test tasks import
        from crm.tasks import send_follow_up_reminders, send_daily_reports, generate_lead_pdf
        print("✅ Celery tasks imported successfully")
        
        # Test Django-Celery-Beat setup
        from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule
        print("✅ Django-Celery-Beat models imported successfully")
        
        # Check if scheduled tasks exist
        scheduled_tasks = PeriodicTask.objects.all()
        print(f"✅ Found {scheduled_tasks.count()} scheduled tasks")
        
        for task in scheduled_tasks:
            print(f"   • {task.name} - {task.task}")
        
        return True
        
    except Exception as e:
        print(f"❌ Celery configuration error: {str(e)}")
        return False

def test_email_config():
    """Test email configuration"""
    print("\n📧 Testing Email Configuration")
    print("=" * 50)
    
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        
        print(f"✅ Email backend: {settings.EMAIL_BACKEND}")
        print(f"✅ Email host: {settings.EMAIL_HOST}")
        print(f"✅ Email port: {settings.EMAIL_PORT}")
        print(f"✅ Email use TLS: {settings.EMAIL_USE_TLS}")
        print(f"✅ Default from email: {settings.DEFAULT_FROM_EMAIL}")
        
        # Test sending email (will go to console in development)
        if settings.DEBUG:
            print("✅ Development mode - emails will go to console")
        else:
            print("⚠️  Production mode - ensure SMTP settings are configured")
        
        return True
        
    except Exception as e:
        print(f"❌ Email configuration error: {str(e)}")
        return False

def test_pdf_generation():
    """Test PDF generation capabilities"""
    print("\n📄 Testing PDF Generation")
    print("=" * 50)
    
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from io import BytesIO
        
        # Create a simple test PDF
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.drawString(100, 750, "Test PDF Generation")
        p.save()
        
        buffer.seek(0)
        pdf_data = buffer.getvalue()
        buffer.close()
        
        print(f"✅ PDF generation works (created {len(pdf_data)} bytes)")
        
        # Check PDF directory
        from django.conf import settings
        import os
        
        pdf_dir = settings.PDF_ROOT
        os.makedirs(pdf_dir, exist_ok=True)
        print(f"✅ PDF directory ready: {pdf_dir}")
        
        return True
        
    except Exception as e:
        print(f"❌ PDF generation error: {str(e)}")
        return False

def test_redis_connection():
    """Test Redis connection if available"""
    print("\n🔴 Testing Redis Connection")
    print("=" * 50)
    
    try:
        import redis
        from django.conf import settings
        
        r = redis.Redis.from_url(settings.REDIS_URL)
        r.ping()
        
        print(f"✅ Redis connection successful: {settings.REDIS_URL}")
        print("✅ Redis is available for Celery")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Redis not available: {str(e)}")
        print("✅ Falling back to memory broker for development")
        return False

def main():
    """Main test function"""
    print("🎯 Celery & Background Tasks Setup Test")
    print("=" * 60)
    
    results = {
        'celery': test_celery_config(),
        'email': test_email_config(),
        'pdf': test_pdf_generation(),
        'redis': test_redis_connection(),
    }
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS")
    print("=" * 60)
    
    for component, success in results.items():
        status = "✅ Working" if success else "❌ Error"
        print(f"{component.capitalize()}: {status}")
    
    # Overall result
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n📋 NEXT STEPS:")
        print("1. Install Redis for production: https://redis.io/download")
        print("2. Start Celery worker: celery -A crm_project worker -l info")
        print("3. Start Celery beat: celery -A crm_project beat -l info")
        print("4. Test background tasks")
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("Check the errors above and fix configuration issues")
    
    return all_passed

if __name__ == "__main__":
    main()
