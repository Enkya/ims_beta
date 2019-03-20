from app.models.baseModel import BaseModel, db
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method


class Address(BaseModel):
    '''This class represents the Address model'''

    __table__name = 'address'

    district = db.Column(db.String(255))
    postal_code = db.Column(db.String(255))
    country = db.Column(db.String(255))
    address_line_1 = db.Column(db.String(255))
    address_line_2 = db.Column(db.String(255))
    
    def save_address(self):
        ''' Method to save address '''
        if not self.exists():
            self.save()
            return True
        return False

    def delete_address(self, deep_delete=False):
        ''' Method to delete address '''
        if not deep_delete:
            if self.deactivate():
                return True
            return False
        if self.exists():
            self.delete()
            return True
        return False

    def exists(self):
        ''' Check if contact exists '''
        return True if Address.query.filter_by(address_line_1=self.address_line_1).first() else False

