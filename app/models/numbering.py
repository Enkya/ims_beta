from app.models.baseModel import BaseModel, db
from sqlalchemy.orm import relationship


class Numbering(BaseModel):
    ''' This class represents the Numbering model '''

    __tablename__ = 'numbering'
    service_category = db.Column(db.String(255))
    number_type = db.Column(db.String(255))
    service_provider_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    applicable_service_type = db.Column(db.String(255))
    description = db.Column(db.String(255))
    assigned_range = db.Column(db.Integer)
    assigned_number = db.Column(db.Integer)
    assignment_date = db.Column(
        db.DateTime,
        default=db.func().current_timestamp())
    assigned_by_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    last_auth_renewal_date = db.Column(db.DateTime)
    is_compliant = db.Column(db.Boolean, default=True)
    notes = db.Column(db.String(255))
    recommendations = db.Column(db.String(255))
    report_id = db.Column(db.Integer, db.ForeignKey('resource.id'))
    last_updated_by_id = db.Column(
        db.Integer,
        db.ForeignKey('employee.id'))

    last_updated_by = relationship(
        'Employee',
        foreign_keys=[last_updated_by_id])
    report = relationship(
        'Report',
        foreign_keys=[report_id]
    )
    assigned_by = relationship(
        'Employee',
        foreign_keys=[assigned_by_id]
    )
