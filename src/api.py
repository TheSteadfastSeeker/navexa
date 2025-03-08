from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://navexa_user:navexa_password@localhost/maritime_predictive_maintenance'
db = SQLAlchemy(app)

swagger = Swagger(app)  # Initialize Flasgger

# Database Models
class Organization(db.Model):
    __tablename__ = 'organization'
    organization_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50))
    contact_info = db.Column(db.Text)
    subscription_level = db.Column(db.String(50))
    fleets = db.relationship('Fleet', backref='organization', lazy=True)

class Fleet(db.Model):
    __tablename__ = 'fleet'
    fleet_id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.organization_id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50))
    description = db.Column(db.Text)
    vessels = db.relationship('Vessel', backref='fleet', lazy=True)

class Vessel(db.Model):
    __tablename__ = 'vessel'
    vessel_id = db.Column(db.Integer, primary_key=True)
    fleet_id = db.Column(db.Integer, db.ForeignKey('fleet.fleet_id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50))
    build_year = db.Column(db.Integer)
    classification = db.Column(db.String(50))
    dimensions = db.Column(db.String(100))
    gross_tonnage = db.Column(db.Numeric(10, 2))
    equipment = db.relationship('Equipment', backref='vessel', lazy=True)

class Equipment(db.Model):
    __tablename__ = 'equipment'
    equipment_id = db.Column(db.Integer, primary_key=True)
    vessel_id = db.Column(db.Integer, db.ForeignKey('vessel.vessel_id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    manufacturer = db.Column(db.String(100))
    model = db.Column(db.String(100))
    installation_date = db.Column(db.Date)
    specifications = db.Column(db.Text)
    manual_ref = db.Column(db.String(255))  # Added manual_ref column
    components = db.relationship('Component', backref='equipment', lazy=True)

class Component(db.Model):
    __tablename__ = 'component'
    component_id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.equipment_id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50))
    manufacturer = db.Column(db.String(100))
    serial_number = db.Column(db.String(100))
    installation_date = db.Column(db.Date)
class ServiceDetails(db.Model):
    __tablename__ = 'service_details'
    service_id = db.Column(db.Integer, primary_key=True)
    vessel_id = db.Column(db.Integer, db.ForeignKey('vessel.vessel_id'), nullable=False)
    service_date = db.Column(db.Date)
    service_type = db.Column(db.String(100))
    details = db.Column(db.Text)

class Voyage(db.Model):
    __tablename__ = 'voyage'
    voyage_id = db.Column(db.Integer, primary_key=True)
    vessel_id = db.Column(db.Integer, db.ForeignKey('vessel.vessel_id'), nullable=False)
    departure_port = db.Column(db.String(100))
    arrival_port = db.Column(db.String(100))
    departure_date = db.Column(db.Date)
    arrival_date = db.Column(db.Date)
    operational_details = db.relationship('OperationalDetails', backref='voyage', lazy=True)

class OperationalDetails(db.Model):
    __tablename__ = 'operational_details'
    operation_id = db.Column(db.Integer, primary_key=True)
    voyage_id = db.Column(db.Integer, db.ForeignKey('voyage.voyage_id'), nullable=False)
    speed = db.Column(db.Numeric(10, 2))
    fuel_consumption = db.Column(db.Numeric(10, 2))
    weather_conditions = db.Column(db.String(255))

class Sensor(db.Model):
    __tablename__ = 'sensor'
    sensor_id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.equipment_id'), nullable=False)
    sensor_type = db.Column(db.String(100))
    unit = db.Column(db.String(50))
    sensor_readings = db.relationship('SensorReading', backref='sensor', lazy=True)

class SensorReading(db.Model):
    __tablename__ = 'sensor_reading'
    reading_id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensor.sensor_id'), nullable=False)
    timestamp = db.Column(db.DateTime)
    value = db.Column(db.Numeric(10, 2))

class FailureEvent(db.Model):
    __tablename__ = 'failure_event'
    event_id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.equipment_id'), nullable=False)
    failure_mode = db.Column(db.String(100))
    detected_date = db.Column(db.Date)
    severity = db.Column(db.String(50))

class PredictionModel(db.Model):
    __tablename__ = 'prediction_model'
    model_id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.equipment_id'), nullable=False)
    model_name = db.Column(db.String(100))
    model_version = db.Column(db.String(50))
    last_trained_date = db.Column(db.Date)
    remaining_useful_life = db.relationship('RemainingUsefulLife', backref='prediction_model', lazy=True)

class RemainingUsefulLife(db.Model):
    __tablename__ = 'remaining_useful_life'
    rul_id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey('prediction_model.model_id'), nullable=False)
    predicted_rul_days = db.Column(db.Integer)
    prediction_date = db.Column(db.Date)

@app.route('/api/organization/<int:org_id>', methods=['GET'])
def get_organization(org_id):
    """
    Get details of an organization along with fleets, vessels, and equipment.
    ---
    parameters:
      - name: org_id
        in: path
        type: integer
        required: true
        description: ID of the organization
    responses:
      200:
        description: Organization details with related fleets, vessels, and equipment.
        schema:
          $ref: '#/definitions/Organization'
    definitions:
      Organization:
        type: object
        properties:
          organization_id:
            type: integer
          name:
            type: string
          type:
            type: string
          contact_info:
            type: string
          subscription_level:
            type: string
          fleets:
            type: array
            items:
              $ref: '#/definitions/Fleet'
      Fleet:
        type: object
        properties:
          fleet_id:
            type: integer
          name:
            type: string
          type:
            type: string
          description:
            type: string
          vessels:
            type: array
            items:
              $ref: '#/definitions/Vessel'
      Vessel:
        type: object
        properties:
          vessel_id:
            type: integer
          name:
            type: string
          type:
            type: string
          build_year:
            type: integer
          classification:
            type: string
          dimensions:
            type: string
          gross_tonnage:
            type: string
          equipment:
            type: array
            items:
              $ref: '#/definitions/Equipment'
      Equipment:
        type: object
        properties:
          equipment_id:
            type: integer
          type:
            type: string
          manufacturer:
            type: string
          model:
            type: string
          installation_date:
            type: string
          specifications:
            type: string
          manual_ref:
            type: string
          components:
            type: array
            items:
              $ref: '#/definitions/Component'
      Component:
        type: object
        properties:
          component_id:
            type: integer
          name:
            type: string
          type:
            type: string
          manufacturer:
            type: string
          serial_number:
            type: string
          installation_date:
            type: string
    """
    organization = Organization.query.get(org_id)
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404

    org_data = {
        'organization_id': organization.organization_id,
        'name': organization.name,
        'type': organization.type,
        'contact_info': organization.contact_info,
        'subscription_level': organization.subscription_level,
        'fleets': []
    }

    for fleet in organization.fleets:
        fleet_data = {
            'fleet_id': fleet.fleet_id,
            'name': fleet.name,
            'type': fleet.type,
            'description': fleet.description,
            'vessels': []
        }

        for vessel in fleet.vessels:
            vessel_data = {
                'vessel_id': vessel.vessel_id,
                'name': vessel.name,
                'type': vessel.type,
                'build_year': vessel.build_year,
                'classification': vessel.classification,
                'dimensions': vessel.dimensions,
                'gross_tonnage': str(vessel.gross_tonnage),
                'equipment': []
            }

            for equipment in vessel.equipment:
                equipment_data = {
                    'equipment_id': equipment.equipment_id,
                    'type': equipment.type,
                    'manufacturer': equipment.manufacturer,
                    'model': equipment.model,
                    'installation_date': str(equipment.installation_date),
                    'specifications': equipment.specifications,
                    'manual_ref': equipment.manual_ref,
                    'components': []
                }

                for component in equipment.components:
                    component_data = {
                        'component_id': component.component_id,
                        'name': component.name,
                        'type': component.type,
                        'manufacturer': component.manufacturer,
                        'serial_number': component.serial_number,
                        'installation_date': str(component.installation_date)
                    }
                    equipment_data['components'].append(component_data)

                vessel_data['equipment'].append(equipment_data)

            fleet_data['vessels'].append(vessel_data)

        org_data['fleets'].append(fleet_data)

    return jsonify(org_data)

if __name__ == '__main__':
    app.run(debug=True)
