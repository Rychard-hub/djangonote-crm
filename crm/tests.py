from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import get_organization
from crm.models import Activity, Comment, Lead, Task


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
        self.assertContains(response, 'Šiandienos follow-up')
        self.assertContains(response, 'Nauji leadai')
        self.assertContains(response, "Artimiausi follow-up'ai")
        self.assertContains(response, 'Vėluojantys kontaktai')


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
        self.assertContains(response, 'Komunikacijos istorija')

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
