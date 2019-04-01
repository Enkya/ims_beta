from flask import request, jsonify, g, url_for
from flask_restplus import abort, Resource, fields, Namespace, marshal_with
from flask_restplus import marshal
from sqlalchemy import desc
from app.models.person import Person
from app.models.address import Address
from app.models.person import Person
from app.models.user import User
from app.utils.utilities import auth
from instance.config import Config


person_api = Namespace(
    'people', description='A person creation namespace')

person_fields = person_api.model(
    'Person',
    {
        'id': fields.Integer(),
        'first_name': fields.String(
            description="Person first name",
            example="John"),
        'last_name': fields.String(
            description="Person last name",
            example="Smith"),
        'full_name': fields.String(
            description="Person Full Name",
            example="John Smith",
        ),
        'date_created': fields.DateTime(
            required=False,
            attribute='date_created'),
    }
)


@person_api.route('', endpoint='person')
class PeopleEndPoint(Resource):

    @person_api.response(200, 'Successful Retrieval of people')
    @person_api.response(200, 'No people found')
    def get(self):
        ''' Retrieve people'''
        search_term = request.args.get('q') or None
        limit = request.args.get('limit') or Config.MAX_PAGE_SIZE
        page_limit = 100 if int(limit) > 100 else int(limit)
        page = request.args.get('page') or 1

        if page_limit < 1 or page < 1:
            return abort(400, 'Page or Limit cannot be negative values')

        person_data = Person.query.filter_by(active=True).\
            order_by(desc(Person.date_created))
        if person_data.all():
            people = person_data

            if search_term:
                people = person_data.filter(
                    Person.last_name.ilike('%'+search_term+'%'),
                    Person.first_name.ilike('%'+search_term+'%')
                )

            person_paged = people.paginate(
                page=page, per_page=page_limit, error_out=True
            )
            results = dict(data=marshal(person_paged.items, person_fields))

            pages = {
                'page': page, 'per_page': page_limit,
                'total_data': person_paged.total, 'pages': person_paged.pages
            }

            if page == 1:
                pages['prev_page'] = url_for('api.person') + \
                    '?limit={}'.format(page_limit)

            if page > 1:
                pages['prev_page'] = url_for('api.person') + \
                    '?limit={}&page={}'.format(page_limit, page-1)

            if page < person_paged.pages:
                pages['next_page'] = url_for('api.person') + \
                    '?limit={}&page={}'.format(page_limit, page+1)

            results.update(pages)
            return results, 200
        return abort(404, message='No people found for specified user')

    @person_api.response(201, 'Person created successfully!')
    @person_api.response(409, 'Person already exists!')
    @person_api.response(500, 'Internal Server Error')
    @person_api.doc(model='Person', body=person_fields)
    def post(self):
        ''' Create a person '''
        arguments = request.get_json(force=True)
        first_name = arguments.get('firstName').strip()
        last_name = arguments.get('lastName').strip()

        if not last_name:
            return abort(400, 'Last Name cannot be empty!')
        try:
            person = Person(
                first_name=first_name,
                last_name=last_name
                )
            if person.save_person():
                return {'message': 'Person created successfully!'}, 201
            return abort(409, message='Person already exists!')
        except Exception as e:
            abort(400, message='Failed to create new person -> {}'.format(e))


@person_api.route('/<int:person_id>', endpoint='single_person')
class SinglePersonEndpoint(Resource):

    @person_api.header('x-access-token', 'Access Token', required=True)
    @marshal_with(person_fields)
    @person_api.response(200, 'Successful retrieval of person')
    @person_api.response(400, 'No person found with specified ID')
    def get(self, person_id):
        ''' Retrieve individual person with given person_id '''
        person = Person.query.filter_by(
            id=person_id, active=True).first()
        if person:
            return person, 200
        abort(404, message='No person found with specified ID')

    @person_api.header('x-access-token', 'Access Token', required=True)
    @person_api.response(200, 'Successfully Updated Person')
    @person_api.response(400, 'Person with id {} not found or not yours.')
    @person_api.marshal_with(person_fields)
    def put(self, person_id):
        ''' Update person with given person_id '''
        arguments = request.get_json(force=True)
        name = arguments.get('name').strip().split(' ')
        person = Person.query.filter_by(
            id=person_id, active=True).first()
        if person:
            if name:
                person.first_name, person.last_name = name[0], name[-1]
            person.save()
            return person, 200
        else:
            abort(
                404,
                message='Person with id {} not found or not yours.'.format(
                    person_id))

    @person_api.header('x-access-token', 'Access Token', required=True)
    @auth.login_required
    @person_api.response(200, 'Person with id {} successfully deleted.')
    @person_api.response(400, 'Person with id {} not found or not yours.')
    def delete(self, person_id):
        ''' Delete person with person_id as given '''
        person = Person.query.filter_by(
            id=person_id, active=True).first()
        if person:
            if person.delete_person():
                response = {
                    'message': 'Person with id {} deleted.'.format(person_id)}
            return response, 200
        else:
            abort(
                404,
                message='Person with id {} not found.'.format(person_id))
