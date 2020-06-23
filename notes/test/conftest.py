import pytest
import http.client
from notes.app import create_app
from faker import Faker

fake = Faker()


@pytest.fixture
def app():
    application = create_app()
    return application


@pytest.fixture
def notes_fixture(client):
    note_ids = []
    for _ in range(3):
        note = {
            'text': fake.text(230)
        }
        response = client.post('/api/notes/', data=note)
        assert response.status_code == http.client.CREATED
        result = response.json
        note_ids.append(result['id'])
    yield note_ids

    response = client.get('/api/notes/')
    notes = response.json
    for note in notes:
        note_id = note['id']
        url = f'/api/notes/{note_id}/'
        response = client.delete(url)
        assert response.status_code == http.client.NO_CONTENT
