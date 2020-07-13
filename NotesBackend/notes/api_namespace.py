from datetime import datetime
import http.client

# from flask import abort
from flask_restx import Namespace, Resource, fields, reqparse

from notes.db import db
from notes.model import NotesModel


api_namespace = Namespace('api', description='Notes App - Public API')

note_parser = reqparse.RequestParser()
note_parser.add_argument('text', required=True, help='Text for the note object', location='form')

search_parser = reqparse.RequestParser()
search_parser.add_argument('search', help='Search keyword')


model = {
    'id': fields.Integer(),
    'text': fields.String(),
    'time_created': fields.DateTime(),
    'time_modified': fields.DateTime(),
}
note_model = api_namespace.model('Note', model)


@api_namespace.route('/notes/')
class Notes(Resource):

    @api_namespace.doc('List all notes')
    @api_namespace.expect(search_parser)
    @api_namespace.marshal_with(note_model, as_list=True)
    def get(self):
        args = search_parser.parse_args()
        search_key = args.get('search')
        query = NotesModel.query
        if search_key:
            keyword = f'%{search_key}%'
            query = query.filter(NotesModel.text.ilike(keyword))
        notes = query.order_by('id').all()
        return notes

    @api_namespace.doc('Create note')
    @api_namespace.expect(note_parser)
    @api_namespace.marshal_with(note_model, code=http.client.CREATED)
    def post(self):
        args = note_parser.parse_args()
        new_note = NotesModel(text=args['text'],
                              time_created=datetime.utcnow(),
                              time_modified=datetime.utcnow())

        db.session.add(new_note)
        db.session.commit()
        result = api_namespace.marshal(new_note, note_model)

        return result, http.client.CREATED


@api_namespace.route('/notes/<int:note_id>/')
class NotesView(Resource):

    @api_namespace.doc('View a Note')
    @api_namespace.marshal_with(note_model)
    def get(self, note_id):
        note = NotesModel.query.get(note_id)
        if not note:
            return '', http.client.NOT_FOUND
        return note

    @api_namespace.doc('Update a existing Note')
    @api_namespace.expect(note_parser)
    @api_namespace.marshal_with(note_model)
    def put(self, note_id):
        args = note_parser.parse_args()
        note_to_update = NotesModel.query.filter_by(id=note_id).first()
        if not note_to_update:
            return '', http.client.NOT_FOUND

        note_to_update.text = args['text']
        note_to_update.time_modified = datetime.utcnow()

        db.session.commit()
        result = api_namespace.marshal(note_to_update, note_model)

        return result

    @api_namespace.doc('Delete a particular Note',
                       responses={http.client.NO_CONTENT: 'No content'})
    def delete(self, note_id):
        note = NotesModel.query.get(note_id)
        if not note:
            return '', http.client.NO_CONTENT
        db.session.delete(note)
        db.session.commit()

        return '', http.client.NO_CONTENT
