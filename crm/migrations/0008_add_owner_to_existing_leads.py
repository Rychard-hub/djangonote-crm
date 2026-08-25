# Generated migration for adding owner field to existing models

from django.db import migrations, models
from django.conf import settings


def set_default_owner(apps, schema_editor):
    Lead = apps.get_model('crm', 'Lead')
    Comment = apps.get_model('crm', 'Comment')
    Task = apps.get_model('crm', 'Task')
    Activity = apps.get_model('crm', 'Activity')
    
    # Get or create a default user (first user in the system)
    User = apps.get_model('auth', 'User')
    default_user = User.objects.first()
    
    if default_user:
        # Set owner for all existing leads
        Lead.objects.filter(owner__isnull=True).update(owner=default_user)
        
        # Set created_by for existing comments, tasks, and activities
        Comment.objects.filter(created_by__isnull=True).update(created_by=default_user)
        Task.objects.filter(created_by__isnull=True).update(created_by=default_user)
        Activity.objects.filter(created_by__isnull=True).update(created_by=default_user)


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0007_auto_20260629_2023'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Add owner field to Lead with nullable first
        migrations.AddField(
            model_name='lead',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=models.CASCADE,
                related_name='leads',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        # Add created_by fields to other models
        migrations.AddField(
            model_name='comment',
            name='created_by',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=models.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='task',
            name='created_by',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=models.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='activity',
            name='created_by',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=models.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        # Run data migration
        migrations.RunPython(set_default_owner),
        # Make fields non-nullable
        migrations.AlterField(
            model_name='lead',
            name='owner',
            field=models.ForeignKey(
                on_delete=models.CASCADE,
                related_name='leads',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
