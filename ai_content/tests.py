from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from accounts.models import get_organization
from ai_content.models import ContentJob
from ai_content.services import (
    GenerationFailed,
    ImageProviderNotConfigured,
    generate_image_bytes,
    generate_video_bytes,
)
from ai_content.tasks import run_content_job


def _response(status_code, content=b'', json_data=None, text=''):
    response = MagicMock()
    response.status_code = status_code
    response.content = content
    response.text = text
    if json_data is not None:
        response.json.return_value = json_data
    return response


@override_settings(STABILITY_API_KEY='test-key')
class GenerateImageBytesTests(TestCase):
    def test_success_returns_bytes_and_content_type(self):
        with patch('ai_content.services.requests.post', return_value=_response(200, content=b'PNGDATA')) as mocked_post:
            content, content_type = generate_image_bytes('a red bicycle')

        self.assertEqual(content, b'PNGDATA')
        self.assertEqual(content_type, 'image/png')
        mocked_post.assert_called_once()

    def test_non_200_raises_generation_failed(self):
        with patch('ai_content.services.requests.post', return_value=_response(402, text='insufficient credits')):
            with self.assertRaises(GenerationFailed):
                generate_image_bytes('a red bicycle')

    @override_settings(STABILITY_API_KEY='')
    def test_missing_api_key_raises_not_configured(self):
        with self.assertRaises(ImageProviderNotConfigured):
            generate_image_bytes('a red bicycle')


@override_settings(STABILITY_API_KEY='test-key')
class GenerateVideoBytesTests(TestCase):
    def test_success_after_polling(self):
        post_responses = [
            _response(200, content=b'PNGDATA'),  # keyframe image
            _response(200, json_data={'id': 'gen-123'}),  # image-to-video start
        ]
        get_responses = [
            _response(202),  # still processing
            _response(200, content=b'MP4DATA'),  # done
        ]
        with patch('ai_content.services.requests.post', side_effect=post_responses), \
             patch('ai_content.services.requests.get', side_effect=get_responses), \
             patch('ai_content.services.time.sleep') as mocked_sleep:
            content, content_type = generate_video_bytes('a bicycle rolling down a hill')

        self.assertEqual(content, b'MP4DATA')
        self.assertEqual(content_type, 'video/mp4')
        mocked_sleep.assert_called_once()

    def test_failed_start_raises_generation_failed(self):
        with patch('ai_content.services.requests.post', side_effect=[
            _response(200, content=b'PNGDATA'),
            _response(500, text='server error'),
        ]):
            with self.assertRaises(GenerationFailed):
                generate_video_bytes('a bicycle rolling down a hill')


class RunContentJobMediaTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester@example.com', password='StrongPass123!')
        self.organization = get_organization(self.user)

    @override_settings(STABILITY_API_KEY='test-key')
    def test_image_job_saves_result_file_and_marks_done(self):
        job = ContentJob.objects.create(
            organization=self.organization, created_by=self.user, kind='image', prompt='a red bicycle',
        )
        with patch('ai_content.tasks.generate_image_bytes', return_value=(b'PNGDATA', 'image/png')):
            run_content_job(job.pk)

        job.refresh_from_db()
        self.assertEqual(job.status, 'done')
        self.assertTrue(job.result_file.name.endswith('.png'))
        job.result_file.delete(save=False)

    @override_settings(STABILITY_API_KEY='test-key')
    def test_video_job_saves_result_file_and_marks_done(self):
        job = ContentJob.objects.create(
            organization=self.organization, created_by=self.user, kind='video', prompt='a rolling bicycle',
        )
        with patch('ai_content.tasks.generate_video_bytes', return_value=(b'MP4DATA', 'video/mp4')):
            run_content_job(job.pk)

        job.refresh_from_db()
        self.assertEqual(job.status, 'done')
        self.assertTrue(job.result_file.name.endswith('.mp4'))
        job.result_file.delete(save=False)

    @override_settings(STABILITY_API_KEY='')
    def test_image_job_without_api_key_marks_failed_gracefully(self):
        job = ContentJob.objects.create(
            organization=self.organization, created_by=self.user, kind='image', prompt='a red bicycle',
        )
        run_content_job(job.pk)

        job.refresh_from_db()
        self.assertEqual(job.status, 'failed')
        self.assertIn('STABILITY_API_KEY', job.error)

    @override_settings(STABILITY_API_KEY='test-key')
    def test_image_job_generation_failure_marks_failed_gracefully(self):
        job = ContentJob.objects.create(
            organization=self.organization, created_by=self.user, kind='image', prompt='a red bicycle',
        )
        with patch('ai_content.tasks.generate_image_bytes', side_effect=GenerationFailed('boom')):
            run_content_job(job.pk)

        job.refresh_from_db()
        self.assertEqual(job.status, 'failed')
        self.assertEqual(job.error, 'boom')
