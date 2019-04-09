from flask import request, jsonify, g, url_for
from flask_restplus import abort, Resource, fields, Namespace, marshal_with
from flask_restplus import marshal
from sqlalchemy import desc
from app.models.company import Company
from app.models.resource import ResourceMeta
from app.models.spectrum import Spectrum
from app.models.employee import Employee
from app.utils.utilities import auth
from instance.config import Config
from datetime import datetime


spectrum_api = Namespace(
    'spectrum', description='A spectrum creation namespace')

spectrum_fields = spectrum_api.model(
    'Spectrum',
    {
        'id': fields.Integer(),
        'assignedTransmissionPower': fields.Integer(
            attribute='assigned_transmission_power'),
        'authorizedAntennaGain': fields.Integer(
            attribute='authorized_antenna_gain'),
        'authorizedAntennaHeight': fields.Integer(
            attribute='authorized_antenna_height'),
        'authorized_transmit_location': fields.String(
            attribute='authorized_transmit_location'),
        'assignedStlFrequency': fields.Integer(
            attribute='assigned_stl_frequency'),
        'assignedStlPower': fields.Integer(
            attribute='assigned_stl_power'),
        'assignedStlLocation': fields.String(
            attribute='assigned_stl_location'),
        'txFreqAssignDate': fields.DateTime(
            attribute='tx_freq_assign_date'),
        'stlFreqAssignDate': fields.DateTime(
            attribute='stl_freq_assign_date'),
        'bandOfOperation': fields.String(
            attribute='band_of_operation'),
        'serviceAuthorized': fields.String(
            attribute='service_authorized'),
        'authorizedBy': fields.String(
            attribute='authorized_by.contact_person.person.full_name'),
        'assignedBy': fields.String(
            attribute='assigned_by.contact_person.person.full_name'),
        'report': fields.String(attribute='report.full_name'),
        'applicant': fields.String(required=False, attribute='applicant.name'),
        'date_created': fields.DateTime(
            attribute='date_created'),
        'date_modified': fields.DateTime(
            attribute='date_modified'),
    }
)


@spectrum_api.route('', endpoint='spectrum')
class SpectrumEndPoint(Resource):

    @spectrum_api.response(
        200,
        'Successful Retrieval of Spectrum records')
    @spectrum_api.response(200, 'No spectrum records found')
    def get(self):
        ''' Retrieve spectrum records'''
        search_term = request.args.get('q') or None
        limit = request.args.get('limit') or Config.MAX_PAGE_SIZE
        page_limit = 100 if int(limit) > 100 else int(limit)
        page = request.args.get('page') or 1

        if page_limit < 1 or page < 1:
            return abort(400, 'Page or Limit cannot be negative values')

        spectrum = Spectrum.query.filter_by(active=True).\
            order_by(desc(Spectrum.date_created))
        if spectrum.all():
            spectrum_records = spectrum

            if search_term:
                spectrum_records = spectrum_data.filter(
                    Spectrum.assigned_transmission_power.ilike(
                        '%'+search_term+'%')
                )

            spectrum_paged = spectrum_records.paginate(
                page=page, per_page=page_limit, error_out=True
            )
            results = dict(data=marshal(
                spectrum_paged.items,
                spectrum_fields))

            pages = {
                'page': page,
                'per_page': page_limit,
                'total_data': spectrum_paged.total,
                'pages': spectrum_paged.pages
            }

            if page == 1:
                pages['prev_page'] = url_for('api.spectrum') + \
                    '?limit={}'.format(page_limit)

            if page > 1:
                pages['prev_page'] = url_for('api.spectrum') + \
                    '?limit={}&page={}'.format(page_limit, page-1)

            if page < spectrum_paged.pages:
                pages['next_page'] = url_for('api.spectrum') + \
                    '?limit={}&page={}'.format(page_limit, page+1)

            results.update(pages)
            return results, 200
        return abort(404, message='No Spectrum found for specified user')

    @spectrum_api.response(201, 'Spectrum created successfully!')
    @spectrum_api.response(409, 'Spectrum already exists!')
    @spectrum_api.response(500, 'Internal Server Error')
    @spectrum_api.doc(model='Spectrum', body=spectrum_fields)
    def post(self):
        ''' Create a spectrum resource'''
        arguments = request.get_json(force=True)
        assigned_transmission_power = int(
            arguments.get('assignedTransmissionPower').strip()) or None
        authorized_antenna_gain = int(
            arguments.get('authorizedAntennaGain').strip()) or None
        authorized_antenna_height = int(
            arguments.get('authorizedAntennaHeight').strip()) or None
        authorized_transmit_location = arguments.get(
            'authorizedTransmitLocation').strip() or None
        assigned_stl_frequency = int(
            arguments.get('authorizedStlFrequency').strip()) or None
        assigned_stl_power = int(
            arguments.get('authorizedStlPower').strip()) or None
        assigned_stl_location = arguments.get(
            'authorizedStlLocation').strip() or None
        tx_freq_assign_date = arguments.get(
            'txFreqAssignDate').strip() or None
        tx_freq_assign_date = datetime.strptime(
            tx_freq_assign_date, '%d-%m-%y'
        )
        stl_freq_assign_date = arguments.get(
            'stlFreqAssignDate').strip() or None
        stl_freq_assign_date = datetime.strptime(
            stl_freq_assign_date, '%d-%m-%y'
        )
        band_of_operation = arguments.get('bandOfOperation').strip() or None
        service_authorized = arguments.get('serviceAuthorized').strip() or None

        assigned_by_id = int(arguments.get('assignedBy').strip()) or None
        authorized_by_id = int(arguments.get('authorizedBy').strip()) or None
        applicant_id = int(arguments.get('applicant').strip()) or None
        report_url = arguments.get('report').strip() or None

        try:
            report = ResourceMeta.query.filter_by(full_name=report_url).first()
            if not report:
                report = ResourceMeta(
                    version=1,
                    name=report_url.split('/')[-1],
                    location=report_url.split('/')[:-1])
            if not applicant_id:
                return abort(400, message='Applicant needed to process data')
            applicant = Company.query.filter_by(
                id=applicant_id,
                active=True).first()
            assigned_by = Employee.query.filter_by(
                id=assigned_by_id).first()
            authorized_by = Employee.query.filter_by(
                id=authorized_by_id).first()

            spectrum = Spectrum(
                assigned_transmission_power=assigned_transmission_power,
                authorized_antenna_gain=authorized_antenna_gain,
                authorized_antenna_height=authorized_antenna_height,
                authorized_transmit_location=authorized_transmit_location,
                assigned_stl_frequency=assigned_stl_frequency,
                assigned_stl_power=assigned_stl_power,
                assigned_stl_location=assigned_stl_location,
                tx_freq_assign_date=tx_freq_assign_date,
                stl_freq_assign_date=stl_freq_assign_date,
                band_of_operation=band_of_operation,
                service_authorized=service_authorized,
                assigned_by=assigned_by,
                authorized_by=authorized_by,
                applicant=applicant,
                report=report
                )
            if spectrum.save_spectrum():
                return {
                        'message': 'Spectrum record created successfully!'
                    }, 201
            return abort(409, message='Spectrum already exists!')
        except Exception as e:
            abort(
                400,
                message='Failed to create new spectrum -> {}'.format(e))


