from app.models.baseModel import BaseModel, db
from sqlalchemy.orm import relationship
from app.models.person import Person
from app.models.contact import Contact


class ContactPerson(BaseModel):
    '''This class represents the company model'''

    __table__name = 'contact_person'

    person_id = db.Column(db.Integer,
                              db.ForeignKey('person.id'), nullable=False)
    # does not cascade
    contact_id = db.Column(db.Integer,
                              db.ForeignKey('contact.id'), nullable=False)

    person = relationship('Person', foreign_keys=[person_id])
    contact = relationship('Contact', foreign_keys=[contact_id])

    def save_contact_person(self):
        if not self.exists():
            self.save()
            return True
        return False

    def delete_contact_person(self, deep_delete=False):
        if not deep_delete:
            if self.deactivate():
                return True
            return False
        if self.exists():
            self.delete()
            return True
        return False
