from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://navexa_user:navexa_password@localhost/maritime_predictive_maintenance'
db = SQLAlchemy(app)

swagger = Swagger(app)

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
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    route = db.Column(db.Text)
    cargo_type = db.Column(db.String(100))
    operating_conditions = db.Column(db.Text)
    weather_data = db.Column(db.Text)

class OperationalState(db.Model):
    __tablename__ = 'operational_state'
    state_id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.equipment_id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    operating_mode = db.Column(db.String(50))
    load_percentage = db.Column(db.Numeric(5, 2))
    environmental_conditions = db.Column(db.Text)

class Sensor(db.Model):
    __tablename__ = 'sensor'
    sensor_id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.equipment_id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100))
    measurement_unit = db.Column(db.String(50))
    calibration_date = db.Column(db.Date)
    accuracy_range = db.Column(db.String(50))
    sampling_frequency = db.Column(db.Integer)  # In Hz or samples per unit time
    readings = db.relationship('SensorReading', backref='sensor', lazy=True)

class SensorReading(db.Model):
    __tablename__ = 'sensor_reading'
    reading_id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensor.sensor_id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    value = db.Column(db.Numeric(15, 6), nullable=False)
    quality_indicator = db.Column(db.String(50))
    collection_method = db.Column(db.String(50))

class FailureEvent(db.Model):
    __tablename__ = 'failure_event'
    event_id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.equipment_id'), nullable=False)
    component_id = db.Column(db.Integer, db.ForeignKey('component.component_id'), nullable=True)  # Nullable if not related to a component
    date_time = db.Column(db.DateTime, nullable=False)
    failure_type = db.Column(db.String(100))
    severity = db.Column(db.String(50))
    impact = db.Column(db.Text)
    resolution = db.Column(db.Text)

class FailureMode(db.Model):
    __tablename__ = 'failure_mode'
    mode_id = db.Column(db.Integer, primary_key=True)
    component_id = db.Column(db.Integer, db.ForeignKey('component.component_id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    typical_indicators = db.Column(db.Text)
    typical_causes = db.Column(db.Text)
    severity_impact = db.Column(db.String(50))

class PredictionModel(db.Model):
    __tablename__ = 'prediction_model'
    model_id = db.Column(db.Integer, primary_key=True)
    equipment_type = db.Column(db.String(50), nullable=False)
    trained_date = db.Column(db.Date)
    version = db.Column(db.String(50))
    accuracy_metrics = db.Column(db.Text)
    input_features = db.Column(db.Text)
    parameters = db.Column(db.Text)
    training_history = db.relationship('ModelTrainingHistory', backref='model', lazy=True)
    predictions = db.relationship('Prediction', backref='model', lazy=True)


class ModelTrainingHistory(db.Model):
    __tablename__ = 'model_training_history'
    training_id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey('prediction_model.model_id'), nullable=False)
    date_time = db.Column(db.DateTime, nullable=False)
    dataset_used = db.Column(db.Text)
    parameters = db.Column(db.Text)
    performance_metrics = db.Column(db.Text)


class Prediction(db.Model):
    __tablename__ = 'prediction'
    prediction_id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey('prediction_model.model_id'), nullable=False)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.equipment_id'), nullable=False)
    date_generated = db.Column(db.DateTime, nullable=False)
    failure_mode = db.Column(db.String(100))
    probability = db.Column(db.Numeric(5, 4))
    predicted_timeframe = db.Column(db.String(100))
    confidence_score = db.Column(db.Numeric(5, 4))


class AnomalyDetection(db.Model):
    __tablename__ = 'anomaly_detection'
    anomaly_id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.equipment_id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    type = db.Column(db.String(50))
    severity = db.Column(db.String(50))
    description = db.Column(db.Text)
    affected_sensors = db.Column(db.Text)  # Store sensor IDs or names as a list in a string format


class RemainingUsefulLife(db.Model):
    __tablename__ = 'remaining_useful_life'
    rul_id = db.Column(db.Integer, primary_key=True)
    component_id = db.Column(db.Integer, db.ForeignKey('component.component_id'), nullable=False, unique=True)  # Ensures one-to-one mapping
    calculation_date = db.Column(db.Date, nullable=False)
    estimated_time = db.Column(db.String(50))  # e.g., "500 hours" or "20 days"
    confidence_interval = db.Column(db.String(50))
    methodology = db.Column(db.String(100))

