from django.db import migrations


def seed_plans_and_subscriptions(apps, schema_editor):
    Plan = apps.get_model('billing', 'Plan')
    Subscription = apps.get_model('billing', 'Subscription')
    Organization = apps.get_model('accounts', 'Organization')

    free_plan, _ = Plan.objects.get_or_create(
        code='free',
        defaults={
            'name': 'Free',
            'monthly_price': 0,
            'max_payment_links_per_month': 3,
            'ai_content_quota': 0,
            'features': [],
        },
    )
    Plan.objects.get_or_create(
        code='pro',
        defaults={
            'name': 'Pro',
            'monthly_price': 29,
            'max_payment_links_per_month': 0,
            'ai_content_quota': 50,
            'features': ['ai_content', 'ai_video'],
        },
    )

    for organization in Organization.objects.all():
        Subscription.objects.get_or_create(organization=organization, defaults={'plan': free_plan})


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0002_plan_subscription'),
        ('accounts', '0002_backfill_organizations'),
    ]

    operations = [
        migrations.RunPython(seed_plans_and_subscriptions, noop_reverse),
    ]
