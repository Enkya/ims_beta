from flask import request, jsonify, g, url_for
from flask_restplus import abort, Resource, fields, Namespace, marshal_with
from flask_restplus import marshal
from sqlalchemy import desc
from app.models.company import Company
from app.models.resource import ResourceMeta
from app.models.telecom import Telecom
from app.models.employee import Employee
from app.utils.utilities import auth
from instance.config import Config
from datetime import datetime


telecom_api = Namespace(
    'telecom', description='A telecom creation namespace')

service_provider_fields = {
    'name': fields.String(required=False, attribute='service_provider.name')
}

telecom_fields = telecom_api.model(
    'Telecom',
    {
        'id': fields.Integer(),
        'serviceDetails': fields.String(
            attribute='service_details'),
        'serviceTechnology': fields.String(attribute='service_technology'),
        'applicableServiceType': fields.String(
            attribute='applicable_service_type'),
        'qosRequirementsClaimsStatus': fields.String(
            attribute='qos_requirements_claims_status'),
        'coverageAreaDetails': fields.String(
            attribute='coverage_area_details'),
        'sharingRequirements': fields.String(attribute='sharing_requirements'),
        'protectionStatus': fields.String(attribute='protection_status'),
        'essentialResourceAuthStatus': fields.String(
            attribute='essential_resource_auth_status'),
        'outageStatus': fields.String(attribute='outage_status'),
        'emergencyServiceRequirements': fields.String(
            attribute='emergency_service_requirements'),
        'generalProvisions': fields.String(attribute='general_provisions'),
        'notes': fields.String(attribute='notes'),
        'recommendations': fields.String(attribute='recommendations'),
        'reviewedBy': fields.String(
            attribute='reviewed_by.contact_person.person.full_name'),
        'approvedBy': fields.String(
            attribute='approved_by.contact_person.person.full_name'),
        'inspectedBy': fields.String(
            attribute='inspected_by.contact_person.person.full_name'),
        'report': fields.String(attribute='report.full_name'),
        'outageReport': fields.String(attribute='outage_report.full_name'),
        'date_created': fields.DateTime(
            required=False,
            attribute='date_created'),
        'date_modified': fields.DateTime(
            required=False,
            attribute='date_modified')
    }
)


