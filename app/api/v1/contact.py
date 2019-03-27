from flask import request, jsonify, g, url_for
from flask_restplus import abort, Resource, fields, Namespace, marshal_with
from flask_restplus import marshal
from sqlalchemy import desc
from app.models.contact import Contact
from app.utils.utilities import auth
from instance.config import Config


contact_api = Namespace(
    'contacts', description='A contact creation namespace')

contact_fields = contact_api.model(
    'Contact',
    {
        'id': fields.Integer(),
        'email': fields.String(
            required=False,
            description="Email contact",
            example="test@test.com"),
        'social_media': fields.String(
            required=False,
            attribute='social_media_handle'),
        'website': fields.String(required=False, attribute='website'),
        'tel_one': fields.String(
            required=False, attribute='tel_one'),
        'tel_two': fields.String(
            required=False, attribute='tel_two'),
        'date_created': fields.DateTime(
            required=False, attribute='date_created'),
        'date_modified': fields.DateTime(
            required=False, attribute='date_modified'),
    }
)


@contact_api.route('', endpoint='contact')
class ContactsEndPoint(Resource):

    @contact_api.response(200, 'Successful Retrieval of contacts')
    @contact_api.response(200, 'No contacts found')
    def get(self):
        ''' Retrieve contacts'''
        search_term = request.args.get('q') or None
        limit = request.args.get('limit') or Config.MAX_PAGE_SIZE
        page_limit = 100 if int(limit) > 100 else int(limit)
        page = request.args.get('page') or 1

        if page_limit < 1 or page < 1:
            return abort(400, 'Page or Limit cannot be negative values')

        contact_data = Contact.query.filter_by(active=True).\
            order_by(desc(Contact.date_created))
        if contact_data.all():
            contacts = contact_data

            if search_term:
                contacts = contact_data.filter(
                    Contact.email.ilike('%'+search_term+'%')
                )

            contact_paged = contacts.paginate(
                page=page, per_page=page_limit, error_out=True
            )
            results = dict(data=marshal(contact_paged.items, contact_fields))

            pages = {
                'page': page, 'per_page': page_limit,
                'total_data': contact_paged.total, 'pages': contact_paged.pages
            }

            if page == 1:
                pages['prev_page'] = url_for(
                    'api.contact')+'?limit={}'.format(page_limit)

            if page > 1:
                pages['prev_page'] = url_for('api.contact') + \
                    '?limit={}&page={}'.format(page_limit, page-1)

            if page < contact_paged.pages:
                pages['next_page'] = url_for('api.contact') + \
                    '?limit={}&page={}'.format(page_limit, page+1)

            results.update(pages)
            return results, 200
        return abort(404, message='No contacts found for specified user')

    @contact_api.response(201, 'Contact created successfully!')
    @contact_api.response(409, 'Contact already exists!')
    @contact_api.response(500, 'Internal Server Error')
    @contact_api.doc(model='Contact', body=contact_fields)
    def post(self):
        ''' Create an contact '''
        arguments = request.get_json(force=True)
        district = arguments.get('district').strip()
        postal = arguments.get('postal').strip() or ''
        country = arguments.get('country').strip() or ''
        contact_line_1 = arguments.get('contact1').strip() or ''
        contact_line_2 = arguments.get('contact1').strip() or ''

        if not contact_line_1:
            return abort(400, 'Contact cannot be empty!')
        try:
            contact = Contact(
                district=district,
                postal_code=postal,
                country=country,
                contact_line_1=contact_line_1,
                contact_line_2=contact_line_2
                )
            if contact.save_contact():
                return {'message': 'Contact created successfully!'}, 201
            return abort(409, message='Contact already exists!')
        except Exception as e:
            abort(400, message='Failed to create new contact -> {}'.format(e))


@contact_api.route('/<int:contact_id>', endpoint='single_contact')
class SingleContactEndpoint(Resource):

    @contact_api.header('x-access-token', 'Access Token', required=True)
    @marshal_with(contact_fields)
    @contact_api.response(200, 'Successful retrieval of contact')
    @contact_api.response(400, 'No contact found with specified ID')
    def get(self, contact_id):
        ''' Retrieve individual contact with given contact_id '''
        contact = Contact.query.filter_by(
            id=contact_id, active=True).first()
        if contact:
            return contact, 200
        abort(404, message='No contact found with specified ID')

    @contact_api.header('x-access-token', 'Access Token', required=True)
    @contact_api.response(200, 'Successfully Updated Contact')
    @contact_api.response(400, 'Contact with id {} not found or not yours.')
    @contact_api.marshal_with(contact_fields)
    def put(self, contact_id):
        ''' Update contact with given contact_id '''
        arguments = request.get_json(force=True)
        contact_line_1 = arguments.get('contact1').strip()
        contact = Contact.query.filter_by(
            id=contact_id, active=True).first()
        if contact:
            if contact_line_1:
                contact.contact_line_1 = contact_line_1
            contact.save()
            return contact, 200
        else:
            abort(
                404,
                message='Contact with id {} not found'.format(contact_id)
            )

    @contact_api.header('x-access-token', 'Access Token', required=True)
    @auth.login_required
    @contact_api.response(200, 'Contact with id {} successfully deleted.')
    @contact_api.response(400, 'Contact with id {} not found or not yours.')
    def delete(self, contact_id):
        ''' Delete contact with contact_id as given '''
        contact = Contact.query.filter_by(
            id=contact_id, active=True).first()
        if contact:
            if contact.delete_contact():
                response = {
                    'message': 'Contact with id {} deleted.'.format(contact_id)
                }
            return response, 200
        else:
            abort(
                404,
                message='Contact with id {} not found.'.format(contact_id)
            )
