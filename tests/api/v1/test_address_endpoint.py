import json

from tests.base_test import BaseCase
from app.models.address import Address


class TestAddressEndpoint(BaseCase):
    ''' A class to test the Address endpoint '''
    def setUp(self):
        super(TestAddressEndpoint, self).setUp()
        self.address_data = {
            "district": "Lugogo",
            "postal": "2787",
            "country": "Uganda",
            "address1": "129W 29th Street NY 10001",
            "address2": "4F"
        }

    def test_post_addresses_adds_new_address(self):
        with self.app.app_context():
            response = self.client().post(
                '/api/v1/addresses',
                data=json.dumps(self.address_data),
                headers=self.auth_headers())
        self.assertEqual(response.status_code, 201)
        self.assertEqual('Address created successfully!',
                         json.loads(response.data.decode('utf-8')).get('message'))

    def test_get_returns_all_addresses(self):
        with self.app.app_context():
            response = self.client().get('/api/v1/addresses',
                                         headers=self.auth_headers())
            result = response.data.decode('utf-8')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(result)), 6)

    def test_get_returns_one_address_if_id_is_specified(self):
        with self.app.app_context():
            response = self.client().get('/api/v1/addresses/1',
                                         headers=self.auth_headers())
        result = json.loads(response.data.decode('utf-8'))
        expected_list = sorted(
            [
                'id',
                'district',
                'postal_code',
                'country',
                'address_line_1',
                'address_line_2',
                'date_created',
                'date_modified'
            ])
        self.assertEqual(response.status_code, 200)
        self.assertListEqual([result.get('district')], ['KLA'])

    def test_edit_updates_address_fields(self):
        with self.app.app_context():
            response = self.client().get('/api/v1/addresses/1',
                                         headers=self.auth_headers())
        result = json.loads(response.data.decode('utf-8'))

        self.assertEqual(result.get('address_line_1'), 'Plot 103 Kira Road')

        update_fields = {'address1': 'Plot 103 Kira Road, Kamwokya'}
        with self.app.app_context():
            response = self.client().put('/api/v1/addresses/1',
                                         data=json.dumps(update_fields),
                                         headers=self.auth_headers())
        result = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(result.get('address_line_1'), update_fields.get('address1'))

    def test_delete_removes_address_from_database(self):
        with self.app.app_context():

            self.assertEqual(len(Address.query.filter_by(active=True).all()), 2)

            response = self.client().delete('/api/v1/addresses/1',
                                            headers=self.auth_headers())
        result = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(result.get('message'), 'Address with id 1 successfully deleted.')
        with self.app.app_context():
            self.assertEqual(len(Address.query.filter_by(active=True).all()), 1)

    def test_search_returns_addresses_whose_address_includes_the_search_term(self):
        with self.app.app_context():
            response = self.client().get('/api/v1/addresses?q=TRM Drive',
                                         headers=self.auth_headers())
        result = json.loads(response.data.decode('utf-8')).get('data')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(result), 1)

    def test_pagination_of_addresses_when_you_pass_a_limit_parameter(self):
        with self.app.app_context():
            response = self.client().get('/api/v1/addresses?limit=1',
                                         headers=self.auth_headers())
        result = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        expected_result = sorted(['data', 'next_page','page', 'per_page', 'total_data', 'pages', 'prev_page'])
        self.assertListEqual(sorted(result.keys()), expected_result)
        self.assertEqual(len(result.get('data')), 1)
