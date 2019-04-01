from app.models.baseModel import BaseModel, db
from sqlalchemy.orm import relationship


class Numbering(BaseModel):
    ''' This class represents the Numbering model '''

    __tablename__ = 'numbering'
    service_category = db.Column(db.String(255))
    number_type = db.Column(db.String(255))
    applicable_service_type = db.Column(db.String(255))
    description = db.Column(db.String(255))
    assigned_range = db.Column(db.Integer)
    assigned_number = db.Column(db.Integer)
    assignment_date = db.Column(
        db.DateTime,
        default=db.func.current_timestamp())
    last_auth_renewal_date = db.Column(db.DateTime)
    is_compliant = db.Column(db.Boolean, default=True)
    notes = db.Column(db.String(255))
    recommendations = db.Column(db.String(255))
    service_provider_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    report_id = db.Column(db.Integer, db.ForeignKey('resource.id'))
    assigned_by_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    last_updated_by_id = db.Column(
        db.Integer,
        db.ForeignKey('employee.id'))

    last_updated_by = relationship(
        'Employee',
        foreign_keys=[last_updated_by_id])
    report = relationship(
        'ResourceMeta',
        foreign_keys=[report_id]
    )
    assigned_by = relationship(
        'Employee',
        foreign_keys=[assigned_by_id]
    )
    service_provider = relationship(
        'Company',
        foreign_keys=[service_provider_id]
    )

    def save_numbering(self):
        ''' Method to save numbering '''
        if not self.exists():
            self.save()
            return True
        return False

    def delete_numbering(self, deep_delete=False):
        ''' Method to delete numbering '''
        if not deep_delete:
            if self.deactivate():
                return True
            return False
        if self.exists():
            self.delete()
            return True
        return False

    def exists(self):
        ''' Check if numbering exists '''
        return True if Numbering.query.filter_by(
            assigned_number=self.assigned_number).first() else False
