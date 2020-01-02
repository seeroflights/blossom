import json

from django_hosts.resolvers import reverse

from blossom.authentication.models import BlossomUser
from blossom.models import Submission, Transcription
from blossom.tests.helpers import (
    create_test_user, create_staff_volunteer_with_keys, create_test_submission
)

class TestTranscriptionCreation():
    def test_transcription_create(self, client):
        client, headers = create_staff_volunteer_with_keys(client)
        s = create_test_submission()
        v = BlossomUser.objects.first()
        data = {
            "submission_id": s.submission_id,
            "v_id": v.id,
            "t_id": 'ABC',
            "completion_method": "automated tests",
            "t_url": "https://example.com",
            "t_text": "test content",
        }
        assert Transcription.objects.count() == 0
        result = client.post(
            reverse('transcription-list', host='api'),
            json.dumps(data),
            HTTP_HOST='api',
            content_type='application/json',
            **headers,
        )
        assert result.status_code == 200
        assert result.json().get('success') == \
               'Transcription ID 1 created on post AAA, written by janeeyre'

        obj = Transcription.objects.get(id=1)
        assert obj.submission == s
        assert obj.completion_method == "automated tests"
        assert obj.author == v
        assert obj.transcription_id == 'ABC'
        assert obj.url == "https://example.com"
        assert obj.text == "test content"

    def test_transcription_create_alt_submission_id(self, client):
        client, headers = create_staff_volunteer_with_keys(client)
        s = create_test_submission()
        v = BlossomUser.objects.first()
        data = {
            "submission_id": s.id,
            "v_id": v.id,
            "t_id": 'ABC',
            "completion_method": "automated tests",
            "t_url": "https://example.com",
            "t_text": "test content",
        }
        result = client.post(
            reverse('transcription-list', host='api'),
            json.dumps(data),
            HTTP_HOST='api',
            content_type='application/json',
            **headers,
        )
        assert result.status_code == 200
        assert result.json().get('success') == \
               'Transcription ID 1 created on post AAA, written by janeeyre'

    def test_transcription_no_submission_id(self, client):
        client, headers = create_staff_volunteer_with_keys(client)
        create_test_submission()
        v = BlossomUser.objects.first()
        data = {
            "v_id": v.id,
            "t_id": 'ABC',
            "completion_method": "automated tests",
            "t_url": "https://example.com",
            "t_text": "test content",
        }
        result = client.post(
            reverse('transcription-list', host='api'),
            json.dumps(data),
            HTTP_HOST='api',
            content_type='application/json',
            **headers,
        )
        assert result.status_code == 400
        assert result.json().get('error') == (
            "Missing JSON body key `submission_id`, str; the ID of the post"
            " the transcription is on."
        )

    def test_transcription_with_invalid_submission_id(self, client):
        client, headers = create_staff_volunteer_with_keys(client)
        create_test_submission()
        v = BlossomUser.objects.first()
        data = {
            "submission_id": 999,
            "v_id": v.id,
            "t_id": 'ABC',
            "completion_method": "automated tests",
            "t_url": "https://example.com",
            "t_text": "test content",
        }
        result = client.post(
            reverse('transcription-list', host='api'),
            json.dumps(data),
            HTTP_HOST='api',
            content_type='application/json',
            **headers,
        )
        assert result.status_code == 404
        assert result.json().get('error') == "No post found with ID 999!"

    def test_transcription_with_invalid_volunteer_id(self, client):
        client, headers = create_staff_volunteer_with_keys(client)
        s = create_test_submission()
        data = {
            "submission_id": s.submission_id,
            "v_id": 999,
            "t_id": 'ABC',
            "completion_method": "automated tests",
            "t_url": "https://example.com",
            "t_text": "test content",
        }
        result = client.post(
            reverse('transcription-list', host='api'),
            json.dumps(data),
            HTTP_HOST='api',
            content_type='application/json',
            **headers,
        )
        assert result.status_code == 404
        assert result.json().get('error') == "No volunteer found with that ID / username."

    def test_transcription_with_missing_transcription_id(self, client):
        client, headers = create_staff_volunteer_with_keys(client)
        s = create_test_submission()
        v = BlossomUser.objects.first()
        data = {
            "submission_id": s.submission_id,
            "v_id": v.id,
            "completion_method": "automated tests",
            "t_url": "https://example.com",
            "t_text": "test content",
        }
        result = client.post(
            reverse('transcription-list', host='api'),
            json.dumps(data),
            HTTP_HOST='api',
            content_type='application/json',
            **headers,
        )
        assert result.status_code == 400
        assert result.json().get('error') == \
               "Missing JSON body key `t_id`, str; the ID of the transcription."

    def test_transcription_with_missing_completion_method(self, client):
        client, headers = create_staff_volunteer_with_keys(client)
        s = create_test_submission()
        v = BlossomUser.objects.first()
        data = {
            "submission_id": s.submission_id,
            "v_id": v.id,
            "t_id": 'ABC',
            "t_url": "https://example.com",
            "t_text": "test content",
        }
        result = client.post(
            reverse('transcription-list', host='api'),
            json.dumps(data),
            HTTP_HOST='api',
            content_type='application/json',
            **headers,
        )
        assert result.status_code == 400
        assert result.json().get('error') == (
            "Missing JSON body key `completion_method`, str; the service this"
            " transcription was completed through. `app`, `ToR`, etc. 20char max."
        )

    def test_transcription_with_missing_transcription_url(self, client):
        client, headers = create_staff_volunteer_with_keys(client)
        s = create_test_submission()
        v = BlossomUser.objects.first()
        data = {
            "submission_id": s.submission_id,
            "v_id": v.id,
            "t_id": 'ABC',
            "completion_method": "automated tests",
            "t_text": "test content",
        }
        result = client.post(
            reverse('transcription-list', host='api'),
            json.dumps(data),
            HTTP_HOST='api',
            content_type='application/json',
            **headers,
        )
        assert result.status_code == 400
        assert result.json().get('error') == (
            "Missing JSON body key `t_url`, str; the direct URL for the"
            " transcription. Use string `None` if no URL is available."
        )

    def test_transcription_with_missing_transcription_text(self, client):
        client, headers = create_staff_volunteer_with_keys(client)
        s = create_test_submission()
        v = BlossomUser.objects.first()
        data = {
            "submission_id": s.submission_id,
            "v_id": v.id,
            "t_id": 'ABC',
            "completion_method": "automated tests",
            "t_url": "https://example.com",
        }
        result = client.post(
            reverse('transcription-list', host='api'),
            json.dumps(data),
            HTTP_HOST='api',
            content_type='application/json',
            **headers,
        )
        assert result.status_code == 400
        assert result.json().get('error') == (
            "Missing JSON body key `t_text`, str; the content of the transcription."
        )
