from app.models.baseModel import db


class ResourceMixin():
    ''' This class represents the resource model '''
    version = db.Column(db.Integer)
    location = db.Column(db.String(255))
