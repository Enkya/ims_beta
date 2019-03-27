from flask import request, jsonify, g, url_for
from flask_restplus import abort, Resource, fields, Namespace, marshal_with
from flask_restplus import marshal
from sqlalchemy import desc
from app.models.company import Company
from app.models.resource import ResourceMeta
from app.models.numbering import Numbering
from app.utils.utilities import auth
from instance.config import Config


numbering_api = Namespace(
    'numbering', description='A numbering creation namespace')

service_provider_fields = {
    'name': fields.String(required=False, attribute='company.name')
}

numbering_fields = numbering_api.model(
    'Numbering',
    {
        'id': fields.Integer(),
        'serviceCategory': fields.String(
            required=True,
            attribute='service_category'),
        'numberType': fields.String(attribute='number_type'),
        'service_provider': fields.Nested(service_provider_fields),
        'date_created': fields.DateTime(
            required=False,
            attribute='date_created'),
        'date_modified': fields.DateTime(
            required=False,
            attribute='date_modified'),
    }
)


@numbering_api.route('', endpoint='numbering')
class NumberingEndPoint(Resource):

    @numbering_api.response(200, 'Successful Retrieval of Numbering records')
    @numbering_api.response(200, 'No numbering records found')
    def get(self):
        ''' Retrieve numbering records'''
        search_term = request.args.get('q') or None
        limit = request.args.get('limit') or Config.MAX_PAGE_SIZE
        page_limit = 100 if int(limit) > 100 else int(limit)
        page = request.args.get('page') or 1

        if page_limit < 1 or page < 1:
            return abort(400, 'Page or Limit cannot be negative values')

        numbering_data = Numbering.query.filter_by(active=True).\
            order_by(desc(Numbering.date_created))
        if numbering_data.all():
            numbering_records = numbering_data

            if search_term:
                numbering_records = numbering_data.filter(
                    Numbering.name.ilike('%'+search_term+'%')
                )

            numbering_paged = numbering_records.paginate(
                page=page, per_page=page_limit, error_out=True
            )
            results = dict(data=marshal(
                numbering_paged.items,
                numbering_fields))

            pages = {
                'page': page,
                'per_page': page_limit,
                'total_data': numbering_paged.total,
                'pages': numbering_paged.pages
            }

            if page == 1:
                pages['prev_page'] = url_for('api.numbering') + \
                    '?limit={}'.format(page_limit)

            if page > 1:
                pages['prev_page'] = url_for('api.numbering') + \
                    '?limit={}&page={}'.format(page_limit, page-1)

            if page < numbering_paged.pages:
                pages['next_page'] = url_for('api.numbering') + \
                    '?limit={}&page={}'.format(page_limit, page+1)

            results.update(pages)
            return results, 200
        return abort(404, message='No Numbering found for specified user')

    @numbering_api.response(201, 'Numbering created successfully!')
    @numbering_api.response(409, 'Numbering already exists!')
    @numbering_api.response(500, 'Internal Server Error')
    @numbering_api.doc(model='Numbering', body=numbering_fields)
    def post(self):
        ''' Create a numbering resource'''
        arguments = request.get_json(force=True)
        service_category = arguments.get('serviceCategory').strip()
        service_provider_id = int(arguments.get('serviceProvider').strip())
        number_type = arguments.get('numberType').strip() or ''
        report_url = arguments.get('report').strip() or ''

        if not service_category:
            return abort(400, 'Service Category cannot be empty!')
        try:
            report = ResourceMeta.query.filter_by(full_name=report_url).first()
            if not report:
                report = ResourceMeta(
                    version=1,
                    name=report_url.split('/')[-1],
                    location=report_url.split('/')[:-1])
            service_provider = Company.query.filter_by(
                id=service_provider_id,
                active=True).first()
            numbering = Numbering(
                service_category=service_category,
                service_provider=service_provider,
                number_type=number_type,
                report=report
                )
            if numbering.save_numbering():
                return {
                    'message': 'Numbering record created successfully!'}, 201
            return abort(409, message='Numbering already exists!')
        except Exception as e:
            abort(
                400,
                message='Failed to create new numbering -> {}'.format(e))


@numbering_api.route('/<int:numbering_id>', endpoint='single_numbering')
class SingleNumberingEndpoint(Resource):

    @numbering_api.header('x-access-token', 'Access Token', required=True)
    @marshal_with(numbering_fields)
    @numbering_api.response(200, 'Successful retrieval of numbering')
    @numbering_api.response(400, 'No numbering found with specified ID')
    def get(self, numbering_id):
        ''' Retrieve individual numbering with given numbering_id '''
        numbering = Numbering.query.filter_by(
            id=numbering_id, active=True).first()
        if numbering:
            return numbering, 200
        abort(404, message='No numbering found with specified ID')

    @numbering_api.header('x-access-token', 'Access Token', required=True)
    @numbering_api.response(200, 'Successfully Updated Numbering')
    @numbering_api.response(
        400,
        'Numbering with id {} not found or not yours.')
    @numbering_api.marshal_with(numbering_fields)
    def put(self, numbering_id):
        ''' Update numbering with given numbering_id '''
        arguments = request.get_json(force=True)
        name = arguments.get('name').strip()
        numbering = Numbering.query.filter_by(
            id=numbering_id, active=True).first()
        if numbering:
            if name:
                numbering.name = name
            numbering.save()
            return numbering, 200
        else:
            abort(
                404,
                message='Numbering with id {} not found'.format(numbering_id))

    @numbering_api.header('x-access-token', 'Access Token', required=True)
    @auth.login_required
    @numbering_api.response(200, 'Numbering with id {} successfully deleted.')
    @numbering_api.response(
        400,
        'Numbering with id {} not found or not yours.')
    def delete(self, numbering_id):
        ''' Delete numbering with numbering_id as given '''
        numbering = Numbering.query.filter_by(
            id=numbering_id, active=True).first()
        if numbering:
            if numbering.delete_numbering():
                response = {
                    'message': 'Numbering with id {} deleted.'.format(
                        numbering_id)
                }
            return response, 200
        else:
            abort(
                404,
                message='Numbering with id {} not found.'.format(numbering_id)
            )
