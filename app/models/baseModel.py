from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class BaseModel(db.Model):
    ''' A model detailing the base properties to be inherited '''
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())
    active = db.Column(db.Boolean, default=True)

    def __init__(self, *args):
        for k, v in args[0].items():
            setattr(self, k, v)

    def delete(self):
        '''delete data from database'''
        db.session.delete(self)
        db.session.commit()

    def deactivate(self):
        ''' deactivate data '''
        if self.exists() and self.active:
            self.active = False
            self.save()
            return True
        return False

    def save(self):
        '''save data to database'''
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def __item_exists():
        pass
