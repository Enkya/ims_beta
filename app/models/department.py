from app.models.baseModel import BaseModel, db
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method


class Department(BaseModel):
    '''This class represents the department model'''

    __tablename__ = 'department'

    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    size = db.Column(db.Integer)
    permissions = db.Column(db.String(255))

    def save_department(self):
        ''' Method to save contact '''
        if not self.exists():
            self.save()
            return True
        return False

    def exists(self):
        ''' Check if department exists '''
        return True if Department.query.filter_by(
            name=self.name).first() else False
