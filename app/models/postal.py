from app.models.baseModel import BaseModel, db
from sqlalchemy.orm import relationship


class Postal(BaseModel):
    ''' This class represents the postal modal '''

    __tablename__ = 'postal'
    call_sign = db.Column(db.String(255), nullable=False)
    physical_location_requirements = db.Column(db.String(255))
    license_validity = db.Column(db.Integer)
    postal_article_confidentiality = db.Column(db.Integer)
    training_requirements = db.Column(db.Boolean)
    qos_requirements_working_days = db.Column(db.Boolean)
    qos_requirements_claims_policy = db.Column(db.Boolean)
    qos_requirements_control_prohibited_items = db.Column(db.Boolean)
    qos_requirements_complaints_register = db.Column(db.Boolean)
    notes_01 = db.Column(db.String(255))
    notes_02 = db.Column(db.String(255))
    recommendations = db.Column(db.String(255))
    report_id = db.Column(db.Integer, db.ForeignKey('resource.id'))
    inspected_by_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    reviewed_by_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    approved_by_id = db.Column(db.Integer, db.ForeignKey('employee.id'))

    report = relationship(
        'Report',
        foreign_keys=[report_id]
    )
    inspected_by = relationship(
        'Employee',
        foreign_keys=[inspected_by_id]
    )
    reviewed_by = relationship(
        'Employee',
        foreign_keys=[reviewed_by_id]
    )
    approved_by = relationship(
        'Employee',
        foreign_keys=[approved_by_id]
    )

    def save_postal(self):
        ''' Method to save postal '''
        if not self.exists():
            self.save()
            return True
        return False

    def delete_postal(self, deep_delete=False):
        ''' Method to delete postal '''
        if not deep_delete:
            if self.deactivate():
                return True
            return False
        if self.exists():
            self.delete()
            return True
        return False

    def exists(self):
        ''' Check if postal exists '''
        return True if Postal.query.filter_by(
            call_sign=self.call_sign, active=True).first() else False
