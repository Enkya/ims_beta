from app.models.baseModel import BaseModel, db


class Employee(BaseModel):
    '''This class represents the company model'''

    __table__name = 'employee'

    person_id = db.Column(db.String(255), nullable=False, unique=True)
    contact_id = db.Column(db.String(120))
    department_id = db.Column(db.Integer)


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
