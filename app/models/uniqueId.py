from app.models.baseModel import db, BaseModel
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method


class UniqueId(BaseModel):
    ''' This class represents the available codes '''
    __tablename__ = 'uniqueid'
    value = db.Column(db.String(255), nullable=False)
    occupant = db.Column(db.String(255))

    def save_resource(self):
        if not self.exists():
            self.save()
            return True
        return False

    def exists(self):
        return True if UniqueId.query.filter_by(
            value=self.value).first() else False

    def __repr__(self):
        return "<Unique ID: {}>".format(self.value)

    def __str__(self):
        return '{0}'.format(self.value)
