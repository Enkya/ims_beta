from app.models.baseModel import db, BaseModel
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method


class ResourceMeta(BaseModel):
    ''' This class represents the resource model '''
    __tablename__ = 'resource'
    name = db.Column(db.String(255), nullable=False)
    version = db.Column(db.Integer)
    location = db.Column(db.String(255), nullable=False, default='/public')

    @hybrid_property
    def full_name(self):
        return self.location + '/' + self.name

    def save_resource(self):
        ''' Method to save resource metadata'''
        if not self.exists():
            self.save()
            return True
        return False

    def exists(self):
        ''' Check if resource metadata exists '''
        return True if ResourceMeta.query.filter_by(
            name=self.full_name).first() else False

    def __repr__(self):
        return "<Resource metadata: {}>".format(self.full_name)

    def __str__(self):
        return '{0}'.format(self.full_name)
