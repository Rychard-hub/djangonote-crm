from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify


class OrganizationManager(models.Manager):
    def create_for_user(self, user, name=None):
        """Create an Organization plus its owning Membership for a new user."""
        org_name = name or f'{user.username} workspace'
        base_slug = slugify(org_name) or 'org'
        slug = base_slug
        suffix = 2
        while self.filter(slug=slug).exists():
            slug = f'{base_slug}-{suffix}'
            suffix += 1

        organization = self.create(name=org_name, slug=slug)
        Membership.objects.create(user=user, organization=organization, role='owner')
        return organization


class Organization(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = OrganizationManager()

    def __str__(self):
        return self.name


class Membership(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('member', 'Member'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='membership')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='members')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='owner')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} @ {self.organization.name}'


def get_organization(user):
    """Resolve the tenant Organization for a logged-in user.

    Provisions one on the fly for a user with no Membership -- e.g. an
    account created via the admin, `createsuperuser`, or a script, rather
    than through the registration flow that normally calls
    Organization.objects.create_for_user().
    """
    membership = Membership.objects.filter(user=user).select_related('organization').first()
    if membership is None:
        return Organization.objects.create_for_user(user)
    return membership.organization
