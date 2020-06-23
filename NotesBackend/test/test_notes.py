from unittest.mock import ANY
import http.client
from freezegun import freeze_time
from faker import Faker

fake = Faker()


@freeze_time('2019-05-07 13:47:34')
def test_create_thought(client):
    new_note = {
        'text': fake.text(240),
    }
    response = client.post('/api/notes/', data=new_note)
    result = response.json
    assert response.status_code == http.client.CREATED

    expected = {
        'id': ANY,
        'text': new_note['text'],
        'time_created': '2019-05-07T13:47:34',
        'time_modified': '2019-05-07T13:47:34',
    }
    assert result == expected


def test_list_all_notes(client):
    response = client.get('/api/notes/')
    result = response.json

    assert response.status_code == http.client.OK
    assert len(result) > 0

    # Check that the ids are increasing
    previous_id = -1
    for note in result:
        expected = {
            'text': ANY,
            'id': ANY,
            'time_created': ANY,
            'time_modified': ANY,
        }
        assert expected == note
        assert note['id'] > previous_id
        previous_id = note['id']


def test_view_note(client, notes_fixture):
    note_id = notes_fixture[0]
    response = client.get(f'/api/notes/{note_id}/')
    result = response.json

    assert http.client.OK == response.status_code
    assert 'text' in result
    assert 'time_modified' in result
    assert 'time_created' in result
    assert 'id' in result


def test_update_note(client, notes_fixture):
    note_id = notes_fixture[1]
    text = {
        'text': fake.text(250)
    }

    response = client.put(f'/api/notes/{note_id}/', data=text)
    old_result = response.json
    assert http.client.OK == response.status_code

    new_response = client.get(f'/api/notes/{note_id}/')
    new_result = new_response.json
    assert old_result == new_result


def test_get_non_existent_note(client):
    note_id = 32423
    response = client.get(f'/api/notes/{note_id}/')

    assert response.status_code == http.client.NOT_FOUND
