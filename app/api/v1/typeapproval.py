from flask import request, jsonify, g, url_for
from flask_restplus import abort, Resource, fields, Namespace, marshal_with
from flask_restplus import marshal
from sqlalchemy import desc
from app.models.company import Company
from app.models.employee import Employee
from app.models.uniqueId import UniqueId
from app.models.resource import ResourceMeta
from app.models.typeapproval import Typeapproval
from app.utils.utilities import auth, load_json_data, updateObject, formatType
from instance.config import Config
from datetime import datetime

typeapproval_api = Namespace(
    'typeapproval', description='A typeapproval creation namespace')

typeapproval_fields = typeapproval_api.model(
    'Typeapproval',
    {
        'id': fields.Integer(),
        'taUniqueId': fields.String(
            required=True,
            attribute='ta_unique_id.value'),
        'equipmentCategory': fields.String(
            required=False,
            attribute='equipment_category'),
        'equipmentModel': fields.String(
            required=False,
            attribute='equipment_model'),
        'equipmentName': fields.String(
            required=False,
            attribute='equipment_name'),
        'equipmentDesc': fields.String(
            required=False,
            attribute='equipment_desc'),
        'statusApproved': fields.Boolean(attribute='status_approved'),
        'applicableStandards': fields.String(
            required=False, attribute='applicable_standards'),
        'approvalRejectionDate': fields.DateTime(
            required=False,
            attribute='approval_rejection_date'),
        'applicant': fields.String(required=False, attribute='applicant.name'),
        'assessedBy': fields.String(
            required=False,
            attribute='assessed_by.contact_person.person.full_name'),
        'report': fields.String(required=False, attribute='report.full_name'),
        'taCertificate': fields.String(
            required=False,
            attribute='ta_certificate.full_name'),
        'date_created': fields.DateTime(
            required=False,
            attribute='date_created'),
        'date_modified': fields.DateTime(
            required=False,
            attribute='date_modified'),
    }
)

import os
fields = load_json_data(
    os.path.join(__file__.split('api')[0], "utils/fields"),
    'typeapproval'
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
                typeapproval_records = typeapproval.filter(
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
        field_data = {}
        for x in fields.keys():
            field_data[x] = {}
        for k, v in arguments.items():
            v = formatType(v)
            for item_key, val in fields.items():
                if k in list(val.keys()):
                    field_data[item_key][val[k]] = v

        try:
            report_url = field_data['typeapproval_fields']['report_url']
            report = ResourceMeta.query.filter_by(full_name=report_url).first()
            if not report:
                report = ResourceMeta({
                    'version':1,
                    'name':report_url.split('/')[-1],
                    'location':report_url.split('/')[:-1]
                })
            field_data['typeapproval_fields']['report'] = report
            field_data['typeapproval_fields'].pop('report_url', None)
            applicant_id = field_data['typeapproval_fields']['applicant_id']
            if not applicant_id:
                return abort(400, message='Applicant needed to process data')
            field_data['typeapproval_fields']['applicant'] = Company.query.filter_by(
                id=applicant_id,
                active=True).first()
            field_data['typeapproval_fields'].pop('applicant_id', None)
            field_data['typeapproval_fields']['assessed_by'] = Employee.query.filter_by(
                id=field_data['typeapproval_fields']['assessed_by_id']
            ).first()
            field_data['typeapproval_fields'].pop('assessed_by_id', None)
            field_data['typeapproval_fields']['ta_certificate_id'] = ResourceMeta.query.filter_by(
                id=field_data['typeapproval_fields']['ta_certificate_id']
            ).first()
            field_data['typeapproval_fields'].pop('ta_certificate_id', None)
            typeapproval = Typeapproval(field_data['typeapproval_fields'])
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
    def patch(self, typeapproval_id):
        ''' Update typeapproval with given typeapproval_id '''
        arguments = request.get_json(force=True)
        typeapproval = Typeapproval.query.filter_by(
            id=typeapproval_id, active=True).first()
        if not typeapproval:
            abort(
                404,
                message='Typeapproval with id {} not found'.format(
                    typeapproval_id))
        try:
            typeapproval = updateObject(typeapproval, arguments, fields['typeapproval_fields'])
            typeapproval.save()
            return typeapproval, 200
        except Exception as e:
            abort(400, message='{}'.format(e))

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
