from flask import request, jsonify, g, url_for
from flask_restplus import abort, Resource, fields, Namespace, marshal_with
from flask_restplus import marshal
from sqlalchemy import desc
from app.models.department import Department
from app.utils.utilities import auth
from instance.config import Config


department_api = Namespace(
    'departments', description='An department creation namespace')

department_fields = department_api.model(
    'Department',
    {
        'id': fields.Integer(),
        'name': fields.String(
            required=False,
            description="Department name",
            example="ECI"),
        'description': fields.String(required=False, attribute='description'),
        'size': fields.Integer(required=False, attribute='size'),
        'permissions': fields.String(required=False, attribute='permissions'),
        'date_created': fields.DateTime(
            required=False,
            attribute='date_created'),
        'date_modified': fields.DateTime(
            required=False,
            attribute='date_modified'),
    }
)


@department_api.route('', endpoint='department')
class DepartmentsEndPoint(Resource):

    @department_api.response(200, 'Successful Retrieval of departments')
    @department_api.response(200, 'No departments found')
    def get(self):
        ''' Retrieve departments'''
        search_term = request.args.get('q') or None
        limit = request.args.get('limit') or Config.MAX_PAGE_SIZE
        page_limit = 100 if int(limit) > 100 else int(limit)
        page = request.args.get('page') or 1

        if page_limit < 1 or page < 1:
            return abort(400, 'Page or Limit cannot be negative values')

        department_data = Department.query.filter_by(active=True).\
            order_by(desc(Department.date_created))
        if department_data.all():
            departments = department_data

            if search_term:
                departments = department_data.filter(
                    Department.department_line_1.ilike('%'+search_term+'%')
                )

            department_paged = departments.paginate(
                page=page, per_page=page_limit, error_out=True
            )
            results = dict(
                data=marshal(department_paged.items, department_fields)
            )

            pages = {
                'page': page, 'per_page': page_limit,
                'total_data': department_paged.total,
                'pages': department_paged.pages
            }

            if page == 1:
                pages['prev_page'] = url_for('api.department') + \
                    '?limit={}'.format(page_limit)

            if page > 1:
                pages['prev_page'] = url_for('api.department') + \
                    '?limit={}&page={}'.format(page_limit, page-1)

            if page < department_paged.pages:
                pages['next_page'] = url_for('api.department') + \
                    '?limit={}&page={}'.format(page_limit, page+1)

            results.update(pages)
            return results, 200
        return abort(404, message='No departments found for specified user')

    @department_api.response(201, 'Department created successfully!')
    @department_api.response(409, 'Department already exists!')
    @department_api.response(500, 'Internal Server Error')
    @department_api.doc(model='Department', body=department_fields)
    def post(self):
        ''' Create an department '''
        arguments = request.get_json(force=True)
        name = arguments.get('name').strip()
        description = arguments.get('description').strip() or None
        size = arguments.get('size').strip()
        size = int(size, 10)
        permissions = arguments.get('permissions').strip() or None

        if not name:
            return abort(400, 'Name cannot be empty!')
        try:
            department = Department(
                name=name,
                description=description,
                size=size,
                permissions=permissions
                )
            if department.save_department():
                return {'message': 'Department created successfully!'}, 201
            return abort(409, message='Department already exists!')
        except Exception as e:
            abort(
                400,
                message='Failed to create new department -> {}'.format(e)
            )


@department_api.route('/<int:department_id>', endpoint='single_department')
class SingleDepartmentEndpoint(Resource):

    @department_api.header('x-access-token', 'Access Token', required=True)
    @marshal_with(department_fields)
    @department_api.response(200, 'Successful retrieval of department')
    @department_api.response(400, 'No department found with specified ID')
    def get(self, department_id):
        ''' Retrieve individual department with given department_id '''
        department = Department.query.filter_by(
            id=department_id, active=True).first()
        if department:
            return department, 200
        abort(404, message='No department found with specified ID')

    @department_api.header('x-access-token', 'Access Token', required=True)
    @department_api.response(200, 'Successfully Updated Department')
    @department_api.response(400, 'Department with id {} not found.')
    @department_api.marshal_with(department_fields)
    def put(self, department_id):
        ''' Update department with given department_id '''
        arguments = request.get_json(force=True)
        permissions = arguments.get('permissions').strip()
        department = Department.query.filter_by(
            id=department_id, active=True).first()
        if department:
            if permissions:
                department.permissions = permissions
            department.save()
            return department, 200
        else:
            abort(
                404,
                message='Department with id {} not found'.format(department_id)
            )

    @department_api.header('x-access-token', 'Access Token', required=True)
    @auth.login_required
    @department_api.response(200, 'Department with id {} successfully deleted')
    @department_api.response(400, 'Department with id {} not found')
    def delete(self, department_id):
        ''' Delete department with department_id as given '''
        department = Department.query.filter_by(
            id=department_id, active=True).first()
        if department:
            if department.delete_department():
                response = {
                    'message': 'Department with id {} deleted'.format(
                        department_id)
                }
            return response, 200
        else:
            abort(
                404,
                message='Department with id {} not found or not yours.'.format(
                    department_id)
            )
