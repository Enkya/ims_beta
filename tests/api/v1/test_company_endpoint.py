import json

from tests.base_test import BaseCase
from app.models.company import Company


class TestCompanyEndpoint(BaseCase):
    ''' A class to test the company endpoints '''
    def setUp(self):
        super(TestCompanyEndpoint, self).setUp()
        self.company_data = {
            "name": "MOVERS",
            "district": "Lugogo",
            "postal": "2787",
            "country": "Uganda",
            "techPersonName": "test",
            "techPersonEmail": "test@gmail.com",
            "address1": "Ggombe B, Wakiso",
            "address2": "",
            "legalPersonName": "Bruce Bigirwenkya",
            "legalPersonEmail": "test@gmail.com"
        }

    def test_post_companies_adds_new_company(self):
        with self.app.app_context():
            response = self.client().post(
                '/api/v1/companies',
                data=json.dumps(self.company_data),
                headers=self.auth_headers())
        self.assertEqual(response.status_code, 201)
        self.assertEqual('Company created successfully!',
                         json.loads(response.data.decode('utf-8')).get('message'))

    def test_get_returns_all_companies_for_user(self):
        with self.app.app_context():
            response = self.client().get('/api/v1/companies',
                                         headers=self.auth_headers())
            result = response.data.decode('utf-8')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(result)), 6)

    def test_get_returns_one_company_if_id_is_specified(self):
        with self.app.app_context():
            response = self.client().get('/api/v1/companies/1',
                                         headers=self.auth_headers())
        result = json.loads(response.data.decode('utf-8'))
        expected_list = sorted(['id', 'name', 'date_created', 'date_modified'])
        self.assertEqual(response.status_code, 200)
        self.assertListEqual([result.get('name')], ['sample_1'])

    def test_edit_updates_company_fields(self):
        with self.app.app_context():
            response = self.client().get('/api/v1/companies/1',
                                         headers=self.auth_headers())
        result = json.loads(response.data.decode('utf-8'))

        self.assertEqual(result.get('name'), 'sample_1')

        update_fields = {'name': 'Bungee Jump'}
        with self.app.app_context():
            response = self.client().put('/api/v1/companies/1',
                                         data=json.dumps(update_fields),
                                         headers=self.auth_headers())
        result = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(result.get('name'), update_fields.get('name'))

    def test_delete_removes_company_from_database(self):
        with self.app.app_context():

            self.assertEqual(len(Company.query.filter_by(active=True).all()), 2)

            response = self.client().delete('/api/v1/companies/1',
                                            headers=self.auth_headers())
        result = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(result.get('message'), 'Company with id 1 successfully deleted.')
        with self.app.app_context():
            self.assertEqual(len(Company.query.filter_by(active=True).all()), 1)

    def test_search_returns_companies_whose_name_matches_a_search_term(self):
        with self.app.app_context():
            response = self.client().get('/api/v1/companies?q=sample',
                                         headers=self.auth_headers())
        result = json.loads(response.data.decode('utf-8')).get('data')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(result), 2)

    def test_pagination_of_companies_when_you_pass_a_limit_parameter(self):
        with self.app.app_context():
            response = self.client().get('/api/v1/companies?limit=1',
                                         headers=self.auth_headers())
        result = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        expected_result = sorted(['data', 'next_page','page', 'per_page', 'total_data', 'pages', 'prev_page'])
        self.assertListEqual(sorted(result.keys()), expected_result)
        self.assertEqual(len(result.get('data')), 1)