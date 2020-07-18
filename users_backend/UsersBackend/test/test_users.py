"""
Test the User operations
"""
from unittest.mock import ANY
import http.client
from freezegun import freeze_time

from faker import Faker
fake = Faker()


@freeze_time('2019-05-07 13:47:34')
def test_create_user(client):
    new_user = {
        'username': fake.name(),
        'password': fake.password(length=15, special_chars=True),
    }
    response = client.post('/api/signup/', data=new_user)
    result = response.json

    assert http.client.CREATED == response.status_code

    expected = {
        'user_id': ANY,
        'username': new_user['username'],
        'time_created': '2019-05-07T13:47:34',
    }
    assert result == expected


def test_login(client):
    username = fake.name()
    password = fake.password(length=15, special_chars=True)
    new_user = {
        'username': username,
        'password': password,
    }
    response = client.post('/api/signup/', data=new_user)
    assert http.client.CREATED == response.status_code

    response = client.post('/api/login/', data=new_user)
    result = response.json
    assert http.client.OK == response.status_code

    expected = {
        'Authorized': ANY,
    }
    assert result == expected
