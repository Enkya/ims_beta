from app.models.baseModel import BaseModel, db
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method


class Contact(BaseModel):
    '''This class represents the contact model'''

    __tablename__ = 'contact'

    tel_one = db.Column(db.String(255))
    tel_two = db.Column(db.String(255))
    email = db.Column(db.String(255))
    social_media_handle = db.Column(db.String(255))
    website = db.Column(db.String(255))
    
    def save_contact(self):
        ''' Method to save contact '''
        if not self.exists():
            self.save()
            return True
        return False

    def exists(self):
        ''' Check if contact exists '''
        return True if Contact.query.filter_by(email=self.email).first() else False

