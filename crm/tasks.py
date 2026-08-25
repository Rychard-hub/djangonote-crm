"""
Celery tasks for CRM application
"""

import logging
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from django.db import models
from celery import shared_task
from .models import Lead, Activity, Profile

logger = logging.getLogger(__name__)

@shared_task(name='crm.tasks.send_follow_up_reminders')
def send_follow_up_reminders():
    """
    Send follow-up reminders for leads that need attention
    """
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)
    
    # Get leads that need follow-up today or tomorrow
    leads_needing_followup = Lead.objects.filter(
        next_follow_up__date__in=[today, tomorrow],
        status__in=['new', 'contacted', 'proposal']
    ).select_related('owner')
    
    sent_count = 0
    
    for lead in leads_needing_followup:
        try:
            # Get user's profile for reminder preferences
            profile = Profile.objects.filter(user=lead.owner).first()
            
            if profile and profile.reminder_days:
                # Check if we should send reminder based on user's preference
                days_until_followup = (lead.next_follow_up.date() - today).days
                
                if days_until_followup <= profile.reminder_days:
                    # Send email reminder
                    subject = f"Follow-up Reminder: {lead.name}"
                    
                    context = {
                        'lead': lead,
                        'days_until': days_until_followup,
                        'user': lead.owner,
                    }
                    
                    message = render_to_string('crm/email/follow_up_reminder.txt', context)
                    html_message = render_to_string('crm/email/follow_up_reminder.html', context)
                    
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[lead.owner.email],
                        html_message=html_message,
                        fail_silently=False,
                    )
                    
                    # Log the activity
                    Activity.objects.create(
                        lead=lead,
                        action='reminder_sent',
                        details=f"Follow-up reminder sent to {lead.owner.email}",
                        created_by=lead.owner
                    )
                    
                    sent_count += 1
                    logger.info(f"Follow-up reminder sent for lead {lead.id} to {lead.owner.email}")
            
        except Exception as e:
            logger.error(f"Error sending follow-up reminder for lead {lead.id}: {str(e)}")
    
    logger.info(f"Follow-up reminders completed. Sent {sent_count} reminders.")
    return f"Sent {sent_count} follow-up reminders"

@shared_task(name='crm.tasks.send_daily_reports')
def send_daily_reports():
    """
    Send daily activity reports to users
    """
    yesterday = timezone.now().date() - timedelta(days=1)
    
    # Get all users who should receive reports
    users_with_profiles = Profile.objects.filter(
        user__is_active=True,
        reminder_days__gt=0
    ).select_related('user')
    
    sent_count = 0
    
    for profile in users_with_profiles:
        try:
            user = profile.user
            
            # Get user's leads
            user_leads = Lead.objects.filter(owner=user)
            
            # Calculate statistics
            stats = {
                'total_leads': user_leads.count(),
                'new_leads': user_leads.filter(status='new', created_at__date=yesterday).count(),
                'contacted_leads': user_leads.filter(status='contacted', updated_at__date=yesterday).count(),
                'proposal_leads': user_leads.filter(status='proposal', updated_at__date=yesterday).count(),
                'won_leads': user_leads.filter(status='won', updated_at__date=yesterday).count(),
                'lost_leads': user_leads.filter(status='lost', updated_at__date=yesterday).count(),
                'total_budget': float(user_leads.aggregate(total=models.Sum('budget'))['total'] or 0),
                'won_budget': float(user_leads.filter(status='won').aggregate(total=models.Sum('budget'))['total'] or 0),
            }
            
            # Get recent activities
            recent_activities = Activity.objects.filter(
                lead__owner=user,
                created_at__date=yesterday
            ).order_by('-created_at')[:10]
            
            # Get upcoming follow-ups
            upcoming_followups = user_leads.filter(
                next_follow_up__date__lte=timezone.now().date() + timedelta(days=7),
                status__in=['new', 'contacted', 'proposal']
            ).order_by('next_follow_up')[:5]
            
            context = {
                'user': user,
                'profile': profile,
                'stats': stats,
                'activities': recent_activities,
                'followups': upcoming_followups,
                'report_date': yesterday,
            }
            
            subject = f"Daily CRM Report - {yesterday.strftime('%Y-%m-%d')}"
            message = render_to_string('crm/email/daily_report.txt', context)
            html_message = render_to_string('crm/email/daily_report.html', context)
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            sent_count += 1
            logger.info(f"Daily report sent to {user.email}")
            
        except Exception as e:
            logger.error(f"Error sending daily report to {profile.user.email}: {str(e)}")
    
    logger.info(f"Daily reports completed. Sent {sent_count} reports.")
    return f"Sent {sent_count} daily reports"

