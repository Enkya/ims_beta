from app.models.baseModel import BaseModel, db
from sqlalchemy.orm import relationship


class Spectrum(BaseModel):
    ''' This class represents the spectrum modal '''

    __tablename__ = 'spectrum'
    assigned_transmission_power = db.Column(db.Integer)
    authorized_antenna_gain = db.Column(db.Integer)
    authorized_antenna_height = db.Column(db.Integer)
    authorized_transmit_location = db.Column(db.Integer)
    assigned_stl_frequency = db.Column(db.Integer)
    assigned_stl_power = db.Column(db.Integer)
    assigned_stl_location = db.Column(db.String(255))
    tx_freq_assign_date = db.Column(db.DateTime)
    stl_freq_assign_date = db.Column(db.DateTime)
    band_of_operation = db.Column(db.String(255))
    service_authorized = db.Column(db.String(255))
    report_id = db.Column(db.Integer, db.ForeignKey('resource.id'))
    authorized_by_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    assigned_by_id = db.Column(db.Integer, db.ForeignKey('employee.id'))

    report = relationship(
        'Report',
        foreign_keys=[report_id]
    )
    authorized_by = relationship(
        'Employee',
        foreign_keys=[authorized_by_id]
    )
    assigned_by = relationship(
        'Employee',
        foreign_keys=[assigned_by_id]
    )

    def save_spectrum(self):
        ''' Method to save spectrum '''
        if not self.exists():
            self.save()
            return True
        return False

    def delete_spectrum(self, deep_delete=False):
        ''' Method to delete spectrum '''
        if not deep_delete:
            if self.deactivate():
                return True
            return False
        if self.exists():
            self.delete()
            return True
        return False

    def exists(self):
        ''' Check if spectrum exists '''
        return True if Spectrum.query.filter_by(
            assigned_stl_location=self.assigned_stl_location,
            active=True).first() else False
