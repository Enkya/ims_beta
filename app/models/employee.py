from app.models.baseModel import BaseModel, db
from sqlalchemy.orm import relationship

class Employee(BaseModel):
    '''This class represents the company model'''

    __table__name = 'employee'

    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'))
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    
    person = relationship("Person", foreign_keys=[person_id])
    contact = relationship('Contact', foreign_keys=[contact_id])
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
        return True if Employee.query.filter_by(person_id=self.person_id).first() else False
