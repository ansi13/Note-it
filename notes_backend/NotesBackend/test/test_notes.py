from unittest.mock import ANY
import http.client

from freezegun import freeze_time
from faker import Faker

from .constants import PRIVATE_KEY, PUBLIC_KEY
from notes import token_validation

fake = Faker()


@freeze_time("2019-05-07 13:47:34")
def test_create_note(client):
    new_note = {
        "title": fake.text(50),
        "text": fake.text(240),
    }
    header = token_validation.generate_token_header(fake.name(), PRIVATE_KEY)
    headers = {
        "Authorization": header,
    }
    response = client.post("/api/me/notes/", data=new_note, headers=headers)
    result = response.json
    assert response.status_code == http.client.CREATED

    expected = {
        "id": ANY,
        "username": ANY,
        "title": new_note["title"],
        "text": new_note["text"],
        "time_created": "2019-05-07T13:47:34",
        "time_modified": "2019-05-07T13:47:34",
    }
    assert result == expected


def test_create_note_unauthorized(client):
    new_note = {
        "title": fake.text(50),
        "text": fake.text(240),
    }
    response = client.post("/api/me/notes/", data=new_note)
    assert http.client.UNAUTHORIZED == response.status_code


def test_list_all_notes(client, notes_fixture):
    note_ids, headers = notes_fixture
    username = token_validation.validate_token_header(
        headers["Authorization"], PUBLIC_KEY
    )

    response = client.get("/api/me/notes/", headers=headers)
    result = response.json

    assert response.status_code == http.client.OK
    assert len(result) == len(note_ids)

    for note in result:
        expected = {
            "username": username,
            "title": ANY,
            "text": ANY,
            "id": ANY,
            "time_created": ANY,
            "time_modified": ANY,
        }
        assert expected == note


def test_search_notes(client):
    username = fake.name()
    new_note = {
        "title": fake.text(50),
        "text": "dummy text for search test",
    }
    header = token_validation.generate_token_header(username, PRIVATE_KEY)
    headers = {
        "Authorization": header,
    }
    response = client.post("/api/me/notes/", data=new_note, headers=headers)
    assert response.status_code == http.client.CREATED
    response = client.get("/api/me/notes/?search=dummy", headers=headers)

    assert response.status_code == http.client.OK
    result = response.json

    assert len(result) > 0
    for note in result:
        expected = {
            "title": ANY,
            "text": ANY,
            "username": username,
            "id": ANY,
            "time_created": ANY,
            "time_modified": ANY,
        }
        assert expected == note
        assert "dummy" in note["text"].lower()


def test_view_note(client, notes_fixture):
    note_ids, headers = notes_fixture
    username = token_validation.validate_token_header(
        headers["Authorization"], PUBLIC_KEY
    )
    response = client.get(f"/api/me/notes/{note_ids[0]}/", headers=headers)
    result = response.json

    assert http.client.OK == response.status_code
    assert result["username"] == username
    assert "text" in result
    assert "title" in result
    assert "time_modified" in result
    assert "time_created" in result
    assert result["id"] == note_ids[0]


def test_view_note_existing_unauthorized(client, notes_random_fixture):
    note_ids = notes_random_fixture
    header = token_validation.generate_token_header("dummy user", PRIVATE_KEY)
    headers = {
        "Authorization": header,
    }
    response = client.get(f"/api/me/notes/{note_ids[0]}/", headers=headers)

    assert http.client.NOT_FOUND == response.status_code


def test_update_note(client, notes_fixture):
    note_ids, headers = notes_fixture
    text = {"title": fake.text(50), "text": fake.text(250)}

    response = client.post(
        f"/api/me/notes/{note_ids[1]}/", data=text, headers=headers
    )
    old_result = response.json
    assert http.client.OK == response.status_code

    new_response = client.get(f"/api/me/notes/{note_ids[1]}/", headers=headers)
    new_result = new_response.json
    assert old_result == new_result


def test_update_note_existing_unauthorized(client, notes_random_fixture):
    note_ids = notes_random_fixture
    text = {"text": fake.text(250)}
    header = token_validation.generate_token_header("dummy user", PRIVATE_KEY)
    headers = {
        "Authorization": header,
    }

    response = client.post(
        f"/api/me/notes/{note_ids[1]}/", data=text, headers=headers
    )
    old_result = response.json
    assert (
        http.client.NOT_FOUND == response.status_code
        or http.client.UNAUTHORIZED == response.status_code
    )

    new_response = client.get(f"/api/me/notes/{note_ids[1]}/", headers=headers)
    new_result = new_response.json
    assert old_result == new_result


def test_get_non_existent_note(client):
    note_id = 32423
    header = token_validation.generate_token_header(fake.name(), PRIVATE_KEY)
    headers = {
        "Authorization": header,
    }
    response = client.get(f"/api/me/notes/{note_id}/", headers=headers)

    assert response.status_code == http.client.NOT_FOUND
