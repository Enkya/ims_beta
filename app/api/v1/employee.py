
from flask import request, jsonify, g, url_for
from flask_restplus import abort, Resource, fields, Namespace, marshal_with
from flask_restplus import marshal
from sqlalchemy import desc
from app.models.employee import Employee
from app.models.address import Address
from app.models.person import Person
from app.models.contact import Contact
from app.models.contact_person import ContactPerson
from app.models.department import Department
from app.models.user import User
from app.utils.utilities import auth
from instance.config import Config


employee_api = Namespace(
    'employees', description='A employee creation namespace')

employee_fields = employee_api.model(
    'Employee',
    {
        'id': fields.Integer(),
        'name': fields.String(
            required=True, attribute='contact_person.person.full_name'),
        'email': fields.String(
            required=True, attribute='contact_person.contact.email'),
        'department': fields.String(
            required=True, attribute='department.name'),
        'permissions': fields.String(
            required=True, attribute='department.permissions'),
        'date_created': fields.DateTime(
            required=False,
            attribute='date_created'),
        'date_modified': fields.DateTime(
            required=False,
            attribute='date_modified'),
    }
)


@employee_api.route('', endpoint='employee')
class EmployeesEndPoint(Resource):

    @employee_api.response(200, 'Successful Retrieval of employees')
    @employee_api.response(200, 'No employees found')
    def get(self):
        ''' Retrieve employees'''
        search_term = request.args.get('q') or None
        limit = request.args.get('limit') or Config.MAX_PAGE_SIZE
        page_limit = 100 if int(limit) > 100 else int(limit)
        page = request.args.get('page') or 1

        if page_limit < 1 or page < 1:
            return abort(400, 'Page or Limit cannot be negative values')

        employee_data = Employee.query.filter_by(active=True).\
            order_by(desc(Employee.date_created))
        if employee_data.all():
            employees = employee_data

            if search_term:
                employees = employee_data.filter(
                    Employee.name.ilike('%'+search_term+'%')
                )

            employee_paged = employees.paginate(
                page=page, per_page=page_limit, error_out=True
            )
            results = dict(data=marshal(employee_paged.items, employee_fields))

            pages = {
                'page': page,
                'per_page': page_limit,
                'total_data': employee_paged.total,
                'pages': employee_paged.pages
            }

            if page == 1:
                pages['prev_page'] = url_for('api.employee') + \
                    '?limit={}'.format(page_limit)

            if page > 1:
                pages['prev_page'] = url_for('api.employee') + \
                    '?limit={}&page={}'.format(page_limit, page-1)

            if page < employee_paged.pages:
                pages['next_page'] = url_for('api.employee') + \
                    '?limit={}&page={}'.format(page_limit, page+1)

            results.update(pages)
            return results, 200
        return abort(404, message='No employees found for specified user')

    @employee_api.response(201, 'Employee created successfully!')
    @employee_api.response(409, 'Employee already exists!')
    @employee_api.response(500, 'Internal Server Error')
    @employee_api.doc(model='Employee', body=employee_fields)
    def post(self):
        ''' Create a employee '''
        arguments = request.get_json(force=True)
        first_name = arguments.get('firstName').strip()
        last_name = arguments.get('lastName').strip()
        department = arguments.get('department').strip() or None
        tel_one = arguments.get('telOne').strip() or None
        tel_two = arguments.get('telTwo').strip() or None
        email = arguments.get('email').strip() or None
        role = arguments.get('role').strip() or None

        if not last_name:
            return abort(400, 'Name cannot be empty!')
        try:
            person = Person(first_name, last_name)
            contact = Contact(email=email, tel_one=tel_one, tel_two=tel_two)
            department = Department.query.filter_by(id=int(department)).first()

            if not person.save_person():
                person = Person.query.filter_by(
                    full_name=(first_name+' '+last_name)).first()
            if not contact.save_contact():
                contact = Contact.query.filter_by(
                    email=email).first()
            contact_person = ContactPerson(
                person=person,
                contact=contact)
            if not contact_person.save_contact_person():
                contact_person = ContactPerson.query.filter_by(
                    person=person,
                    contact=contact).first()

            employee = Employee(
                contact_person=contact_person,
                department=department
                )
            if employee.save_employee():
                return {'message': 'Employee created successfully!'}, 201
            return abort(409, message='Employee already exists!')
        except Exception as e:
            abort(400, message='Failed to create new employee -> {}'.format(e))


@employee_api.route('/<int:employee_id>', endpoint='single_employee')
class SingleEmployeeEndpoint(Resource):

    # @employee_api.header('x-access-token', 'Access Token', required=True)
    @marshal_with(employee_fields)
    @employee_api.response(200, 'Successful retrieval of employee')
    @employee_api.response(400, 'No employee found with specified ID')
    def get(self, employee_id):
        ''' Retrieve individual employee with given employee_id '''
        employee = Employee.query.filter_by(
            id=employee_id, active=True).first()
        if employee:
            return employee, 200
        abort(404, message='No employee found with specified ID')

    # @employee_api.header('x-access-token', 'Access Token', required=True)
    @employee_api.response(200, 'Successfully Updated Employee')
    @employee_api.response(400, 'Employee with id {} not found or not yours.')
    @employee_api.marshal_with(employee_fields)
    def put(self, employee_id):
        ''' Update employee with given employee_id '''
        arguments = request.get_json(force=True)
        name = arguments.get('name').strip()
        employee = Employee.query.filter_by(
            id=employee_id, active=True).first()
        if employee:
            if name:
                employee.name = name
            employee.save()
            return employee, 200
        else:
            abort(
                404,
                message='Employee with id {} not found'.format(employee_id))

    # @employee_api.header('x-access-token', 'Access Token', required=True)
    @auth.login_required
    @employee_api.response(200, 'Employee with id {} successfully deleted.')
    @employee_api.response(400, 'Employee with id {} not found or not yours.')
    def delete(self, employee_id):
        ''' Delete employee with employee_id as given '''
        employee = Employee.query.filter_by(
            id=employee_id, active=True).first()
        if employee:
            if employee.delete_employee():
                response = {
                    'message': 'Employee with id {} deleted.'.format(
                        employee_id)
                }
            return response, 200
        else:
            abort(
                404,
                message='Employee with id {} not found.'.format(employee_id)
            )
