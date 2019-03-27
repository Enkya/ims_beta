from flask import request, jsonify, g, url_for
from flask_restplus import abort, Resource, fields, Namespace, marshal_with
from flask_restplus import marshal
from sqlalchemy import desc
from app.models.company import Company
from app.models.resource import ResourceMeta
from app.models.typeapproval import Typeapproval
from app.utils.utilities import auth
from instance.config import Config


typeapproval_api = Namespace(
    'typeapproval', description='A typeapproval creation namespace')

typeapproval_fields = typeapproval_api.model(
    'Typeapproval',
    {
        'id': fields.Integer(),
        'taUniqueId': fields.String(
            required=True,
            attribute='ta_unique_id'),
        'status_approved': fields.Boolean(attribute='status_approved'),
        'date_created': fields.DateTime(
            required=False,
            attribute='date_created'),
        'date_modified': fields.DateTime(
            required=False,
            attribute='date_modified'),
    }
)


@typeapproval_api.route('', endpoint='typeapproval')
class TypeapprovalEndPoint(Resource):

    @typeapproval_api.response(
        200,
        'Successful Retrieval of Typeapproval records')
    @typeapproval_api.response(200, 'No typeapproval records found')
    def get(self):
        ''' Retrieve typeapproval records'''
        search_term = request.args.get('q') or None
        limit = request.args.get('limit') or Config.MAX_PAGE_SIZE
        page_limit = 100 if int(limit) > 100 else int(limit)
        page = request.args.get('page') or 1

        if page_limit < 1 or page < 1:
            return abort(400, 'Page or Limit cannot be negative values')

        typeapproval = Typeapproval.query.filter_by(active=True).\
            order_by(desc(Typeapproval.date_created))
        if typeapproval.all():
            typeapproval_records = typeapproval

            if search_term:
                typeapproval_records = typeapproval_data.filter(
                    Typeapproval.ta_unique_id.ilike('%'+search_term+'%')
                )

            typeapproval_paged = typeapproval_records.paginate(
                page=page, per_page=page_limit, error_out=True
            )
            results = dict(data=marshal(
                typeapproval_paged.items,
                typeapproval_fields))

            pages = {
                'page': page,
                'per_page': page_limit,
                'total_data': typeapproval_paged.total,
                'pages': typeapproval_paged.pages
            }

            if page == 1:
                pages['prev_page'] = url_for('api.typeapproval') + \
                    '?limit={}'.format(page_limit)

            if page > 1:
                pages['prev_page'] = url_for('api.typeapproval') + \
                    '?limit={}&page={}'.format(page_limit, page-1)

            if page < typeapproval_paged.pages:
                pages['next_page'] = url_for('api.typeapproval') + \
                    '?limit={}&page={}'.format(page_limit, page+1)

            results.update(pages)
            return results, 200
        return abort(404, message='No Typeapproval found for specified user')

    @typeapproval_api.response(201, 'Typeapproval created successfully!')
    @typeapproval_api.response(409, 'Typeapproval already exists!')
    @typeapproval_api.response(500, 'Internal Server Error')
    @typeapproval_api.doc(model='Typeapproval', body=typeapproval_fields)
    def post(self):
        ''' Create a typeapproval resource'''
        arguments = request.get_json(force=True)
        status_approved = arguments.get('statusApproved') or False
        applicant_id = int(arguments.get('applicant').strip())
        report_url = arguments.get('report').strip() or ''

        try:
            report = ResourceMeta.query.filter_by(full_name=report_url).first()
            if not report:
                report = ResourceMeta(
                    version=1,
                    name=report_url.split('/')[-1],
                    location=report_url.split('/')[:-1])
            applicant = Company.query.filter_by(
                id=applicant_id,
                active=True).first()
            typeapproval = Typeapproval(
                status_approved=status_approved,
                applicant=applicant,
                report=report
                )
            if typeapproval.save_typeapproval():
                return {
                        'message': 'Typeapproval record created successfully!'
                    }, 201
            return abort(409, message='Typeapproval already exists!')
        except Exception as e:
            abort(
                400,
                message='Failed to create new typeapproval -> {}'.format(e))


@typeapproval_api.route(
    '/<int:typeapproval_id>',
    endpoint='single_typeapproval')
class SingleTypeapprovalEndpoint(Resource):

    @typeapproval_api.header('x-access-token', 'Access Token', required=True)
    @marshal_with(typeapproval_fields)
    @typeapproval_api.response(200, 'Successful retrieval of typeapproval')
    @typeapproval_api.response(400, 'No typeapproval found with specified ID')
    def get(self, typeapproval_id):
        ''' Retrieve individual typeapproval with given typeapproval_id '''
        typeapproval = Typeapproval.query.filter_by(
            id=typeapproval_id, active=True).first()
        if typeapproval:
            return typeapproval, 200
        abort(404, message='No typeapproval found with specified ID')

    @typeapproval_api.header('x-access-token', 'Access Token', required=True)
    @typeapproval_api.response(200, 'Successfully Updated Typeapproval')
    @typeapproval_api.response(
        400,
        'Typeapproval with id {} not found or not yours.')
    @typeapproval_api.marshal_with(typeapproval_fields)
    def put(self, typeapproval_id):
        ''' Update typeapproval with given typeapproval_id '''
        arguments = request.get_json(force=True)
        name = arguments.get('name').strip()
        typeapproval = Typeapproval.query.filter_by(
            id=typeapproval_id, active=True).first()
        if typeapproval:
            if name:
                typeapproval.name = name
            typeapproval.save()
            return typeapproval, 200
        else:
            abort(
                404,
                message='Typeapproval with id {} not found'.format(
                    typeapproval_id))

    @typeapproval_api.header('x-access-token', 'Access Token', required=True)
    @auth.login_required
    @typeapproval_api.response(
        200, 'Typeapproval with id {} successfully deleted.')
    @typeapproval_api.response(
        400,
        'Typeapproval with id {} not found or not yours.')
    def delete(self, typeapproval_id):
        ''' Delete typeapproval with typeapproval_id as given '''
        typeapproval = Typeapproval.query.filter_by(
            id=typeapproval_id, active=True).first()
        if typeapproval:
            if typeapproval.delete_typeapproval():
                response = {
                    'message': 'Typeapproval with id {} deleted.'.format(
                        typeapproval_id)
                }
            return response, 200
        else:
            abort(
                404,
                message='Typeapproval with id {} not found.'.format(
                    typeapproval_id)
            )
