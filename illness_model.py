from .. import db


class Illness(db.Model):
    __tablename__ = 'illness'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    title = db.Column(
        db.String(200),
        default="Untitled Illness",
        nullable=False
    )

    symptoms = db.relationship('Symptom', backref='illness')
    diagnoses = db.relationship('Diagnosis', backref='illness')

    active = db.Column(db.Boolean, nullable=False, default=True)

    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now()
    )

    def get_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'active': self.active,
            'created_on': self.created_on.strftime("%Y-%m-%dT%H:%M:%SZ"),
            'updated_on': self.updated_on.strftime("%Y-%m-%dT%H:%M:%SZ"),
            'symptoms': [s.get_json() for s in self.symptoms],
            'diagnosis': self.diagnoses[-1].data[0:3] if self.diagnoses and type(self.diagnoses[-1].data) is list else []  # noqa: E501
        }


class Symptom(db.Model):
    __tablename__ = 'symptom'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    illness_id = db.Column(
        db.Integer,
        db.ForeignKey('illness.id'),
        nullable=False
    )

    # Format for JSON
    # {
    #   "id": "s_1782",
    #   "name": "Abdominal pain, mild",
    #   "common_name": "Mild stomach pain",
    #   "orth": "mild stomach ache",
    #   "choice_id": "present",
    #   "type": "symptom"
    # }
    data = db.Column(db.JSON)

    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now()
    )

    def get_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'created_on': self.created_on.strftime("%Y-%m-%dT%H:%M:%SZ"),
            'updated_on': self.updated_on.strftime("%Y-%m-%dT%H:%M:%SZ"),
            'symptom_json': self.data
        }


class Diagnosis(db.Model):
    __tablename__ = 'diagnosis'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    illness_id = db.Column(db.Integer, db.ForeignKey('illness.id'))

    datetime = db.Column(db.DateTime, server_default=db.func.now())

    data = db.Column(db.JSON)

    def update_data(self, data):
        self.data = data
        db.session.add(self)
        db.session.commit

    def get_json(self):
        return {
            'id': self.id,
            'datetime': self.datetime.strftime("%Y-%m-%dT%H:%M:%SZ"),
            'diagnosis_json': self.data
        }
