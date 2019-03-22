from app.models.baseModel import BaseModel, db
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method


class Person(BaseModel):
    '''This class represents the person model'''

    __table__name = 'person'

    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255), nullable=False)

    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name

    @hybrid_property
    def full_name(self):
        return self.first_name + ' ' + self.last_name

    def save_person(self):
        ''' Method to save person '''
        if not self.exists():
            self.save()
            return True
        return False

    def exists(self):
        ''' Check if person exists '''
        return True if Person.query.filter_by(
            full_name=self.full_name).first() else False

    def __repr__(self):
        return "<Person: {}>".format(self.full_name)

    def __str__(self):
        return '{0}'.format(self.full_name)
