from flask import request, jsonify, g, url_for
from flask_restplus import abort, Resource, fields, Namespace, marshal_with
from flask_restplus import marshal
from sqlalchemy import desc
from app.models.company import Company
from app.models.resource import ResourceMeta
from app.models.postal import Postal
from app.models.employee import Employee
from app.utils.utilities import auth
from instance.config import Config
from datetime import datetime


postal_api = Namespace(
    'postal', description='A postal creation namespace')

postal_fields = postal_api.model(
    'Postal',
    {
        'id': fields.Integer(),
        'callSign': fields.String(
            attribute='call_sign'),
        'physicalLocationRequirements': fields.String(
            attribute='physical_location_requirements'),
        'licenseValidity': fields.Integer(
            attribute='license_validity'),
        'postalArticleConfidentiality': fields.Integer(
            attribute='postal_article_confidentiality'),
        'trainingRequirements': fields.Boolean(
            attribute='training_requirements'),
        'qosRequirementsWorkingDays': fields.Boolean(
            attribute='qos_reqs_working_days'),
        'qosRequirementsClaimsPolicy': fields.Boolean(
            attribute='qos_reqs_claims_policy'),
        'qosRequirementsControlProhibitedItems': fields.Boolean(
            attribute='qos_reqs_ctrl_prohibit_items'),
        'qosRequirementsComplaintsRegister': fields.Boolean(
            attribute='qos_reqs_complaints_register'),
        'notes01': fields.String(
            attribute='notes_01'),
        'notes02': fields.String(attribute='notes_02'),
        'recommendations': fields.String(attribute='recommendations'),
        'reviewedBy': fields.String(
            attribute='reviewed_by.contact_person.person.full_name'),
        'approvedBy': fields.String(
            attribute='approved_by.contact_person.person.full_name'),
        'inspectedBy': fields.String(
            attribute='inspected_by.contact_person.person.full_name'),
        'report': fields.String(attribute='report.full_name'),
        'date_created': fields.DateTime(
            required=False,
            attribute='date_created'),
        'date_modified': fields.DateTime(
            required=False,
            attribute='date_modified')
    }
)


