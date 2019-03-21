from app.models.baseModel import BaseModel, db
from sqlalchemy.orm import relationship
from app.models.contact_person import ContactPerson
from app.models.department import Department

class Employee(BaseModel):
    '''This class represents the company model'''

    __tablename__ = 'employee'

    contact_person_id = db.Column(db.Integer, db.ForeignKey('contact_person.id'))
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    
    contact_person = relationship("ContactPerson", foreign_keys=[contact_person_id])
    department = relationship('Department', foreign_keys=[department_id])


    def save_employee(self):
        ''' Method to save employee '''
        if not self.exists():
            self.save()
            return True
        return False

    def delete_employee(self, deep_delete=False):
        ''' Method to delete employee '''
        if not deep_delete:
            if self.deactivate():
                return True
            return False
        if self.exists():
            self.delete()
            return True
        return False

    def exists(self):
        ''' Check if employee exists '''
        return True if Employee.query.filter_by(contact_person=self.contact_person).first() else False
