from django.db import migrations


def backfill_lead_organization(apps, schema_editor):
    Lead = apps.get_model('crm', 'Lead')
    Membership = apps.get_model('accounts', 'Membership')

    for membership in Membership.objects.all():
        Lead.objects.filter(
            owner_id=membership.user_id,
            organization__isnull=True,
        ).update(organization_id=membership.organization_id)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0012_lead_organization'),
        ('accounts', '0002_backfill_organizations'),
    ]

    operations = [
        migrations.RunPython(backfill_lead_organization, noop_reverse),
    ]