@app.route('/api/organizations', methods=['GET'])
def get_organizations():
    """
    Get a list of organization IDs and names.
    ---
    responses:
      200:
        description: A list of organization IDs and names.
        schema:
          type: array
          items:
            type: object
            properties:
              organization_id:
                type: integer
              name:
                type: string
    """
    organizations = Organization.query.all()

    org_list = [{'organization_id': org.organization_id, 'name': org.name} for org in organizations]

    return jsonify(org_list)
##############################
# ORGANIZATIONAL INFORMATION #
##############################
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

###########################
# OPERATIONAL INFORMATION #
###########################
@app.route('/api/operational_data/<int:vessel_id>', methods=['GET'])
def get_operational_data(vessel_id):
    """
    Get operational data for a specific vessel, including voyages, operational states, sensor readings, and failure events.
    ---
    parameters:
      - name: vessel_id
        in: path
        type: integer
        required: true
        description: ID of the vessel
    responses:
      200:
        description: Operational data of the vessel.
        schema:
          type: object
          properties:
            voyages:
              type: array
              items:
                $ref: '#/definitions/Voyage'
            operational_states:
              type: array
              items:
                $ref: '#/definitions/OperationalState'
            sensor_readings:
              type: array
              items:
                $ref: '#/definitions/SensorReading'
            failure_events:
              type: array
              items:
                $ref: '#/definitions/FailureEvent'
    definitions:
      Voyage:
        type: object
        properties:
          voyage_id:
            type: integer
          start_date:
            type: string
          end_date:
            type: string
          route:
            type: string
          cargo_type:
            type: string
          operating_conditions:
            type: string
          weather_data:
            type: string
      OperationalState:
        type: object
        properties:
          state_id:
            type: integer
          timestamp:
            type: string
          operating_mode:
            type: string
          load_percentage:
            type: string
          environmental_conditions:
            type: string
      SensorReading:
        type: object
        properties:
          reading_id:
            type: integer
          timestamp:
            type: string
          value:
            type: string
          quality_indicator:
            type: string
          collection_method:
            type: string
      FailureEvent:
        type: object
        properties:
          event_id:
            type: integer
          date_time:
            type: string
          failure_type:
            type: string
          severity:
            type: string
          impact:
            type: string
          resolution:
            type: string
    """
    vessel = Vessel.query.get(vessel_id)
    if not vessel:
        return jsonify({'error': 'Vessel not found'}), 404

    # Fetch voyages
    voyages = Voyage.query.filter_by(vessel_id=vessel_id).all()
    voyage_list = [{
        'voyage_id': v.voyage_id,
        'start_date': str(v.start_date),
        'end_date': str(v.end_date),
        'route': v.perform_route,
        'cargo_type': v.cargo_type,
        'operating_conditions': v.operating_conditions,
        'weather_data': v.weather_data
    } for v in voyages]

    # Fetch operational states
    operational_states = OperationalState.query.join(Equipment).filter(Equipment.vessel_id == vessel_id).all()
    operational_state_list = [{
        'state_id': s.state_id,
        'timestamp': str(s.timestamp),
        'operating_mode': s.operating_mode,
        'load_percentage': str(s.load_percentage),
        'environmental_conditions': s.environmental_conditions
    } for s in operational_states]

    # Fetch sensor readings
    sensor_readings = SensorReading.query.join(Sensor).join(Equipment).filter(Equipment.vessel_id == vessel_id).all()
    sensor_reading_list = [{
        'reading_id': sr.reading_id,
        'timestamp': str(sr.timestamp),
        'value': str(sr.value),
        'quality_indicator': sr.quality_indicator,
        'collection_method': sr.collection_method
    } for sr in sensor_readings]

    # Fetch failure events
    failure_events = FailureEvent.query.join(Equipment).filter(Equipment.vessel_id == vessel_id).all()
    failure_event_list = [{
        'event_id': fe.event_id,
        'date_time': str(fe.date_time),
        'failure_type': fe.failure_type,
        'severity': fe.severity,
        'impact': fe.impact,
        'resolution': fe.resolution
    } for fe in failure_events]

    operational_data = {
        'voyages': voyage_list,
        'operational_states': operational_state_list,
        'sensor_readings': sensor_reading_list,
        'failure_events': failure_event_list
    }
    return jsonify(operational_data)

if __name__ == '__main__':
    app.run(debug=True)
