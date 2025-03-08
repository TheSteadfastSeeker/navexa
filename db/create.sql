-- Create database
CREATE DATABASE maritime_predictive_maintenance;
\c maritime_predictive_maintenance;

-- 1. Core Entities
-- Organization
CREATE TABLE organization (
    organization_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50),
    contact_info TEXT,
    subscription_level VARCHAR(50)
);

-- Fleet
CREATE TABLE fleet (
    fleet_id SERIAL PRIMARY KEY,
    organization_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50),
    description TEXT,
    FOREIGN KEY (organization_id) REFERENCES organization(organization_id)
);

-- Vessel
CREATE TABLE vessel (
    vessel_id SERIAL PRIMARY KEY,
    fleet_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50),
    build_year INT,
    classification VARCHAR(50),
    dimensions VARCHAR(100),
    gross_tonnage DECIMAL(10,2),
    FOREIGN KEY (fleet_id) REFERENCES fleet(fleet_id)
);

-- Equipment
CREATE TABLE equipment (
    equipment_id SERIAL PRIMARY KEY,
    vessel_id INT NOT NULL,
    type VARCHAR(50) NOT NULL,
    manufacturer VARCHAR(100),
    model VARCHAR(100),
    installation_date DATE,
    specifications TEXT,
    location_on_vessel VARCHAR(100),
    manual_ref VARCHAR(100),
    FOREIGN KEY (vessel_id) REFERENCES vessel(vessel_id)
);

-- Component
CREATE TABLE component (
    component_id SERIAL PRIMARY KEY,
    equipment_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50),
    manufacturer VARCHAR(100),
    serial_number VARCHAR(100),
    installation_date DATE,
    expected_lifetime INT, -- in hours or days
    FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id)
);

-- Sensor
CREATE TABLE sensor (
    sensor_id SERIAL PRIMARY KEY,
    equipment_id INT NOT NULL,
    type VARCHAR(50) NOT NULL,
    location VARCHAR(100),
    measurement_unit VARCHAR(50),
    calibration_date DATE,
    accuracy_range VARCHAR(50),
    sampling_frequency INT, -- in Hz or samples per time unit
    FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id)
);

-- User
CREATE TABLE "user" (
    user_id SERIAL PRIMARY KEY,
    organization_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(50),
    permissions TEXT,
    contact_info TEXT,
    authentication_details VARCHAR(255),
    FOREIGN KEY (organization_id) REFERENCES organization(organization_id)
);

-- 2. Operational Data
-- Voyage
CREATE TABLE voyage (
    voyage_id SERIAL PRIMARY KEY,
    vessel_id INT NOT NULL,
    start_date DATE,
    end_date DATE,
    route TEXT,
    cargo_type VARCHAR(100),
    operating_conditions TEXT,
    weather_data TEXT,
    FOREIGN KEY (vessel_id) REFERENCES vessel(vessel_id)
);

-- Operational State
CREATE TABLE operational_state (
    state_id SERIAL PRIMARY KEY,
    equipment_id INT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    operating_mode VARCHAR(50),
    load_percentage DECIMAL(5,2),
    environmental_conditions TEXT,
    FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id)
);

-- Sensor Reading
CREATE TABLE sensor_reading (
    reading_id SERIAL PRIMARY KEY,
    sensor_id INT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    value DECIMAL(15,6),
    quality_indicator VARCHAR(50),
    collection_method VARCHAR(50),
    FOREIGN KEY (sensor_id) REFERENCES sensor(sensor_id)
);

-- Failure Event
CREATE TABLE failure_event (
    event_id SERIAL PRIMARY KEY,
    equipment_id INT NOT NULL,
    component_id INT,
    date_time TIMESTAMP NOT NULL,
    failure_type VARCHAR(100),
    severity VARCHAR(50),
    impact TEXT,
    resolution TEXT,
    FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id),
    FOREIGN KEY (component_id) REFERENCES component(component_id)
);

-- 3. Analytical Models
-- Failure Mode
CREATE TABLE failure_mode (
    mode_id SERIAL PRIMARY KEY,
    component_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    typical_indicators TEXT,
    typical_causes TEXT,
    severity_impact VARCHAR(50),
    FOREIGN KEY (component_id) REFERENCES component(component_id)
);

-- Prediction Model
CREATE TABLE prediction_model (
    model_id SERIAL PRIMARY KEY,
    equipment_type VARCHAR(50) NOT NULL,
    trained_date DATE,
    version VARCHAR(50),
    accuracy_metrics TEXT,
    input_features TEXT,
    parameters TEXT
);

-- Model Training History
CREATE TABLE model_training_history (
    training_id SERIAL PRIMARY KEY,
    model_id INT NOT NULL,
    date_time TIMESTAMP NOT NULL,
    dataset_used TEXT,
    parameters TEXT,
    performance_metrics TEXT,
    FOREIGN KEY (model_id) REFERENCES prediction_model(model_id)
);

