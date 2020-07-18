from collections import defaultdict
import pytest
import http.client

from faker import Faker

from .constants import PRIVATE_KEY
from notes.app import create_app
from notes import token_validation

fake = Faker()


@pytest.fixture
def app():
    application = create_app()
    return application


@pytest.fixture
def notes_fixture(client):
    note_ids = []
    header = token_validation.generate_token_header(fake.name(),
                                                    PRIVATE_KEY)
    headers = {
        'Authorization': header,
    }

    for _ in range(3):
        note = {
            'text': fake.text(230)
        }
        response = client.post('/api/me/notes/', data=note,
                               headers=headers)

        assert response.status_code == http.client.CREATED
        result = response.json
        note_ids.append(result['id'])
    yield note_ids, headers

    response = client.get('/api/me/notes/', headers=headers)
    notes = response.json
    for note in notes:
        note_id = note['id']
        url = f'/api/me/notes/{note_id}/'
        response = client.delete(url, headers=headers)
        assert response.status_code == http.client.NO_CONTENT


@pytest.fixture
def notes_random_fixture(client):
    note_ids = []
    headers_dict = defaultdict(str)
    for _ in range(3):
        note = {
            'text': fake.text(230)
        }
        header = token_validation.generate_token_header(fake.name(),
                                                        PRIVATE_KEY)
        headers = {
            'Authorization': header,
        }
        response = client.post('/api/me/notes/', data=note,
                               headers=headers)

        assert response.status_code == http.client.CREATED
        result = response.json
        note_ids.append(result['id'])
        headers_dict[result['id']] = header
    yield note_ids

    for note_id in note_ids:
        header = headers_dict[note_id]
        url = f'/api/me/notes/{note_id}/'
        response = client.delete(url, headers={'Authorization': header, })
        assert response.status_code == http.client.NO_CONTENT