@postal_api.route('', endpoint='postal')
class PostalEndPoint(Resource):

    @postal_api.response(200, 'Successful Retrieval of Postal records')
    @postal_api.response(200, 'No postal records found')
    def get(self):
        ''' Retrieve postal records'''
        search_term = request.args.get('q') or None
        limit = request.args.get('limit') or Config.MAX_PAGE_SIZE
        page_limit = 100 if int(limit) > 100 else int(limit)
        page = request.args.get('page') or 1

        if page_limit < 1 or page < 1:
            return abort(400, 'Page or Limit cannot be negative values')

        postal_data = Postal.query.filter_by(active=True).\
            order_by(desc(Postal.date_created))
        if postal_data.all():
            postal_records = postal_data

            if search_term:
                postal_records = postal_data.filter(
                    Postal.name.ilike('%'+search_term+'%')
                )

            postal_paged = postal_records.paginate(
                page=page, per_page=page_limit, error_out=True
            )
            results = dict(data=marshal(
                postal_paged.items,
                postal_fields))

            pages = {
                'page': page,
                'per_page': page_limit,
                'total_data': postal_paged.total,
                'pages': postal_paged.pages
            }

            if page == 1:
                pages['prev_page'] = url_for('api.postal') + \
                    '?limit={}'.format(page_limit)

            if page > 1:
                pages['prev_page'] = url_for('api.postal') + \
                    '?limit={}&page={}'.format(page_limit, page-1)

            if page < postal_paged.pages:
                pages['next_page'] = url_for('api.postal') + \
                    '?limit={}&page={}'.format(page_limit, page+1)

            results.update(pages)
            return results, 200
        return abort(404, message='No Postal found for specified user')

    @postal_api.response(201, 'Postal created successfully!')
    @postal_api.response(409, 'Postal already exists!')
    @postal_api.response(500, 'Internal Server Error')
    @postal_api.doc(model='Postal', body=postal_fields)
    def post(self):
        ''' Create a postal resource'''
        arguments = request.get_json(force=True)
        call_sign = arguments.get('callSign').strip() or None
        physical_location_requirements = arguments.get(
            'physicalLocationRequirements').strip() or None
        license_validity = int(arguments.get(
            'licenseValidity').strip()) or None
        postal_article_confidentiality = int(arguments.get(
            'postalArticleConfidentiality').strip()) or None
        training_requirements = arguments.get(
            'trainingRequirements') or False
        qos_reqs_working_days = arguments.get(
            'qosRequirementsWorkingDays') or False
        qos_reqs_claims_policy = arguments.get(
            'qosRequirementsClaimsPolicy') or False
        qos_reqs_ctrl_prohibit_items = arguments.get(
            'qosRequirementsControlProhibitedItems') or False
        qos_reqs_complaints_register = arguments.get(
            'qosRequirementsComplaintsRegister') or False
        notes_01 = arguments.get('notes01').strip() or None
        notes_02 = arguments.get('notes02').strip() or None
        recommendations = arguments.get('recommendations').strip() or None
        reviewed_by_id = arguments.get('reviewedBy').strip() or None
        approved_by_id = arguments.get('approvedBy').strip() or None
        inspected_by_id = arguments.get('inspectedBy').strip() or None
        report_url = arguments.get('report').strip() or None

        try:
            report = ResourceMeta.query.filter_by(full_name=report_url).first()
            if not report:
                report = ResourceMeta(
                    version=1,
                    name=report_url.split('/')[-1],
                    location=report_url.split('/')[:-1])
            reviewed_by = Employee.query.filter_by(id=reviewed_by_id).first()
            approved_by = Employee.query.filter_by(id=approved_by_id).first()
            inspected_by = Employee.query.filter_by(id=inspected_by_id).first()

            postal = Postal(
                call_sign=call_sign,
                physical_location_requirements=physical_location_requirements,
                license_validity=license_validity,
                postal_article_confidentiality=postal_article_confidentiality,
                training_requirements=training_requirements,
                qos_reqs_working_days=qos_reqs_working_days,
                qos_reqs_ctrl_prohibit_items=qos_reqs_ctrl_prohibit_items,
                qos_reqs_claims_policy=qos_reqs_claims_policy,
                qos_reqs_complaints_register=qos_reqs_complaints_register,
                notes_01=notes_01,
                notes_02=notes_02,
                recommendations=recommendations,
                reviewed_by=reviewed_by,
                approved_by=approved_by,
                inspected_by=inspected_by,
                report=report
                )
            if postal.save_postal():
                return {
                    'message': 'Postal record created successfully!'}, 201
            return abort(409, message='Postal already exists!')
        except Exception as e:
            abort(
                400,
                message='Failed to create new postal -> {}'.format(e))


@postal_api.route('/<int:postal_id>', endpoint='single_postal')
class SinglePostalEndpoint(Resource):

    @postal_api.header('x-access-token', 'Access Token', required=True)
    @marshal_with(postal_fields)
    @postal_api.response(200, 'Successful retrieval of postal')
    @postal_api.response(400, 'No postal found with specified ID')
    def get(self, postal_id):
        ''' Retrieve individual postal with given postal_id '''
        postal = Postal.query.filter_by(
            id=postal_id, active=True).first()
        if postal:
            return postal, 200
        abort(404, message='No postal found with specified ID')

    @postal_api.header('x-access-token', 'Access Token', required=True)
    @postal_api.response(200, 'Successfully Updated Postal')
    @postal_api.response(
        400,
        'Postal with id {} not found or not yours.')
    @postal_api.marshal_with(postal_fields)
    def put(self, postal_id):
        ''' Update postal with given postal_id '''
        arguments = request.get_json(force=True)
        name = arguments.get('name').strip()
        postal = Postal.query.filter_by(
            id=postal_id, active=True).first()
        if postal:
            if name:
                postal.name = name
            postal.save()
            return postal, 200
        else:
            abort(
                404,
                message='Postal with id {} not found'.format(postal_id))

    @postal_api.header('x-access-token', 'Access Token', required=True)
    @auth.login_required
    @postal_api.response(200, 'Postal with id {} successfully deleted.')
    @postal_api.response(
        400,
        'Postal with id {} not found or not yours.')
    def delete(self, postal_id):
        ''' Delete postal with postal_id as given '''
        postal = Postal.query.filter_by(
            id=postal_id, active=True).first()
        if postal:
            if postal.delete_postal():
                response = {
                    'message': 'Postal with id {} deleted.'.format(
                        postal_id)
                }
            return response, 200
        else:
            abort(
                404,
                message='Postal with id {} not found.'.format(postal_id)
            )