-- Prediction
CREATE TABLE prediction (
    prediction_id SERIAL PRIMARY KEY,
    model_id INT NOT NULL,
    equipment_id INT NOT NULL,
    date_generated TIMESTAMP NOT NULL,
    failure_mode VARCHAR(100),
    probability DECIMAL(5,4),
    predicted_timeframe VARCHAR(100),
    confidence_score DECIMAL(5,4),
    FOREIGN KEY (model_id) REFERENCES prediction_model(model_id),
    FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id)
);

-- Anomaly Detection
CREATE TABLE anomaly_detection (
    anomaly_id SERIAL PRIMARY KEY,
    equipment_id INT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    type VARCHAR(50),
    severity VARCHAR(50),
    description TEXT,
    affected_sensors TEXT,
    FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id)
);

-- Remaining Useful Life
CREATE TABLE remaining_useful_life (
    rul_id SERIAL PRIMARY KEY,
    component_id INT NOT NULL,
    calculation_date DATE NOT NULL,
    estimated_time VARCHAR(50), -- could be hours, days, etc.
    confidence_interval VARCHAR(50),
    methodology VARCHAR(100),
    FOREIGN KEY (component_id) REFERENCES component(component_id),
    UNIQUE (component_id) -- ensures one-to-one relationship
);

-- 4. Operational Management
-- Alert
CREATE TABLE alert (
    alert_id SERIAL PRIMARY KEY,
    prediction_id INT,
    anomaly_id INT,
    type VARCHAR(50),
    severity VARCHAR(50),
    timestamp TIMESTAMP NOT NULL,
    description TEXT,
    status VARCHAR(50),
    resolution_notes TEXT,
    FOREIGN KEY (prediction_id) REFERENCES prediction(prediction_id),
    FOREIGN KEY (anomaly_id) REFERENCES anomaly_detection(anomaly_id)
);

-- Maintenance Task
CREATE TABLE maintenance_task (
    task_id SERIAL PRIMARY KEY,
    equipment_id INT NOT NULL,
    alert_id INT,
    description TEXT,
    priority VARCHAR(50),
    status VARCHAR(50),
    scheduled_date DATE,
    estimated_duration INT, -- in hours
    assigned_to INT,
    FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id),
    FOREIGN KEY (alert_id) REFERENCES alert(alert_id),
    FOREIGN KEY (assigned_to) REFERENCES "user"(user_id)
);

-- Maintenance Record
CREATE TABLE maintenance_record (
    record_id SERIAL PRIMARY KEY,
    equipment_id INT,
    component_id INT,
    maintenance_task_id INT,
    date_time TIMESTAMP NOT NULL,
    type VARCHAR(50),
    description TEXT,
    parts_replaced TEXT,
    labor_hours DECIMAL(5,2),
    cost DECIMAL(10,2),
    user_id INT,
    FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id),
    FOREIGN KEY (component_id) REFERENCES component(component_id),
    FOREIGN KEY (maintenance_task_id) REFERENCES maintenance_task(task_id),
    FOREIGN KEY (user_id) REFERENCES "user"(user_id)
);

-- Maintenance Procedure
CREATE TABLE maintenance_procedure (
    procedure_id SERIAL PRIMARY KEY,
    equipment_type VARCHAR(50) NOT NULL,
    title VARCHAR(100) NOT NULL,
    steps TEXT,
    required_tools TEXT,
    required_parts TEXT,
    safety_precautions TEXT
);

-- Spare Part
CREATE TABLE spare_part (
    part_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    compatible_equipment VARCHAR(100),
    stock_levels INT,
    supplier VARCHAR(100),
    cost DECIMAL(10,2),
    lead_time VARCHAR(50)
);

-- Sensor Threshold
CREATE TABLE sensor_threshold (
    threshold_id SERIAL PRIMARY KEY,
    sensor_id INT NOT NULL,
    min_value DECIMAL(15,6),
    max_value DECIMAL(15,6),
    warning_levels TEXT,
    context_conditions TEXT,
    FOREIGN KEY (sensor_id) REFERENCES sensor(sensor_id)
);

-- Junction tables for many-to-many relationships
CREATE TABLE maintenance_procedure_spare_part (
    procedure_id INT NOT NULL,
    part_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    PRIMARY KEY (procedure_id, part_id),
    FOREIGN KEY (procedure_id) REFERENCES maintenance_procedure(procedure_id),
    FOREIGN KEY (part_id) REFERENCES spare_part(part_id)
);

-- Create indexes for performance
CREATE INDEX idx_equipment_vessel ON equipment(vessel_id);
CREATE INDEX idx_component_equipment ON component(equipment_id);
CREATE INDEX idx_sensor_equipment ON sensor(equipment_id);
CREATE INDEX idx_sensor_reading_sensor ON sensor_reading(sensor_id);
CREATE INDEX idx_alert_prediction ON alert(prediction_id);
CREATE INDEX idx_alert_anomaly ON alert(anomaly_id);
CREATE INDEX idx_maintenance_task_equipment ON maintenance_task(equipment_id);
CREATE INDEX idx_maintenance_record_task ON maintenance_record(maintenance_task_id);