@telecom_api.route('', endpoint='telecom')
class TelecomEndPoint(Resource):

    @telecom_api.response(200, 'Successful Retrieval of Telecom records')
    @telecom_api.response(200, 'No telecom records found')
    def get(self):
        ''' Retrieve telecom records'''
        search_term = request.args.get('q') or None
        limit = request.args.get('limit') or Config.MAX_PAGE_SIZE
        page_limit = 100 if int(limit) > 100 else int(limit)
        page = request.args.get('page') or 1

        if page_limit < 1 or page < 1:
            return abort(400, 'Page or Limit cannot be negative values')

        telecom_data = Telecom.query.filter_by(active=True).\
            order_by(desc(Telecom.date_created))
        if telecom_data.all():
            telecom_records = telecom_data

            if search_term:
                telecom_records = telecom_data.filter(
                    Telecom.name.ilike('%'+search_term+'%')
                )

            telecom_paged = telecom_records.paginate(
                page=page, per_page=page_limit, error_out=True
            )
            results = dict(data=marshal(
                telecom_paged.items,
                telecom_fields))

            pages = {
                'page': page,
                'per_page': page_limit,
                'total_data': telecom_paged.total,
                'pages': telecom_paged.pages
            }

            if page == 1:
                pages['prev_page'] = url_for('api.telecom') + \
                    '?limit={}'.format(page_limit)

            if page > 1:
                pages['prev_page'] = url_for('api.telecom') + \
                    '?limit={}&page={}'.format(page_limit, page-1)

            if page < telecom_paged.pages:
                pages['next_page'] = url_for('api.telecom') + \
                    '?limit={}&page={}'.format(page_limit, page+1)

            results.update(pages)
            return results, 200
        return abort(404, message='No Telecom found for specified user')

    @telecom_api.response(201, 'Telecom created successfully!')
    @telecom_api.response(409, 'Telecom already exists!')
    @telecom_api.response(500, 'Internal Server Error')
    @telecom_api.doc(model='Telecom', body=telecom_fields)
    def post(self):
        ''' Create a telecom resource'''
        arguments = request.get_json(force=True)
        service_details = arguments.get('serviceDetails').strip() or None
        service_technology = arguments.get('serviceTechnology').strip() or None
        qos_requirements_claims_status = arguments.get(
            'qosRequirementsClaimsStatus').strip() or None
        coverage_area_details = arguments.get(
            'coverageAreaDetails').strip() or None
        sharing_requirements = arguments.get(
            'sharingRequirements').strip() or None
        protection_status = arguments.get(
            'protectionStatus').strip() or None
        essential_resource_auth_status = arguments.get(
            'essentialResourceAuthStatus').strip() or None
        outage_status = arguments.get('outageStatus').strip() or None
        emergency_service_requirements = arguments.get(
            'emergencyServiceRequirements').strip() or None
        general_provisions = arguments.get('generalProvisions').strip() or None
        notes = arguments.get('notes').strip() or None
        recommendations = arguments.get('recommendations').strip() or None
        reviewed_by_id = arguments.get('reviewedBy').strip() or None
        approved_by_id = arguments.get('approvedBy').strip() or None
        inspected_by_id = arguments.get('inspectedBy').strip() or None
        report_url = arguments.get('report').strip() or None
        outage_report_url = arguments.get('outageReport').strip() or None

        try:
            report = ResourceMeta.query.filter_by(full_name=report_url).first()
            if not report:
                report = ResourceMeta(
                    version=1,
                    name=report_url.split('/')[-1],
                    location=report_url.split('/')[:-1])
            outage_report = ResourceMeta.query.filter_by(
                full_name=outage_report_url).first()
            if not outage_report:
                report = ResourceMeta(
                    version=1,
                    name=outage_report_url.split('/')[-1],
                    location=outage_report_url.split('/')[:-1])
            reviewed_by = Employee.query.filter_by(id=reviewed_by_id).first()
            approved_by = Employee.query.filter_by(id=approved_by_id).first()
            inspected_by = Employee.query.filter_by(id=inspected_by_id).first()

            telecom = Telecom(
                service_details=service_details,
                service_technology=service_technology,
                qos_requirements_claims_status=qos_requirements_claims_status,
                coverage_area_details=coverage_area_details,
                sharing_requirements=sharing_requirements,
                protection_status=protection_status,
                essential_resource_auth_status=essential_resource_auth_status,
                outage_status=outage_status,
                emergency_service_requirements=emergency_service_requirements,
                general_provisions=general_provisions,
                notes=notes,
                recommendations=recommendations,
                reviewed_by=reviewed_by,
                approved_by=approved_by,
                inspected_by=inspected_by,
                report=report
                )
            if telecom.save_telecom():
                return {
                    'message': 'Telecom record created successfully!'}, 201
            return abort(409, message='Telecom already exists!')
        except Exception as e:
            abort(
                400,
                message='Failed to create new telecom -> {}'.format(e))


@telecom_api.route('/<int:telecom_id>', endpoint='single_telecom')
class SingleTelecomEndpoint(Resource):

    @telecom_api.header('x-access-token', 'Access Token', required=True)
    @marshal_with(telecom_fields)
    @telecom_api.response(200, 'Successful retrieval of telecom')
    @telecom_api.response(400, 'No telecom found with specified ID')
    def get(self, telecom_id):
        ''' Retrieve individual telecom with given telecom_id '''
        telecom = Telecom.query.filter_by(
            id=telecom_id, active=True).first()
        if telecom:
            return telecom, 200
        abort(404, message='No telecom found with specified ID')

    @telecom_api.header('x-access-token', 'Access Token', required=True)
    @telecom_api.response(200, 'Successfully Updated Telecom')
    @telecom_api.response(
        400,
        'Telecom with id {} not found or not yours.')
    @telecom_api.marshal_with(telecom_fields)
    def put(self, telecom_id):
        ''' Update telecom with given telecom_id '''
        arguments = request.get_json(force=True)
        name = arguments.get('name').strip()
        telecom = Telecom.query.filter_by(
            id=telecom_id, active=True).first()
        if telecom:
            if name:
                telecom.name = name
            telecom.save()
            return telecom, 200
        else:
            abort(
                404,
                message='Telecom with id {} not found'.format(telecom_id))

    @telecom_api.header('x-access-token', 'Access Token', required=True)
    @auth.login_required
    @telecom_api.response(200, 'Telecom with id {} successfully deleted.')
    @telecom_api.response(
        400,
        'Telecom with id {} not found or not yours.')
    def delete(self, telecom_id):
        ''' Delete telecom with telecom_id as given '''
        telecom = Telecom.query.filter_by(
            id=telecom_id, active=True).first()
        if telecom:
            if telecom.delete_telecom():
                response = {
                    'message': 'Telecom with id {} deleted.'.format(
                        telecom_id)
                }
            return response, 200
        else:
            abort(
                404,
                message='Telecom with id {} not found.'.format(telecom_id)
            )
