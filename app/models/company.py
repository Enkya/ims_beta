from app.models.baseModel import BaseModel, db
from app.models.address import Address
from app.models.contact_person import ContactPerson
from sqlalchemy.orm import relationship

class Company(BaseModel):
    '''This class represents the company model'''

    __table__name = 'company'

    name = db.Column(db.String(255), nullable=False, unique=True)
    address_id = db.Column(db.Integer, db.ForeignKey("address.id"))
    legal_person_id = db.Column(db.Integer, db.ForeignKey('contact_person.id'))
    tech_person_id = db.Column(db.Integer, db.ForeignKey('contact_person.id'))
    
    address = relationship("Address", foreign_keys=[address_id])
    legal_person = relationship('ContactPerson', foreign_keys=[legal_person_id])
    tech_person = relationship('ContactPerson', foreign_keys=[tech_person_id])

    def save_company(self):
        ''' Method to save company '''
        if not self.exists():
            self.save()
            return True
        return False

    def delete_company(self, deep_delete=False):
        ''' Method to delete company '''
        if not deep_delete:
            if self.deactivate():
                return True
            return False
        if self.exists():
            self.delete()
            return True
        return False

    def exists(self):
        ''' Check if company exists '''
        return True if Company.query.filter_by(name=self.name).first() else False

    def __repr__(self):
        return "<Company: {}>".format(self.name)

    def __str__(self):
        return '{0}'.format(self.name)
