from django.db import migrations
from django.utils.text import slugify


def unique_slug(base, taken):
    slug = slugify(base) or 'org'
    candidate = slug
    suffix = 2
    while candidate in taken:
        candidate = f'{slug}-{suffix}'
        suffix += 1
    taken.add(candidate)
    return candidate


def backfill_organizations(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Profile = apps.get_model('crm', 'Profile')
    Organization = apps.get_model('accounts', 'Organization')
    Membership = apps.get_model('accounts', 'Membership')

    taken_slugs = set(Organization.objects.values_list('slug', flat=True))

    for user in User.objects.all():
        if Membership.objects.filter(user=user).exists():
            continue

        profile = Profile.objects.filter(user=user).first()
        org_name = (profile.organization if profile else '') or f'{user.username} workspace'

        org = Organization.objects.create(
            name=org_name,
            slug=unique_slug(org_name, taken_slugs),
        )
        Membership.objects.create(user=user, organization=org, role='owner')


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('crm', '0011_alter_activity_id_alter_activity_lead_and_more'),
    ]

    operations = [
        migrations.RunPython(backfill_organizations, noop_reverse),
    ]
