from flask import request, jsonify, g, url_for
from flask_restplus import abort, Resource, fields, Namespace, marshal_with
from flask_restplus import marshal
from sqlalchemy import desc

from app.models.company import Company
from app.models.address import Address
from app.models.person import Person
from app.models.contact import Contact
from app.models.contact_person import ContactPerson
from app.models.user import User
from app.models.numbering import Numbering
from app.models.postal import Postal
from app.models.spectrum import Spectrum
from app.models.telecom import Telecom
from app.models.typeapproval import Typeapproval

from app.utils.utilities import auth
from instance.config import Config

from .numbering import numbering_fields
from .postal import postal_fields
from .spectrum import spectrum_fields
from .telecom import telecom_fields
from .typeapproval import typeapproval_fields


company_api = Namespace(
    'companies', description='A company creation namespace')

address_fields = company_api.model(
    'address',
    {
        'district': fields.String(required=False, attribute='district'),
        'postal': fields.String(required=False, attribute='postal_code'),
        'country': fields.String(required=False, attribute='country'),
        'address_line_1': fields.String(
            required=True,
            attribute='address_line_1'),
        'address_line_2': fields.String(
            required=True,
            attribute='address_line_2'),
    }
)

contact_people_fields = company_api.model(
    'contact_people',
    {
        'email': fields.String(required=True, attribute='contact.email'),
        'person': fields.String(required=True, attribute='person.full_name')
    }
)

company_fields = company_api.model(
    'Company',
    {
        'id': fields.Integer(),
        'name': fields.String(
            required=True,
            description="Company name",
            example="test_company"),
        'address': fields.Nested(address_fields),
        'tech_person': fields.Nested(contact_people_fields),
        'legal_person': fields.Nested(contact_people_fields),
        'date_created': fields.DateTime(
            required=False,
            attribute='date_created'),
        'date_modified': fields.DateTime(
            required=False,
            attribute='date_modified'),
    }
)

single_company_fields = company_api.model(
    'Single Company',
    {
        'company': fields.Nested(company_fields),
        'numbering': fields.Nested(numbering_fields),
        'postal': fields.Nested(postal_fields),
        'spectrum': fields.Nested(spectrum_fields),
        'telecom': fields.Nested(telecom_fields),
        'typeapproval': fields.Nested(typeapproval_fields),
    }
)


@company_api.route('', endpoint='company')
class CompaniesEndPoint(Resource):

    @company_api.response(200, 'Successful Retrieval of companies')
    @company_api.response(200, 'No companies found')
    def get(self):
        ''' Retrieve companies'''
        search_term = request.args.get('q') or None
        limit = request.args.get('limit') or Config.MAX_PAGE_SIZE
        page_limit = 100 if int(limit) > 100 else int(limit)
        page = request.args.get('page') or 1

        if page_limit < 1 or page < 1:
            return abort(400, 'Page or Limit cannot be negative values')

        company_data = Company.query.filter_by(active=True).\
            order_by(desc(Company.date_created))
        if company_data.all():
            companies = company_data

            if search_term:
                companies = company_data.filter(
                    Company.name.ilike('%'+search_term+'%')
                )

            company_paged = companies.paginate(
                page=page, per_page=page_limit, error_out=True
            )
            results = dict(data=marshal(company_paged.items, company_fields))

            pages = {
                'page': page, 'per_page': page_limit,
                'total_data': company_paged.total, 'pages': company_paged.pages
            }

            if page == 1:
                pages['prev_page'] = url_for('api.company') + \
                    '?limit={}'.format(page_limit)

            if page > 1:
                pages['prev_page'] = url_for('api.company') + \
                    '?limit={}&page={}'.format(page_limit, page-1)

            if page < company_paged.pages:
                pages['next_page'] = url_for('api.company') + \
                    '?limit={}&page={}'.format(page_limit, page+1)

            results.update(pages)
            return results, 200
        return abort(404, message='No companies found for specified user')

    @company_api.response(201, 'Company created successfully!')
    @company_api.response(409, 'Company already exists!')
    @company_api.response(500, 'Internal Server Error')
    @company_api.doc(model='Company', body=company_fields)
    def post(self):
        ''' Create a company '''
        arguments = request.get_json(force=True)
        name = arguments.get('name').strip()
        district = arguments.get('district').strip() or None
        postal = arguments.get('postal').strip() or None
        country = arguments.get('country').strip() or None
        tech_person_name_string = arguments.get(
            'techPersonName').strip() or None
        tech_person_email = arguments.get('techPersonEmail').strip() or None
        address_line_1 = arguments.get('address1').strip() or None
        address_line_2 = arguments.get('address2').strip() or None
        legal_person_name_str = arguments.get(
            'legalPersonName').strip() or None
        legal_person_email = arguments.get('legalPersonEmail').strip() or None
        tech_person_name = tech_person_name_string.split()
        legal_person_name = legal_person_name_str.split()

        if not name:
            return abort(400, 'Name cannot be empty!')
        try:
            address = Address(
                district=district,
                postal_code=postal,
                country=country,
                address_line_1=address_line_1,
                address_line_2=address_line_2
                )
            tech_person = Person(tech_person_name[0], tech_person_name[-1])
            legal_person = Person(legal_person_name[0], legal_person_name[-1])
            tech_contact = Contact(email=tech_person_email)
            legal_contact = Contact(email=legal_person_email)

            if not address.save_address():
                address = Address.query.filter_by(
                    address_line_1=address.address_line_1,
                    active=True).first()
            if not tech_person.save_person():
                tech_person = Person.query.filter_by(
                    full_name=tech_person_name_string).first()
            if not legal_person.save_person():
                legal_person = Person.query.filter_by(
                    full_name=legal_person_name_str).first()
            if not tech_contact.save_contact():
                tech_contact = Contact.query.filter_by(
                    email=tech_person_email).first()
            if not legal_contact.save_contact():
                legal_contact = Contact.query.filter_by(
                    email=legal_person_email).first()
            tech_contact_person = ContactPerson(
                person=tech_person,
                contact=tech_contact)
            legal_contact_person = ContactPerson(
                person=legal_person,
                contact=legal_contact)
            if not tech_contact_person.save_contact_person():
                tech_contact_person = ContactPerson.query.filter_by(
                    person=tech_person,
                    contact=tech_contact).first()
            if not legal_contact_person.save_contact_person():
                legal_contact_person = ContactPerson.query.filter_by(
                    person=legal_person,
                    contact=legal_contact).first()

            company = Company(
                name=name,
                address=address,
                legal_person=legal_contact_person,
                tech_person=tech_contact_person
                )
            if company.save_company():
                return {'message': 'Company created successfully!'}, 201
            return abort(409, message='Company already exists!')
        except Exception as e:
            abort(400, message='Failed to create new company -> {}'.format(e))


