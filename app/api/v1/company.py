from flask import request, jsonify, g, url_for
from flask_restplus import abort, Resource, fields, Namespace, marshal_with
from flask_restplus import marshal
from sqlalchemy import desc
from app.models.company import Company
from app.models.user import User
from app.utils.utilities import auth
from instance.config import Config


company_api = Namespace(
    'companies', description='A company creation namespace')

company_fields = company_api.model(
    'Company',
    {
        'id': fields.Integer(),
        'name': fields.String(
            required=True,
            description="Company name",
            example="test_company"),
        'location': fields.String(required=False, attribute='location'),
        'postal': fields.String(required=False, attribute='postal'),
        'country': fields.String(required=False, attribute='country'),
        'tech_person_name': fields.String(required=False, attribute='tech_person_name'),
        'tech_person_email': fields.String(required=False, attribute='tech_person_email'),
        'address_line_1': fields.String(required=False, attribute='address_line_1'),
        'address_line_2': fields.String(required=False, attribute='address_line_2'),
        'legal_person_name': fields.String(required=False, attribute='legal_person_name'),
        'legal_person_email': fields.String(required=False, attribute='legal_person_email'),
        'date_created': fields.DateTime(required=False, attribute='date_created'),
        'date_modified': fields.DateTime(required=False, attribute='date_modified'),
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
                pages['prev_page'] = url_for('api.company')+'?limit={}'.format(page_limit)

            if page > 1:
                pages['prev_page'] = url_for('api.company')+'?limit={}&page={}'.format(page_limit, page-1)

            if page < company_paged.pages:
                pages['next_page'] = url_for('api.company')+'?limit={}&page={}'.format(page_limit, page+1)

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
        location = arguments.get('district').strip()
        postal = int(arguments.get('postal').strip())
        country = arguments.get('country').strip()
        tech_person_name = arguments.get('techPersonName').strip()
        tech_person_email = arguments.get('techPersonEmail').strip()
        address_line_1 = arguments.get('address1').strip()
        address_line_2 = arguments.get('address1').strip()
        legal_person_name = arguments.get('legalPersonName').strip()
        legal_person_email = arguments.get('legalPersonEmail').strip()

        if not name:
            return abort(400, 'Name cannot be empty!')
        try:
            company = Company(
                name=name,
                location=location,
                postal=postal,
                country=country,
                tech_person_name=tech_person_name,
                tech_person_email=tech_person_email,
                address_line_1=address_line_1,
                address_line_2=address_line_2,
                legal_person_name=legal_person_name,
                legal_person_email=legal_person_email
                )
            if company.save_company():
                return {'message': 'Company created successfully!'}, 201
            return abort(409, message='Company already exists!')
        except Exception as e:
            abort(400, message='Failed to create new company -> {}'.format(e.message))


@company_api.route('/<int:company_id>', endpoint='single_company')
class SingleCompanyEndpoint(Resource):

    @company_api.header('x-access-token', 'Access Token', required=True)
    @marshal_with(company_fields)
    @company_api.response(200, 'Successful retrieval of company')
    @company_api.response(400, 'No company found with specified ID')
    def get(self, company_id):
        ''' Retrieve individual company with given company_id '''
        company = Company.query.filter_by(
            id=company_id, active=True).first()
        if company:
            return company, 200
        abort(404, message='No company found with specified ID')

    @company_api.header('x-access-token', 'Access Token', required=True)
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
            abort(404, message='Company with id {} not found or not yours.'.format(
                company_id))

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
                    'message': 'Company with id {} successfully deleted.'.format(company_id)}
            return response, 200
        else:
            abort(404, message='Company with id {} not found or not yours.'.format(
                company_id))