@shared_task(name='crm.tasks.cleanup_old_activities')
def cleanup_old_activities():
    """
    Clean up old activities to keep database clean
    """
    # Delete activities older than 6 months
    cutoff_date = timezone.now() - timedelta(days=180)
    
    deleted_count = Activity.objects.filter(
        created_at__lt=cutoff_date
    ).delete()[0]
    
    logger.info(f"Cleaned up {deleted_count} old activities")
    return f"Deleted {deleted_count} old activities"

@shared_task(name='crm.tasks.generate_lead_pdf')
def generate_lead_pdf(lead_id):
    """
    Generate PDF report for a specific lead
    """
    try:
        from django.http import HttpResponse
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.units import inch
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
        from io import BytesIO
        import os
        
        lead = Lead.objects.get(id=lead_id)
        
        # Create PDF in memory
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        normal_style = styles['Normal']
        
        # Build PDF content
        story = []
        
        # Title
        story.append(Paragraph(f"Lead Report: {lead.name}", title_style))
        story.append(Spacer(1, 12))
        
        # Lead information table
        data = [
            ['Field', 'Value'],
            ['Name', lead.name],
            ['Company', lead.company or ''],
            ['Email', lead.email or ''],
            ['Phone', lead.phone or ''],
            ['Status', lead.status_display],
            ['Budget', f"€{lead.budget}" if lead.budget else ''],
            ['Created', lead.created_at.strftime('%Y-%m-%d')],
            ['Last Contact', lead.last_contacted.strftime('%Y-%m-%d') if lead.last_contacted else ''],
            ['Next Follow-up', lead.next_follow_up.strftime('%Y-%m-%d') if lead.next_follow_up else ''],
        ]
        
        table = Table(data)
        story.append(table)
        story.append(Spacer(1, 12))
        
        # Notes
        if lead.notes:
            story.append(Paragraph("Notes:", normal_style))
            story.append(Paragraph(lead.notes, normal_style))
        
        # Build PDF
        doc.build(story)
        
        # Save to file
        pdf_filename = f"lead_{lead.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = os.path.join(settings.PDF_ROOT, pdf_filename)
        
        # Ensure PDF directory exists
        os.makedirs(settings.PDF_ROOT, exist_ok=True)
        
        with open(pdf_path, 'wb') as f:
            f.write(buffer.getvalue())
        
        buffer.close()
        
        # Log activity
        Activity.objects.create(
            lead=lead,
            action='pdf_generated',
            details=f"PDF report generated: {pdf_filename}",
            created_by=lead.owner
        )
        
        logger.info(f"PDF generated for lead {lead.id}: {pdf_filename}")
        return pdf_filename
        
    except Exception as e:
        logger.error(f"Error generating PDF for lead {lead_id}: {str(e)}")
        raise

@shared_task(name='crm.tasks.send_welcome_email')
def send_welcome_email(lead_id):
    """
    Send welcome email to new lead
    """
    try:
        lead = Lead.objects.get(id=lead_id)
        
        subject = f"Welcome to our CRM system - {lead.name}"
        
        context = {
            'lead': lead,
            'company': lead.company or 'Your Company',
        }
        
        message = render_to_string('crm/email/welcome_lead.txt', context)
        html_message = render_to_string('crm/email/welcome_lead.html', context)
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[lead.email] if lead.email else [],
            html_message=html_message,
            fail_silently=False,
        )
        
        # Log activity
        Activity.objects.create(
            lead=lead,
            action='email_sent',
            details=f"Welcome email sent to {lead.email}",
            created_by=lead.owner
        )
        
        logger.info(f"Welcome email sent to lead {lead.id}")
        return f"Welcome email sent to {lead.email}"
        
    except Exception as e:
        logger.error(f"Error sending welcome email to lead {lead_id}: {str(e)}")
        raise

@shared_task(name='crm.tasks.process_mcp_request')
def process_mcp_request(tool_name, arguments, user_id):
    """
    Process MCP requests asynchronously
    """
    try:
        from .mcp_bridge import MCPBridge
        
        # Initialize MCP bridge
        bridge = MCPBridge()
        
        # Process the request
        result = getattr(bridge, tool_name)(**arguments)
        
        logger.info(f"MCP request processed: {tool_name} for user {user_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error processing MCP request {tool_name}: {str(e)}")
        raise
