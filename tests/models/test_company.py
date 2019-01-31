from datetime import datetime

from tests.base_test import BaseCase
from app.models.user import User
from app.models.company import Company


class TestCompanyModel(BaseCase):

    def setUp(self):
        super(TestCompanyModel, self).setUp()

    def Company_inserted_in_db(self):
        with self.app.app_context():
            company = Company.query.filter_by(id=1, active=True).first()
        self.assertEqual(company.name, "Company", "Name not added")
        self.assertTrue(isinstance(company.date_created, datetime))
        self.assertTrue(isinstance(company.date_modified, datetime))

    def test_add_company(self):
        company = Company(name='Go hard or go home')
        check = company.save_company()
        self.assertTrue(check, "Company should be added")

    def test_delete_company(self):
        with self.app.app_context():
            company = Company.query.filter_by(
                name="sample_1", active=True).first()
        self.assertTrue(isinstance(company, Company))
        with self.app.app_context():
            company.delete_company()
            verify_company = Company.query.filter_by(
                name="sample_1", active=True).first()
        self.assertFalse(
            verify_company,
            "Company that is deleted should not be returned"
        )

    def test_deep_delete_company_deletes_from_db(self):
        with self.app.app_context():
            company = Company.query.filter_by(
                name="sample_1", active=True).first()
        self.assertTrue(isinstance(company, Company))
        with self.app.app_context():
            company.delete_company(True)
            verify_company = Company.query.filter_by(
                name="sample_1").first()
        self.assertFalse(
            verify_company,
            "Company that is deleted should not exist in the database"
        )

    def Company_item_list(self):
        with self.app.app_context():
            company = Company.query.filter_by(name="sample_1", active=True).first()
        self.assertTrue(isinstance(company.company_items, list))