@company_api.route('/<int:company_id>', endpoint='single_company')
class SingleCompanyEndpoint(Resource):

    # @company_api.header('x-access-token', 'Access Token', required=True)
    @marshal_with(single_company_fields)
    @company_api.response(200, 'Successful retrieval of company')
    @company_api.response(400, 'No company found with specified ID')
    def get(self, company_id):
        ''' Retrieve individual company with given company_id '''
        company = Company.query.filter_by(
            id=company_id, active=True).first()
        data = {}
        if company:
            data['company'] = company
        numbering = Numbering.query.filter_by(
            service_provider=company, active=True).\
            order_by(desc(Numbering.date_created))
        if numbering.all():
            data['numbering'] = numbering
        spectrum = Spectrum.query.filter_by(
            applicant=company, active=True).\
            order_by(desc(Spectrum.date_created))
        if spectrum.all():
            data['spectrum'] = spectrum
        postal = Postal.query.filter_by(
            company=company, active=True).\
            order_by(desc(Postal.date_created))
        if postal.all():
            data['postal'] = postal
        telecom = Telecom.query.filter_by(
            company=company, active=True).\
            order_by(desc(Telecom.date_created))
        if telecom.all():
            data['telecom'] = telecom
        typeapproval = Typeapproval.query.filter_by(
            applicant=company, active=True).\
            order_by(desc(Typeapproval.date_created))
        if typeapproval.all():
            data['typeapproval'] = typeapproval
        return data, 200
        abort(404, message='No company found with specified ID')

    # @company_api.header('x-access-token', 'Access Token', required=True)
    @company_api.response(200, 'Successfully Updated Company')
    @company_api.response(400, 'Company with id {} not found or not yours.')
    @company_api.marshal_with(company_fields)
    def put(self, company_id):
        ''' Update company with given company_id '''
        arguments = request.get_json(force=True)
        name = arguments.get('name').strip()
        company = Company.query.filter_by(
            id=company_id, active=True).first()
        if company:
            if name:
                company.name = name
            company.save()
            return company, 200
        else:
            abort(
                404,
                message='Company with id {} not found'.format(company_id))

    @company_api.header('x-access-token', 'Access Token', required=True)
    @auth.login_required
    @company_api.response(200, 'Company with id {} successfully deleted.')
    @company_api.response(400, 'Company with id {} not found or not yours.')
    def delete(self, company_id):
        ''' Delete company with company_id as given '''
        company = Company.query.filter_by(
            id=company_id, active=True).first()
        if company:
            if company.delete_company():
                response = {
                    'message': 'Company with id {} deleted.'.format(company_id)
                }
            return response, 200
        else:
            abort(
                404,
                message='Company with id {} not found.'.format(company_id)
            )
