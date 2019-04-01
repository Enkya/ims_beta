from app.models.baseModel import BaseModel, db
from sqlalchemy.orm import relationship


class Telecom(BaseModel):
    ''' This class represents the telecom modal '''

    __tablename__ = 'telecom'
    service_details = db.Column(db.String(255))
    service_technology = db.Column(db.String(255))
    qos_reqs_claims_status = db.Column(db.String(255))
    coverage_area_details = db.Column(db.String(255))
    sharing_requirements = db.Column(db.String(255))
    protection_status = db.Column(db.String(255))
    essential_resource_auth_status = db.Column(db.String(255))
    outage_status = db.Column(db.String(255))
    emergency_service_requirements = db.Column(db.String(255))
    general_provisions = db.Column(db.String(255))
    notes = db.Column(db.String(255))
    recommendations = db.Column(db.String(255))
    outage_report_id = db.Column(db.Integer, db.ForeignKey('resource.id'))
    report_id = db.Column(db.Integer, db.ForeignKey('resource.id'))
    reviewed_by_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    approved_by_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    inspected_by_id = db.Column(db.Integer, db.ForeignKey('employee.id'))

    outage_report = relationship(
        'ResourceMeta',
        foreign_keys=[outage_report_id]
    )
    report = relationship(
        'ResourceMeta',
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

    def save_telecom(self):
        ''' Method to save telecom '''
        if not self.exists():
            self.save()
            return True
        return False

    def delete_telecom(self, deep_delete=False):
        ''' Method to delete telecom '''
        if not deep_delete:
            if self.deactivate():
                return True
            return False
        if self.exists():
            self.delete()
            return True
        return False

    def exists(self):
        ''' Check if telecom exists '''
        return True if Telecom.query.filter_by(
            service_details=self.service_details,
            active=True).first() else False
