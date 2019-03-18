import unittest
import json

from app import create_app
from app.models.baseModel import db
from app.models.user import User
from app.models.company import Company
from app.models.address import Address
from app.models.person import Person


class BaseCase(unittest.TestCase):
    ''' A class detailing the base properties to be inherited '''
    @staticmethod
    def create_new_app():
        return create_app(config_name='testing')

    def setUp(self):
        super(BaseCase, self).setUp()
        self.app = self.create_new_app()
        self.client = self.app.test_client
        self._password = 'test'

        self.company_data = {'name': 'Go fishing'}

        with self.app.app_context():
            db.session.close()
            db.drop_all()
            db.create_all()
            
            self.user_1 = User(
                first_name='Ezekiel',
                last_name='Mugaya',
                email='emugaya@andela.com',
                password=self._password
            )
            self.user_2 = User(
                first_name='Paul',
                last_name='Nyondo',
                email='pnyondo@andela.com',
                password=self._password
            )
            self.populate_db()

    def populate_db(self):
        self.add_test_users()
        self.add_test_addresses()
        self.add_test_people()
        self.add_test_companies()

    def add_test_users(self):
        ''' method to add test users to db '''
        self.user_1.save_user()
        self.user_2.save_user()

    @staticmethod
    def add_test_addresses():
        ''' method to add test addresses to db '''
        address_1 = Address(district='KLA', postal_code=45, country='UG', address_line_1='Plot 103 Kira Road')
        address_2 = Address(district='NBO', postal_code=7245, country='KE', address_line_1 = 'TRM Drive Roysambu')
        address_1.save(), address_2.save()

    @staticmethod
    def add_test_people():
        ''' method to add test people to db '''
        person_1 = Person(first_name='John', last_name='Smith')
        person_2 = Person(first_name='Bjorn', last_name='Smit')
        person_1.save(), person_2.save()

    def add_test_companies(self):
        ''' method to add test companies to db '''
        with self.app.app_context():
            self.address_1 = Address.query.filter_by(id=1, active=True).first()
            self.address_2 = Address.query.filter_by(id=2, active=True).first()
            self.legal_person = Person.query.filter_by(id=1, active=True).first()
            self.tech_person = Person.query.filter_by(id=2, active=True).first()
        company_1 = Company(name='sample_1', address=self.address_1, legal_person=self.legal_person)
        company_2 = Company(name='sample_2', address=self.address_2, tech_person=self.tech_person)
        company_1.save(), company_2.save()

    def auth_headers(self, email='emugaya@andela.com', password='test'):
        ''' method generates auth headers for test user '''
        path = '/api/v1/auth/login'
        data = {'email': email, 'password': password}
        response = self.post_data(path, data)
        result = json.loads(response.data.decode('utf-8'))
        self.assertTrue(result['token'])
        return {'x-access-token': result['token']}


    def post_data(self, path, data):
        ''' method to pass data to API path given '''
        return self.client().post(
            path,
            data=json.dumps(data),
            content_type='application/json'
        )

    def tearDown(self):
        super(BaseCase, self).tearDown()
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
