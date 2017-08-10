from flask_restful import json
from flask_bcrypt import Bcrypt
from itsdangerous import (
    TimedJSONWebSignatureSerializer as Serializer,
    BadSignature, SignatureExpired
)

from app.models.baseModel import BaseModel
from app import db
from instance.config import Config

bcrypt = Bcrypt()


class User(BaseModel):
    '''This class represents the user model'''
    first_name = db.Column(db.String(25), nullable=False)
    last_name = db.Column(db.String(35), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    _password_hash = db.Column(db.String(25))

    @property
    def password(self):
        ''' Method that is run when password property is called '''
        return json.loads('Password: Write Only')

    @password.setter
    def password(self, password):
        self._password_hash = bcrypt.generate_password_hash(
            password, Config.BCRYPT_LOG_ROUNDS).decode()

    def exists(self):
        return True if User.query.filter_by(email=self.email).first() else False

    def verify_password(self, password):
        ''' Method to verify that user's password matches password provided '''
        return bcrypt.check_password_hash(self._password_hash, password)

    def generate_auth_token(self, duration=Config.AUTH_TOKEN_DURATION):
        ''' Method for generating a JWT authentication token '''
        serializer = Serializer(Config.SECRET_KEY, expires_in=int(duration))
        return serializer.dumps({'id': self.id})

    def __repr__(self):
        return '<User %r>' % self.name()

    def __str__(self):
        return '{0}'.format(self.name())
