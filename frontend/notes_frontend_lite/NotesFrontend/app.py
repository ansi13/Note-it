import http
import os

from flask import Flask, session, render_template, request, redirect,\
    url_for, make_response
from flask_cors import CORS

import requests

from NotesFrontend import config
from NotesFrontend import token_validation


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
CORS(app)

USER_BACKEND = os.environ['USER_BACKEND_URL']
NOTES_BACKEND = os.environ['NOTES_BACKEND_URL']


def get_username_from_session(session):
    cookie_session = session.get('Authorized')
    username = token_validation.validate_token_header(cookie_session,
                                                      config.PUBLIC_KEY)
    if not username:
        return None
    return username


@app.route("/", methods=['GET', 'POST'])
def index():
    username = get_username_from_session(session)
    if username:
        return redirect(url_for('home_page'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    no_log = False
    if request.method == 'POST':
        req = request.form
        username = req.get('lusername', '')
        password = req.get('password', '')
        login_url = USER_BACKEND + '/api/login/'
        data = {
            'username': username,
            'password': password,
        }
        result = requests.post(login_url, data)
        if result.status_code == http.client.OK:
            session['Authorized'] = result.json()['Authorized']
            return redirect(url_for('home_page'))
        no_log = True

    return render_template('login.html', no_log=no_log)


@app.route('/logout')
def logout():
    # Delete session cookie
    session.pop('Authorized', None)
    response = redirect(url_for('index'))
    return response


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    no_password_match = False
    if request.method == 'POST':
        req = request.form
        username = req.get('susername', '')
        password = req.get('password', '')
        cpassword = req.get('cpassword', '')
        if password != cpassword:
            no_password_match = True
            return render_template('signup.html',
                                   no_password_match=no_password_match,
                                   susername=username,
                                   password=password,
                                   cpassword=cpassword)
        signup_url = USER_BACKEND + '/api/signup/'
        data = {
            'username': username,
            'password': password,
        }
        result = requests.post(signup_url, data)
        if result.status_code == http.client.CREATED:
            return redirect(url_for('login'))

    return render_template('signup.html', no_password_match=no_password_match)


@app.route('/home', methods=['GET', 'POST'])
def home_page():

    username = get_username_from_session(session)
    if not username:
        return redirect(url_for('login'))

    url = NOTES_BACKEND + '/api/me/notes/'
    headers = {
        'Authorization': session.get('Authorized'),
    }
    result = requests.get(url, headers=headers)
    if result.status_code != http.client.OK:
        return redirect('login')

    return render_template('list_thoughts.html', notes=result.json(), username=username)


@app.route('/search', methods=['GET', 'POST'])
def search_notes():
    username = get_username_from_session(session)
    if not username:
        return redirect(url_for('login'))

    search_query = request.args.get('search', '')
    if search_query:
        url = NOTES_BACKEND + f'/api/me/notes/?search={search_query}'
        headers = {
            'Authorization': session.get('Authorized'),
        }
        result = requests.get(url, headers=headers)
        if result.status_code != http.client.OK:
            return redirect('login')

        return render_template('list_thoughts.html', search_query=search_query, notes=result.json(), username=username)

    return redirect(url_for('home_page'))


@app.route('/new', methods=['GET', 'POST'])
def new_note():
    username = get_username_from_session(session)
    if not username:
        return redirect(url_for('login'))

    if request.method == 'POST':
        req = request.form
        title = req.get('title', 'New Note')
        text = req.get('text', '')
        if text or title:
            url = NOTES_BACKEND + f'/api/me/notes/'
            data = {
                'title': title,
                'text': text,
            }
            headers = {
                'Authorization': session.get('Authorized'),
            }
            result = requests.post(url, headers=headers, data=data)
            if result.status_code != http.client.CREATED:
                return redirect(url_for('login'))
        return redirect(url_for('home_page'))

    return render_template('new_note.html', username=username)


@app.route('/edit/<note_id>', methods=['GET', 'POST'])
def edit_note(note_id):
    username = get_username_from_session(session)
    if not username:
        return redirect(url_for('login'))

    if request.method == 'GET':
        url = NOTES_BACKEND + f'/api/me/notes/{note_id}/'
        headers = {
            'Authorization': session.get('Authorized'),
        }
        result = requests.get(url, headers=headers)
        if result.status_code != http.client.OK:
            return redirect(url_for('login'))

        note_to_edit = result.json()
        return render_template('edit_note.html',
                               text=note_to_edit['text'],
                               username=username,
                               title=note_to_edit['title'],
                               note_id=note_to_edit['id'])

    if request.method == 'POST':
        req = request.form
        title = req.get('title', 'New Note')
        text = req.get('text', '')
        if text or title:
            url = NOTES_BACKEND + f'/api/me/notes/{note_id}/'
            data = {
                'title': title,
                'text': text,
            }
            headers = {
                'Authorization': session.get('Authorized'),
            }
            result = requests.post(url, headers=headers, data=data)
            if result.status_code != http.client.OK:
                return redirect(url_for('login'))
        return redirect(url_for('home_page'))


@app.route('/delete/<note_id>', methods=['GET'])
def delete_note(note_id):
    username = get_username_from_session(session)
    if not username:
        return redirect(url_for('login'))

    if request.method == 'GET':
        url = NOTES_BACKEND + f'/api/me/notes/{note_id}/'
        headers = {
            'Authorization': session.get('Authorized'),
        }
        result = requests.delete(url, headers=headers)
        if result.status_code != http.client.NO_CONTENT:
            return redirect(url_for('login'))

        return redirect(url_for('home_page'))
    return redirect(url_for('home_page'))


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response