@spectrum_api.route(
    '/<int:spectrum_id>',
    endpoint='single_spectrum')
class SingleSpectrumEndpoint(Resource):

    # @spectrum_api.header('x-access-token', 'Access Token', required=True)
    @marshal_with(spectrum_fields)
    @spectrum_api.response(200, 'Successful retrieval of spectrum')
    @spectrum_api.response(400, 'No spectrum found with specified ID')
    def get(self, spectrum_id):
        ''' Retrieve individual spectrum with given spectrum_id '''
        spectrum = Spectrum.query.filter_by(
            id=spectrum_id, active=True).first()
        if spectrum:
            return spectrum, 200
        abort(404, message='No spectrum found with specified ID')

    # @spectrum_api.header('x-access-token', 'Access Token', required=True)
    @spectrum_api.response(200, 'Successfully Updated Spectrum')
    @spectrum_api.response(
        400,
        'Spectrum with id {} not found or not yours.')
    @spectrum_api.marshal_with(spectrum_fields)
    def put(self, spectrum_id):
        ''' Update spectrum with given spectrum_id '''
        arguments = request.get_json(force=True)
        name = arguments.get('name').strip()
        spectrum = Spectrum.query.filter_by(
            id=spectrum_id, active=True).first()
        if spectrum:
            if name:
                spectrum.name = name
            spectrum.save()
            return spectrum, 200
        else:
            abort(
                404,
                message='Spectrum with id {} not found'.format(
                    spectrum_id))

    # @spectrum_api.header('x-access-token', 'Access Token', required=True)
    @auth.login_required
    @spectrum_api.response(
        200, 'Spectrum with id {} successfully deleted.')
    @spectrum_api.response(
        400,
        'Spectrum with id {} not found or not yours.')
    def delete(self, spectrum_id):
        ''' Delete spectrum with spectrum_id as given '''
        spectrum = Spectrum.query.filter_by(
            id=spectrum_id, active=True).first()
        if spectrum:
            if spectrum.delete_spectrum():
                response = {
                    'message': 'Spectrum with id {} deleted.'.format(
                        spectrum_id)
                }
            return response, 200
        else:
            abort(
                404,
                message='Spectrum with id {} not found.'.format(
                    spectrum_id)
            )
