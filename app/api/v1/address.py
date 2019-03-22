from flask import request, jsonify, g, url_for
from flask_restplus import abort, Resource, fields, Namespace, marshal_with
from flask_restplus import marshal
from sqlalchemy import desc
from app.models.address import Address
from app.utils.utilities import auth
from instance.config import Config


address_api = Namespace(
    'addresses', description='An address creation namespace')

address_fields = address_api.model(
    'Address',
    {
        'id': fields.Integer(),
        'district': fields.String(
            required=False,
            description="District name",
            example="Wakiso"),
        'postal_code': fields.String(required=False, attribute='postal_code'),
        'country': fields.String(required=False, attribute='country'),
        'address_line_1': fields.String(
            required=False, attribute='address_line_1'),
        'address_line_2': fields.String(
            required=False, attribute='address_line_2'),
        'date_created': fields.DateTime(
            required=False, attribute='date_created'),
        'date_modified': fields.DateTime(
            required=False, attribute='date_modified'),
    }
)


@address_api.route('', endpoint='address')
class AddressesEndPoint(Resource):

    @address_api.response(200, 'Successful Retrieval of addresses')
    @address_api.response(200, 'No addresses found')
    def get(self):
        ''' Retrieve addresses'''
        search_term = request.args.get('q') or None
        limit = request.args.get('limit') or Config.MAX_PAGE_SIZE
        page_limit = 100 if int(limit) > 100 else int(limit)
        page = request.args.get('page') or 1

        if page_limit < 1 or page < 1:
            return abort(400, 'Page or Limit cannot be negative values')

        address_data = Address.query.filter_by(active=True).\
            order_by(desc(Address.date_created))
        if address_data.all():
            addresses = address_data

            if search_term:
                addresses = address_data.filter(
                    Address.address_line_1.ilike('%'+search_term+'%')
                )

            address_paged = addresses.paginate(
                page=page, per_page=page_limit, error_out=True
            )
            results = dict(data=marshal(address_paged.items, address_fields))

            pages = {
                'page': page, 'per_page': page_limit,
                'total_data': address_paged.total, 'pages': address_paged.pages
            }

            if page == 1:
                pages['prev_page'] = url_for(
                    'api.address')+'?limit={}'.format(page_limit)

            if page > 1:
                pages['prev_page'] = url_for('api.address') + \
                    '?limit={}&page={}'.format(page_limit, page-1)

            if page < address_paged.pages:
                pages['next_page'] = url_for('api.address') + \
                    '?limit={}&page={}'.format(page_limit, page+1)

            results.update(pages)
            return results, 200
        return abort(404, message='No addresses found for specified user')

    @address_api.response(201, 'Address created successfully!')
    @address_api.response(409, 'Address already exists!')
    @address_api.response(500, 'Internal Server Error')
    @address_api.doc(model='Address', body=address_fields)
    def post(self):
        ''' Create an address '''
        arguments = request.get_json(force=True)
        district = arguments.get('district').strip()
        postal = arguments.get('postal').strip() or ''
        country = arguments.get('country').strip() or ''
        address_line_1 = arguments.get('address1').strip() or ''
        address_line_2 = arguments.get('address1').strip() or ''

        if not address_line_1:
            return abort(400, 'Address cannot be empty!')
        try:
            address = Address(
                district=district,
                postal_code=postal,
                country=country,
                address_line_1=address_line_1,
                address_line_2=address_line_2
                )
            if address.save_address():
                return {'message': 'Address created successfully!'}, 201
            return abort(409, message='Address already exists!')
        except Exception as e:
            abort(400, message='Failed to create new address -> {}'.format(e))


@address_api.route('/<int:address_id>', endpoint='single_address')
class SingleAddressEndpoint(Resource):

    @address_api.header('x-access-token', 'Access Token', required=True)
    @marshal_with(address_fields)
    @address_api.response(200, 'Successful retrieval of address')
    @address_api.response(400, 'No address found with specified ID')
    def get(self, address_id):
        ''' Retrieve individual address with given address_id '''
        address = Address.query.filter_by(
            id=address_id, active=True).first()
        if address:
            return address, 200
        abort(404, message='No address found with specified ID')

    @address_api.header('x-access-token', 'Access Token', required=True)
    @address_api.response(200, 'Successfully Updated Address')
    @address_api.response(400, 'Address with id {} not found or not yours.')
    @address_api.marshal_with(address_fields)
    def put(self, address_id):
        ''' Update address with given address_id '''
        arguments = request.get_json(force=True)
        address_line_1 = arguments.get('address1').strip()
        address = Address.query.filter_by(
            id=address_id, active=True).first()
        if address:
            if address_line_1:
                address.address_line_1 = address_line_1
            address.save()
            return address, 200
        else:
            abort(
                404,
                message='Address with id {} not found'.format(address_id)
            )

    @address_api.header('x-access-token', 'Access Token', required=True)
    @auth.login_required
    @address_api.response(200, 'Address with id {} successfully deleted.')
    @address_api.response(400, 'Address with id {} not found or not yours.')
    def delete(self, address_id):
        ''' Delete address with address_id as given '''
        address = Address.query.filter_by(
            id=address_id, active=True).first()
        if address:
            if address.delete_address():
                response = {
                    'message': 'Address with id {} deleted.'.format(address_id)
                }
            return response, 200
        else:
            abort(
                404,
                message='Address with id {} not found.'.format(address_id)
            )
