from app.models.baseModel import BaseModel, db
from sqlalchemy.orm import relationship


class Typeapproval(BaseModel):
    ''' This class represents the typeapproval modal '''

    __tablename__ = 'typeapproval'
    equipment_category = db.Column(db.String(255))
    status_approved = db.Column(db.Boolean)
    equipment_name = db.Column(db.String(255))
    equipment_model = db.Column(db.String(255))
    equipment_desc = db.Column(db.String(255))
    applicable_standards = db.Column(db.String(255))
    approval_rejection_date = db.Column(db.DateTime)
    ta_unique_id = db.Column(db.String(255))
    ta_certificate_id = db.Column(db.Integer, db.ForeignKey('resource.id'))
    report_id = db.Column(db.Integer, db.ForeignKey('resource.id'))
    assessed_by_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    applicant_id = db.Column(db.Integer, db.ForeignKey('company.id'))

    ta_certificate = relationship(
        'ResourceMeta',
        foreign_keys=[ta_certificate_id]
    )
    report = relationship(
        'ResourceMeta',
        foreign_keys=[report_id]
    )
    assessed_by = relationship(
        'Employee',
        foreign_keys=[assessed_by_id]
    )
    applicant = relationship(
        'Company',
        foreign_keys=[applicant_id]
    )

    def save_typeapproval(self):
        ''' Method to save typeapproval '''
        if not self.exists():
            self.save()
            return True
        return False

    def delete_typeapproval(self, deep_delete=False):
        ''' Method to delete typeapproval '''
        if not deep_delete:
            if self.deactivate():
                return True
            return False
        if self.exists():
            self.delete()
            return True
        return False

    def exists(self):
        ''' Check if typeapproval exists '''
        return True if Typeapproval.query.filter_by(
            applicant=self.applicant,
            equipment_name=self.equipment_name).first() else False
