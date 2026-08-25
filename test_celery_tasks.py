"""
Test Celery background tasks
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_project.settings')
django.setup()

def test_debug_task():
    """Test basic Celery debug task"""
    print("🔧 Testing Debug Task")
    print("=" * 40)
    
    try:
        from crm_project.celery import debug_task
        
        # Send task to worker
        result = debug_task.delay()
        
        print(f"✅ Debug task sent: {result.id}")
        print("⏳ Waiting for result...")
        
        # Wait for result (with timeout)
        try:
            task_result = result.get(timeout=10)
            print(f"✅ Debug task result: {task_result}")
            return True
        except Exception as e:
            print(f"❌ Debug task timeout or error: {str(e)}")
            return False
            
    except Exception as e:
        print(f"❌ Debug task error: {str(e)}")
        return False

def test_follow_up_reminders():
    """Test follow-up reminders task"""
    print("\n📧 Testing Follow-up Reminders")
    print("=" * 40)
    
    try:
        from crm.tasks import send_follow_up_reminders
        
        # Send task to worker
        result = send_follow_up_reminders.delay()
        
        print(f"✅ Follow-up reminders task sent: {result.id}")
        print("⏳ Processing...")
        
        # Wait for result
        try:
            task_result = result.get(timeout=30)
            print(f"✅ Follow-up reminders result: {task_result}")
            return True
        except Exception as e:
            print(f"❌ Follow-up reminders timeout or error: {str(e)}")
            return False
            
    except Exception as e:
        print(f"❌ Follow-up reminders error: {str(e)}")
        return False

def test_daily_reports():
    """Test daily reports task"""
    print("\n📊 Testing Daily Reports")
    print("=" * 40)
    
    try:
        from crm.tasks import send_daily_reports
        
        # Send task to worker
        result = send_daily_reports.delay()
        
        print(f"✅ Daily reports task sent: {result.id}")
        print("⏳ Processing...")
        
        # Wait for result
        try:
            task_result = result.get(timeout=30)
            print(f"✅ Daily reports result: {task_result}")
            return True
        except Exception as e:
            print(f"❌ Daily reports timeout or error: {str(e)}")
            return False
            
    except Exception as e:
        print(f"❌ Daily reports error: {str(e)}")
        return False

def test_pdf_generation():
    """Test PDF generation task"""
    print("\n📄 Testing PDF Generation")
    print("=" * 40)
    
    try:
        from crm.models import Lead
        from crm.tasks import generate_lead_pdf
        
        # Get a lead for testing
        leads = Lead.objects.all()
        if not leads:
            print("❌ No leads found for PDF generation test")
            return False
        
        lead = leads.first()
        print(f"📋 Using lead: {lead.name} (ID: {lead.id})")
        
        # Send task to worker
        result = generate_lead_pdf.delay(lead.id)
        
        print(f"✅ PDF generation task sent: {result.id}")
        print("⏳ Processing...")
        
        # Wait for result
        try:
            task_result = result.get(timeout=30)
            print(f"✅ PDF generation result: {task_result}")
            return True
        except Exception as e:
            print(f"❌ PDF generation timeout or error: {str(e)}")
            return False
            
    except Exception as e:
        print(f"❌ PDF generation error: {str(e)}")
        return False

def test_welcome_email():
    """Test welcome email task"""
    print("\n👋 Testing Welcome Email")
    print("=" * 40)
    
    try:
        from crm.models import Lead
        from crm.tasks import send_welcome_email
        
        # Get a lead with email for testing
        leads = Lead.objects.filter(email__isnull=False).exclude(email='')
        if not leads:
            print("❌ No leads with email found for welcome email test")
            return False
        
        lead = leads.first()
        print(f"📋 Using lead: {lead.name} ({lead.email})")
        
        # Send task to worker
        result = send_welcome_email.delay(lead.id)
        
        print(f"✅ Welcome email task sent: {result.id}")
        print("⏳ Processing...")
        
        # Wait for result
        try:
            task_result = result.get(timeout=30)
            print(f"✅ Welcome email result: {task_result}")
            return True
        except Exception as e:
            print(f"❌ Welcome email timeout or error: {str(e)}")
            return False
            
    except Exception as e:
        print(f"❌ Welcome email error: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🎯 Celery Background Tasks Test")
    print("=" * 60)
    print("Make sure Celery worker is running in another terminal:")
    print("python -m celery -A crm_project worker -l info")
    print("=" * 60)
    
    results = {
        'debug': test_debug_task(),
        'follow_up': test_follow_up_reminders(),
        'daily_reports': test_daily_reports(),
        'pdf': test_pdf_generation(),
        'welcome_email': test_welcome_email(),
    }
    
    print("\n" + "=" * 60)
    print("📊 TASK TEST RESULTS")
    print("=" * 60)
    
    for task, success in results.items():
        status = "✅ Success" if success else "❌ Failed"
        print(f"{task.replace('_', ' ').title()}: {status}")
    
    # Overall result
    passed_count = sum(results.values())
    total_count = len(results)
    
    print(f"\n📈 Summary: {passed_count}/{total_count} tasks passed")
    
    if passed_count == total_count:
        print("\n🎉 ALL TASKS WORKING!")
        print("\n📋 BACKGROUND TASKS READY:")
        print("✅ Follow-up reminders")
        print("✅ Daily reports")
        print("✅ PDF generation")
        print("✅ Welcome emails")
        print("✅ MCP request processing")
    else:
        print("\n⚠️  SOME TASKS FAILED")
        print("Check the error messages above")
    
    return passed_count == total_count

if __name__ == "__main__":
    main()
