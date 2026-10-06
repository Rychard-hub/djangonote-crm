import re
from datetime import timedelta
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import get_organization
from crm.models import Activity, Comment, EmailVerification, Lead, Profile, Task


def authenticate_test_client(client):
    user = User.objects.create_user(username='tester@example.com', email='tester@example.com', password='StrongPass123!')
    client.force_login(user)
    return user


def create_lead(owner, **kwargs):
    """Lead.objects.create() with the required owner/organization tenancy fields filled in."""
    return Lead.objects.create(owner=owner, organization=get_organization(owner), **kwargs)


class LoginPageTests(TestCase):
    def test_login_page_contains_email_and_password_fields(self):
        response = self.client.get(reverse('login'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="email"')
        self.assertContains(response, 'name="password"')
        self.assertContains(response, 'Prisijungti')


class DashboardPageTests(TestCase):
    def test_dashboard_shows_key_metrics_and_recent_activity(self):
        authenticate_test_client(self.client)
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Šiandien susisiekti')
        self.assertContains(response, 'Nauji')
        self.assertContains(response, 'Pipeline')
        self.assertContains(response, 'Šiandienos užduotys')
        self.assertContains(response, 'Paskutinė veikla')


class AccessControlTests(TestCase):
    def test_anonymous_user_is_redirected_from_protected_pages(self):
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 302)
        self.assertIn('next=', response.url)
        self.assertIn('/dashboard', response.url)


class LeadManagementTests(TestCase):
    def test_lead_list_page_shows_new_lead_button_and_filters(self):
        authenticate_test_client(self.client)
        response = self.client.get(reverse('lead-list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pridėti leadą')
        self.assertContains(response, 'Paieška')
        self.assertContains(response, 'Statusas')

    def test_lead_creation_saves_a_new_lead(self):
        authenticate_test_client(self.client)
        response = self.client.post(
            reverse('lead-create'),
            {
                'name': 'Mantas',
                'company': 'Studio X',
                'email': 'mantas@example.com',
                'phone': '+37060000000',
                'status': 'new',
                'budget': '1500.00',
                'notes': 'Pirmas kontaktas',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Lead.objects.filter(name='Mantas').exists())

    def test_lead_detail_and_edit_delete_workflow(self):
        user = authenticate_test_client(self.client)
        lead = create_lead(user, name='Laura', company='Studio Y', status='proposal', budget='900.00')

        detail_response = self.client.get(reverse('lead-detail', args=[lead.pk]))
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(detail_response, 'Laura')

        edit_response = self.client.post(
            reverse('lead-edit', args=[lead.pk]),
            {'name': 'Laura', 'company': 'Studio Y', 'status': 'won', 'budget': '1200.00', 'notes': 'Updated'},
        )
        self.assertEqual(edit_response.status_code, 302)
        lead.refresh_from_db()
        self.assertEqual(lead.status, 'won')

        delete_response = self.client.post(reverse('lead-delete', args=[lead.pk]))
        self.assertEqual(delete_response.status_code, 302)
        self.assertFalse(Lead.objects.filter(pk=lead.pk).exists())

    def test_inline_status_update_and_comments_and_reminder(self):
        user = authenticate_test_client(self.client)
        lead = create_lead(user, name='Jonas', company='Studio Z', email='jonas@example.com', status='new', budget='600.00')

        status_response = self.client.post(
            reverse('lead-status-update', args=[lead.pk]),
            {'status': 'contacted'},
        )
        self.assertEqual(status_response.status_code, 302)
        lead.refresh_from_db()
        self.assertEqual(lead.status, 'contacted')

        comment_response = self.client.post(
            reverse('lead-comment-add', args=[lead.pk]),
            {'body': 'Vakar kalbėjomės su klientu.'},
        )
        self.assertEqual(comment_response.status_code, 302)
        self.assertTrue(Comment.objects.filter(lead=lead, body='Vakar kalbėjomės su klientu.').exists())

        reminder_response = self.client.post(reverse('lead-reminder-send', args=[lead.pk]))
        self.assertEqual(reminder_response.status_code, 302)

    def test_lead_detail_page_shows_actions_and_task_form(self):
        user = authenticate_test_client(self.client)
        lead = create_lead(user, name='Milda', company='Studio W', status='proposal', budget='900.00')

        response = self.client.get(reverse('lead-detail', args=[lead.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Redaguoti')
        self.assertContains(response, 'Nauja užduotis')
        self.assertContains(response, 'Laimėtas')
        self.assertContains(response, 'Komunikacija')

    def test_task_toggle_and_activity_log_and_quick_actions(self):
        user = authenticate_test_client(self.client)
        lead = create_lead(user, name='Eglė', company='Studio Q', status='new', budget='650.00')
        task = Task.objects.create(lead=lead, title='Paskambinti')

        toggle_response = self.client.post(reverse('task-toggle', args=[task.pk]))
        self.assertEqual(toggle_response.status_code, 302)
        task.refresh_from_db()
        self.assertTrue(task.completed)

        activity_response = self.client.post(
            reverse('lead-status-mark', args=[lead.pk, 'won']),
        )
        self.assertEqual(activity_response.status_code, 302)
        self.assertTrue(Activity.objects.filter(lead=lead, action='status_change').exists())

        quick_action_response = self.client.post(
            reverse('lead-quick-action', args=[lead.pk]),
            {'action': 'reminder'},
        )
        self.assertEqual(quick_action_response.status_code, 302)

    def test_registration_creates_a_user(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'newuser@example.com',
                'email': 'newuser@example.com',
                'password1': 'StrongPass123!',
                'password2': 'StrongPass123!',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser@example.com').exists())

    def test_reminder_sends_an_email(self):
        user = authenticate_test_client(self.client)
        lead = create_lead(user, name='Tomas', company='Studio R', email='tomas@example.com', status='new', budget='400.00')

        with patch('crm.views.send_mail') as mocked_send_mail:
            response = self.client.post(reverse('lead-reminder-send', args=[lead.pk]))

        self.assertEqual(response.status_code, 302)
        mocked_send_mail.assert_called_once()

    def test_followup_list_page_shows_filters_and_followup_items(self):
        user = authenticate_test_client(self.client)
        today = timezone.now().date()
        create_lead(user, name='Asta', company='Studio A', status='new', next_follow_up=today, budget='500.00')
        create_lead(user, name='Marius', company='Studio M', status='contacted', next_follow_up=today - timedelta(days=3), budget='700.00')

        response = self.client.get(reverse('followup-list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Šiandien')
        self.assertContains(response, 'Vėluoja')
        self.assertContains(response, 'Šią savaitę')
        self.assertContains(response, 'Asta')


class EmailVerificationAndPasswordResetTests(TestCase):
    password = 'Sup3rSecret!pw'

    def register(self, email='new@example.com'):
        return self.client.post(reverse('register'), {
            'email': email,
            'password1': self.password,
            'password2': self.password,
        })

    def verification_token_from_outbox(self):
        match = re.search(r'/verify-email/([0-9a-f-]{36})/', mail.outbox[-1].body)
        return match.group(1)

    def test_register_sends_verification_email_and_shows_banner_until_verified(self):
        response = self.register()
        self.assertRedirects(response, reverse('dashboard'), fetch_redirect_response=False)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].from_email, settings.DEFAULT_FROM_EMAIL)
        self.assertEqual(mail.outbox[0].to, ['new@example.com'])
        self.assertContains(self.client.get(reverse('dashboard')), 'bn-verify-banner')

        user = User.objects.get(email='new@example.com')
        self.assertEqual(user.username, 'new@example.com')

    def test_verification_link_marks_profile_verified_and_hides_banner(self):
        self.register()
        token = self.verification_token_from_outbox()

        response = self.client.get(reverse('verify-email', args=[token]))
        self.assertContains(response, 'El. paštas patvirtintas')
        self.assertTrue(Profile.objects.get(user__email='new@example.com').email_verified)
        self.assertNotContains(self.client.get(reverse('dashboard')), 'bn-verify-banner')

    def test_expired_verification_link_is_rejected(self):
        self.register()
        token = self.verification_token_from_outbox()
        EmailVerification.objects.filter(token=token).update(created_at=timezone.now() - timedelta(days=2))

        self.client.get(reverse('verify-email', args=[token]))
        self.assertFalse(Profile.objects.get(user__email='new@example.com').email_verified)

    def test_resend_sends_new_email_only_while_unverified(self):
        self.register()
        self.client.post(reverse('resend-verification'))
        self.assertEqual(len(mail.outbox), 2)

        token = self.verification_token_from_outbox()
        self.client.get(reverse('verify-email', args=[token]))
        self.client.post(reverse('resend-verification'))
        self.assertEqual(len(mail.outbox), 2)

    def test_password_reset_sends_confirm_link_to_registered_email(self):
        User.objects.create_user(username='reset@example.com', email='reset@example.com', password=self.password)

        response = self.client.post(reverse('password-reset'), {'email': 'reset@example.com'})
        self.assertRedirects(response, reverse('password-reset-done'), fetch_redirect_response=False)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].from_email, settings.DEFAULT_FROM_EMAIL)
        self.assertRegex(mail.outbox[0].body, r'http://testserver/reset/[^/]+/[^/]+/')

    def test_reset_link_lets_user_set_new_password(self):
        user = User.objects.create_user(username='reset@example.com', email='reset@example.com', password=self.password)
        self.client.post(reverse('password-reset'), {'email': 'reset@example.com'})
        link = re.search(r'http://testserver(/reset/[^\s]+/)', mail.outbox[0].body).group(1)

        first = self.client.get(link, follow=True)
        self.assertContains(first, 'Naujas slaptažodis')
        set_password_url = first.redirect_chain[-1][0]

        response = self.client.post(set_password_url, {
            'new_password1': 'An0ther!Secret',
            'new_password2': 'An0ther!Secret',
        })
        self.assertRedirects(response, reverse('password-reset-complete'), fetch_redirect_response=False)
        user.refresh_from_db()
        self.assertTrue(user.check_password('An0ther!Secret'))
