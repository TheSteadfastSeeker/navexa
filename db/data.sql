-- Sample data insertion for all tables
\c maritime_predictive_maintenance;

-- 1. Core Entities
-- Organization
INSERT INTO organization (name, type, contact_info, subscription_level) VALUES
('Maritime Shipping Co.', 'Shipping', 'contact@maritimeshipping.com', 'Enterprise'),
('Global Logistics Ltd.', 'Logistics', 'info@globallogistics.com', 'Premium'),
('OceanTech Solutions', 'Technology Provider', 'support@oceantech.com', 'Standard');

-- Fleet
INSERT INTO fleet (organization_id, name, type, description) VALUES
(1, 'Cargo Fleet Alpha', 'Container', 'Primary container shipping fleet'),
(1, 'Tanker Fleet', 'Oil Tanker', 'Oil and petroleum products transport'),
(2, 'Bulk Carrier Fleet', 'Bulk Carrier', 'Bulk dry cargo shipping');

-- Vessel
INSERT INTO vessel (fleet_id, name, type, build_year, classification, dimensions, gross_tonnage) VALUES
(1, 'MS Oceanic', 'Container Ship', 2015, 'Class A', '300m x 48m x 30m', 90000.00),
(1, 'MS Pacific', 'Container Ship', 2018, 'Class A', '320m x 50m x 35m', 105000.00),
(2, 'MT Petrostar', 'Oil Tanker', 2012, 'Class B', '250m x 40m x 25m', 75000.00),
(3, 'MV Bulkhaul', 'Bulk Carrier', 2017, 'Class A', '225m x 35m x 20m', 65000.00);

-- Equipment
INSERT INTO equipment (vessel_id, type, manufacturer, model, installation_date, specifications, location_on_vessel, manual_ref)
VALUES
(1, 'Main Engine', 'Wärtsilä', 'RT-flex96C', '2015-03-15', '14-cylinder, 108,920 hp', 'Engine Room', 'manuals/equipment/Wartsila-RT-flex96C.pdf'),
(1, 'Generator', 'Caterpillar', 'C32', '2015-03-20', '1000 kW, 60 Hz', 'Engine Room', 'manuals/equipment/Caterpillar-C32.pdf'),
(1, 'Boiler', 'Alfa Laval', 'Aalborg OS', '2015-03-25', 'Steam output: 2.5 t/h', 'Engine Room', 'manuals/equipment/Wartsila-RT-flex82C.pdf'),
(2, 'Main Engine', 'MAN BnW', 'S90ME-C', '2018-05-10', '12-cylinder, 115,000 hp', 'Engine Room', 'manuals/equipment/MAN-B&W-6S90ME-C.pdf'),
(3, 'Main Engine', 'MAN BnW', 'G95ME-C', '2012-07-01', '10-cylinder, 85,000 hp', 'Engine Room', 'manuals/equipment/MAN-B&W-G95ME-C.pdf'),
(3, 'Cargo Pump', 'Framo', 'SD300', '2012-07-15', 'Capacity: 1000 m³/h', 'Pump Room', NULL),
(4, 'Main Engine', 'Wärtsilä', 'RT-flex82C', '2017-04-12', '8-cylinder, 72,000 hp', 'Engine Room', 'manuals/Wartsila-RT-flex82C.pdf');
-- Component
INSERT INTO component (equipment_id, name, type, manufacturer, serial_number, installation_date, expected_lifetime) VALUES
(1, 'Fuel Pump', 'Pump', 'Wärtsilä', 'FP-12345', '2015-03-15', 12000),
(1, 'Piston', 'Engine Part', 'Wärtsilä', 'P-23456', '2015-03-15', 20000),
(1, 'Turbocharger', 'Engine Part', 'ABB', 'TC-34567', '2015-03-15', 15000),
(2, 'Voltage Regulator', 'Electrical', 'Caterpillar', 'VR-45678', '2015-03-20', 10000),
(3, 'Burner', 'Boiler Part', 'Alfa Laval', 'B-56789', '2015-03-25', 8000),
(4, 'Fuel Pump', 'Pump', 'MAN B&W', 'FP-67890', '2018-05-10', 15000),
(5, 'Cylinder Liner', 'Engine Part', 'MAN B&W', 'CL-78901', '2012-07-01', 25000);

-- Sensor
INSERT INTO sensor (equipment_id, type, location, measurement_unit, calibration_date, accuracy_range, sampling_frequency) VALUES
(1, 'Temperature', 'Cylinder Head', 'Celsius', '2023-01-15', '±0.5°C', 60),
(1, 'Pressure', 'Fuel Line', 'Bar', '2023-01-15', '±0.1 Bar', 60),
(1, 'Vibration', 'Engine Mount', 'mm/s', '2023-01-20', '±0.05 mm/s', 120),
(2, 'Voltage', 'Output Terminal', 'Volt', '2023-02-01', '±0.5V', 30),
(3, 'Temperature', 'Steam Output', 'Celsius', '2023-02-10', '±1.0°C', 30),
(4, 'Temperature', 'Cylinder Head', 'Celsius', '2023-03-05', '±0.5°C', 60),
(5, 'Pressure', 'Fuel Rail', 'Bar', '2022-12-10', '±0.1 Bar', 60);

-- User
INSERT INTO "user" (organization_id, name, role, permissions, contact_info, authentication_details) VALUES
(1, 'John Smith', 'Fleet Manager', 'admin,report,maintenance', 'john.smith@maritimeshipping.com', 'hashed_password_1'),
(1, 'Sarah Johnson', 'Maintenance Engineer', 'maintenance,report', 'sarah.johnson@maritimeshipping.com', 'hashed_password_2'),
(2, 'David Lee', 'Fleet Manager', 'admin,report,maintenance', 'david.lee@globallogistics.com', 'hashed_password_3'),
(3, 'Emily Chen', 'Technical Support', 'support,report', 'emily.chen@oceantech.com', 'hashed_password_4'),
(1, 'Michael Brown', 'Captain', 'report,view', 'michael.brown@maritimeshipping.com', 'hashed_password_5');

-- 2. Operational Data
-- Voyage
INSERT INTO voyage (vessel_id, start_date, end_date, route, cargo_type, operating_conditions, weather_data) VALUES
(1, '2024-01-10', '2024-02-15', 'Rotterdam to Singapore', 'Consumer Electronics', 'Normal Operation', 'Moderate seas, Wind 15-20 knots'),
(1, '2024-02-20', '2024-03-25', 'Singapore to Los Angeles', 'Mixed Cargo', 'Normal Operation', 'Calm seas, Wind 5-10 knots'),
(2, '2024-01-05', '2024-02-10', 'Shanghai to Vancouver', 'Consumer Goods', 'Normal Operation', 'Rough seas, Wind 25-30 knots'),
(3, '2024-01-15', '2024-02-05', 'Saudi Arabia to Rotterdam', 'Crude Oil', 'Normal Operation', 'Moderate seas, Wind 10-15 knots'),
(4, '2024-02-01', '2024-03-10', 'Australia to Japan', 'Iron Ore', 'Normal Operation', 'Calm seas, Wind 5-10 knots');

-- Operational State
INSERT INTO operational_state (equipment_id, timestamp, operating_mode, load_percentage, environmental_conditions) VALUES
(1, '2024-01-15 08:00:00', 'Normal', 75.50, 'Sea temp: 18°C, Air temp: 22°C'),
(1, '2024-01-15 14:00:00', 'Normal', 80.20, 'Sea temp: 19°C, Air temp: 24°C'),
(1, '2024-01-16 08:00:00', 'Normal', 78.30, 'Sea temp: 18°C, Air temp: 21°C'),
(2, '2024-01-15 08:00:00', 'Normal', 65.00, 'Engine room temp: 35°C'),
(3, '2024-01-15 08:00:00', 'Normal', 60.50, 'Engine room temp: 38°C'),
(4, '2024-01-15 08:00:00', 'Normal', 70.80, 'Sea temp: 22°C, Air temp: 26°C'),
(5, '2024-01-15 08:00:00', 'Normal', 65.40, 'Sea temp: 15°C, Air temp: 18°C');

-- Sensor Reading (abbreviated - in a real system you'd have thousands of these)
INSERT INTO sensor_reading (sensor_id, timestamp, value, quality_indicator, collection_method) VALUES
(1, '2024-01-15 08:00:00', 85.2, 'Good', 'Automatic'),
(1, '2024-01-15 08:15:00', 84.8, 'Good', 'Automatic'),
(1, '2024-01-15 08:30:00', 86.1, 'Good', 'Automatic'),
(2, '2024-01-15 08:00:00', 35.5, 'Good', 'Automatic'),
(2, '2024-01-15 08:15:00', 35.7, 'Good', 'Automatic'),
(3, '2024-01-15 08:00:00', 2.8, 'Good', 'Automatic'),
(3, '2024-01-15 08:15:00', 3.2, 'Good', 'Automatic'),
(4, '2024-01-15 08:00:00', 440.5, 'Good', 'Automatic'),
(5, '2024-01-15 08:00:00', 175.3, 'Good', 'Automatic'),
(6, '2024-01-15 08:00:00', 82.7, 'Good', 'Automatic'),
(7, '2024-01-15 08:00:00', 30.2, 'Good', 'Automatic');

-- Failure Event
INSERT INTO failure_event (equipment_id, component_id, date_time, failure_type, severity, impact, resolution) VALUES
(1, 1, '2023-11-20 15:45:00', 'Fuel Pump Failure', 'Critical', 'Engine shutdown, vessel operational on reduced power', 'Emergency replacement of fuel pump'),
(3, 5, '2023-10-05 09:30:00', 'Burner Malfunction', 'Moderate', 'Reduced boiler efficiency', 'Burner cleaned and recalibrated'),
(2, 4, '2023-12-12 22:15:00', 'Voltage Regulator Failure', 'Major', 'Generator unstable output, switched to backup', 'Replaced voltage regulator');

-- 3. Analytical Models
-- Failure Mode
INSERT INTO failure_mode (component_id, name, description, typical_indicators, typical_causes, severity_impact) VALUES
(1, 'Fuel Pump Seizure', 'Complete failure of fuel pump', 'High temperature, Unusual noise, Pressure drop', 'Contamination, Wear and tear, Overheating', 'Critical'),
(1, 'Fuel Pump Leak', 'Fuel leakage from pump seals', 'Pressure fluctuation, Visible leakage, Reduced efficiency', 'Seal wear, Excessive pressure, Improper installation', 'Major'),
(2, 'Piston Ring Wear', 'Excessive wear of piston rings', 'Increased oil consumption, Reduced compression, Power loss', 'Normal wear, Poor lubrication, Overheating', 'Major'),
(3, 'Turbocharger Imbalance', 'Rotor imbalance in turbocharger', 'Unusual vibration, Noise, Reduced efficiency', 'Fouling, Bearing wear, Mechanical damage', 'Major'),
(5, 'Burner Fouling', 'Accumulation of deposits on burner', 'Irregular flame, Reduced efficiency, Increased fuel consumption', 'Fuel impurities, Incomplete combustion', 'Moderate');

-- Prediction Model
INSERT INTO prediction_model (equipment_type, trained_date, version, accuracy_metrics, input_features, parameters) VALUES
('Main Engine', '2023-09-15', 'v2.3', 'Precision: 0.92, Recall: 0.88, F1: 0.90', 'Temperature, Pressure, Vibration, Load, Run Hours', 'Learning rate: 0.01, Layers: 4, Neurons: [64, 32, 16, 8]'),
('Generator', '2023-08-20', 'v1.8', 'Precision: 0.89, Recall: 0.85, F1: 0.87', 'Voltage, Current, Frequency, Temperature, Load', 'Learning rate: 0.02, Layers: 3, Neurons: [32, 16, 8]'),
('Boiler', '2023-10-01', 'v1.5', 'Precision: 0.91, Recall: 0.86, F1: 0.88', 'Temperature, Pressure, Flow Rate, Gas Consumption', 'Learning rate: 0.015, Layers: 3, Neurons: [32, 16, 8]');

-- Model Training History
INSERT INTO model_training_history (model_id, date_time, dataset_used, parameters, performance_metrics) VALUES
(1, '2023-09-15 10:30:00', 'Engine data from 5 vessels, 2020-2023, 500,000 records', 'Epochs: 100, Batch size: 64, Optimizer: Adam', 'Training loss: 0.08, Validation loss: 0.12, Training time: 3.5 hours'),
(1, '2023-07-10 14:20:00', 'Engine data from 3 vessels, 2020-2022, 320,000 records', 'Epochs: 80, Batch size: 64, Optimizer: Adam', 'Training loss: 0.10, Validation loss: 0.15, Training time: 2.8 hours'),
(2, '2023-08-20 09:45:00', 'Generator data from 8 vessels, 2019-2023, 400,000 records', 'Epochs: 120, Batch size: 32, Optimizer: Adam', 'Training loss: 0.09, Validation loss: 0.14, Training time: 4.2 hours');

-- Prediction
INSERT INTO prediction (model_id, equipment_id, date_generated, failure_mode, probability, predicted_timeframe, confidence_score) VALUES
(1, 1, '2024-01-15 00:01:00', 'Fuel Pump Seizure', 0.15, '30-45 days', 0.82),
(1, 4, '2024-01-15 00:01:00', 'Cylinder Liner Wear', 0.28, '20-30 days', 0.88),
(1, 5, '2024-01-15 00:01:00', 'Fuel Injector Failure', 0.35, '15-25 days', 0.91),
(2, 2, '2024-01-15 00:01:00', 'Voltage Regulator Failure', 0.12, '45-60 days', 0.79),
(3, 3, '2024-01-15 00:01:00', 'Burner Fouling', 0.42, '10-20 days', 0.85);

-- Anomaly Detection
INSERT INTO anomaly_detection (equipment_id, timestamp, type, severity, description, affected_sensors) VALUES
(1, '2024-01-14 14:23:17', 'Temperature Spike', 'Warning', 'Unexpected temperature increase in cylinder #3', 'Temp sensor #1'),
(1, '2024-01-15 08:45:22', 'Pressure Fluctuation', 'Medium', 'Irregular pressure pattern in fuel system', 'Pressure sensor #2'),
(4, '2024-01-13 22:18:05', 'Vibration Anomaly', 'High', 'Abnormal vibration signature detected', 'Vibration sensor #8'),
(2, '2024-01-15 11:32:40', 'Voltage Irregularity', 'Medium', 'Unusual voltage pattern detected', 'Voltage sensor #4'),
(5, '2024-01-12 17:05:33', 'Temperature Trend', 'Low', 'Gradual temperature increase over 48 hours', 'Temp sensor #12');

-- Remaining Useful Life
INSERT INTO remaining_useful_life (component_id, calculation_date, estimated_time, confidence_interval, methodology) VALUES
(1, '2024-01-15', '1500 hours', '±300 hours', 'Statistical + Physics-based model'),
(2, '2024-01-15', '5200 hours', '±800 hours', 'Deep Learning model'),
(3, '2024-01-15', '2800 hours', '±450 hours', 'Statistical + Physics-based model'),
(4, '2024-01-15', '900 hours', '±200 hours', 'Statistical model'),
(5, '2024-01-15', '350 hours', '±100 hours', 'Machine Learning model'),
(6, '2024-01-15', '1850 hours', '±350 hours', 'Statistical + Physics-based model'),
(7, '2024-01-15', '8500 hours', '±1200 hours', 'Deep Learning model');

-- Alert
INSERT INTO alert (prediction_id, anomaly_id, type, severity, timestamp, description, status, resolution_notes) VALUES
(3, NULL, 'Predictive', 'High', '2024-01-15 00:05:00', 'Fuel injector failure predicted within 15-25 days', 'Open', NULL),
(NULL, 3, 'Anomaly', 'High', '2024-01-13 22:20:00', 'Abnormal vibration detected in main engine', 'In Progress', 'Initial investigation completed, scheduling inspection'),
(5, NULL, 'Predictive', 'Medium', '2024-01-15 00:10:00', 'Burner fouling predicted within 10-20 days', 'Open', NULL),
(NULL, 2, 'Anomaly', 'Medium', '2024-01-15 08:50:00', 'Irregular fuel pressure detected', 'Open', NULL),
(NULL, 1, 'Anomaly', 'Low', '2024-01-14 14:30:00', 'Temperature spike in cylinder #3', 'Closed', 'Temperature returned to normal range after adjustment');

-- Maintenance Task
INSERT INTO maintenance_task (equipment_id, alert_id, description, priority, status, scheduled_date, estimated_duration, assigned_to) VALUES
(5, 1, 'Replace fuel injectors', 'High', 'Scheduled', '2024-01-25', 8, 2),
(4, 2, 'Inspect and diagnose abnormal vibration', 'High', 'In Progress', '2024-01-16', 4, 2),
(3, 3, 'Clean and inspect burner', 'Medium', 'Scheduled', '2024-01-20', 6, 2),
(1, 4, 'Inspect fuel system for pressure irregularities', 'Medium', 'Pending', '2024-01-18', 3, 2),
(1, 5, 'Verify temperature sensor calibration', 'Low', 'Completed', '2024-01-15', 2, 2);

-- Maintenance Record
INSERT INTO maintenance_record (equipment_id, component_id, maintenance_task_id, date_time, type, description, parts_replaced, labor_hours, cost, user_id) VALUES
(1, 1, NULL, '2023-11-21 10:45:00', 'Corrective', 'Emergency replacement of failed fuel pump', 'Fuel pump (1)', 6.5, 4500.00, 2),
(3, 5, NULL, '2023-10-05 14:20:00', 'Corrective', 'Burner cleaning and recalibration', NULL, 3.0, 750.00, 2),
(2, 4, NULL, '2023-12-13 08:30:00', 'Corrective', 'Replacement of voltage regulator', 'Voltage regulator (1)', 2.5, 1200.00, 2),
(1, NULL, 5, '2024-01-15 13:45:00', 'Preventive', 'Temperature sensor inspection and calibration', NULL, 2.0, 300.00, 2),
(5, NULL, NULL, '2023-09-15 09:00:00', 'Planned', 'Annual engine inspection and maintenance', 'Fuel filters (4), Oil filters (2), Gaskets (8)', 24.0, 8500.00, 2);

-- Maintenance Procedure
INSERT INTO maintenance_procedure (equipment_type, title, steps, required_tools, required_parts, safety_precautions) VALUES
('Main Engine', 'Fuel Injector Replacement', '1. Shut down engine and allow to cool\n2. Depressurize fuel system\n3. Remove access panels\n4. Disconnect fuel lines\n5. Remove old injectors\n6. Install new injectors\n7. Reconnect fuel lines\n8. Test for leaks\n9. Restart engine and verify operation', 'Torque wrench, Socket set, Fuel line removal tool', 'Fuel injectors, Copper washers, O-rings', 'Ensure engine is cool and fuel system is depressurized. Wear appropriate PPE.'),
('Main Engine', 'Fuel Filter Replacement', '1. Shut down engine\n2. Close fuel supply valve\n3. Drain filter housing\n4. Remove old filter\n5. Install new filter\n6. Prime fuel system\n7. Check for leaks\n8. Restart engine', 'Filter wrench, Collection container', 'Fuel filter, O-rings, Gasket', 'Ensure engine is shut down and fuel supply is closed. Proper disposal of old filter and fuel.'),
('Generator', 'Voltage Regulator Replacement', '1. Shut down generator\n2. Disconnect battery\n3. Remove access panel\n4. Disconnect wiring\n5. Remove old regulator\n6. Install new regulator\n7. Reconnect wiring\n8. Test operation', 'Insulated screwdriver, Multimeter', 'Voltage regulator, Wire connectors', 'Ensure generator is shut down and battery disconnected. Use insulated tools.'),
('Boiler', 'Burner Cleaning', '1. Shut down boiler\n2. Allow to cool\n3. Remove burner assembly\n4. Clean burner components\n5. Inspect for damage\n6. Reassemble burner\n7. Test operation', 'Brush set, Compressed air, Cleaning solution', 'Gaskets, Seals', 'Ensure boiler is cool. Wear appropriate PPE. Proper ventilation required.'),
('Main Engine', 'Cylinder Head Inspection', '1. Shut down engine\n2. Allow to cool\n3. Remove necessary components\n4. Remove cylinder head\n5. Inspect for cracks and wear\n6. Measure valve clearances\n7. Reinstall cylinder head\n8. Reinstall components', 'Torque wrench, Lifting equipment, Feeler gauges', 'Head gasket, Bolts, Seals', 'Ensure engine is cool. Use proper lifting techniques. Follow torque specifications.');

-- Spare Part
INSERT INTO spare_part (name, compatible_equipment, stock_levels, supplier, cost, lead_time) VALUES
('Fuel Pump', 'Wärtsilä RT-flex96C, MAN B&W S90ME-C', 2, 'Marine Parts Inc.', 3500.00, '2-3 weeks'),
('Fuel Injector', 'Wärtsilä RT-flex96C, MAN B&W S90ME-C, MAN B&W G95ME-C', 8, 'Marine Parts Inc.', 850.00, '1-2 weeks'),
('Piston Ring Set', 'Wärtsilä RT-flex96C', 3, 'Engine Supply Co.', 1200.00, '2-4 weeks'),
('Turbocharger Repair Kit', 'ABB TPS-F', 1, 'ABB Marine', 2800.00, '3-4 weeks'),
('Voltage Regulator', 'Caterpillar C32', 2, 'Cat Marine Parts', 950.00, '1 week'),
('Burner Nozzle', 'Alfa Laval Aalborg OS', 4, 'Alfa Laval', 320.00, '1-2 weeks'),
('Cylinder Liner', 'MAN B&W G95ME-C', 1, 'MAN Marine Parts', 5500.00, '4-6 weeks'),
('Fuel Filter', 'Various', 25, 'Filter Supply Inc.', 45.00, '2-3 days'),
('Oil Filter', 'Various', 30, 'Filter Supply Inc.', 35.00, '2-3 days'),
('Gasket Set', 'Wärtsilä RT-flex96C', 5, 'Marine Parts Inc.', 650.00, '1-2 weeks');

-- Sensor Threshold
INSERT INTO sensor_threshold (sensor_id, min_value, max_value, warning_levels, context_conditions) VALUES
(1, 70.0, 95.0, 'Warning: 90-95, Critical: >95', 'Normal operation'),
(1, 65.0, 90.0, 'Warning: 85-90, Critical: >90', 'Low load operation'),
(2, 30.0, 40.0, 'Warning: 38-40, Critical: >40', 'Normal operation'),
(3, 0.0, 5.0, 'Warning: 4-5, Critical: >5', 'Normal operation'),
(4, 430.0, 450.0, 'Warning: <435 or >445, Critical: <430 or >450', 'Normal operation'),
(5, 165.0, 185.0, 'Warning: 180-185, Critical: >185', 'Normal operation'),
(6, 70.0, 90.0, 'Warning: 85-90, Critical: >90', 'Normal operation'),
(7, 25.0, 35.0, 'Warning: 32-35, Critical: >35', 'Normal operation');

-- Junction table for many-to-many relationships
INSERT INTO maintenance_procedure_spare_part (procedure_id, part_id, quantity) VALUES
(1, 2, 1), -- Fuel Injector Replacement needs 1 Fuel Injector
(1, 9, 2), -- Fuel Injector Replacement needs 2 Gaskets
(2, 8, 1), -- Fuel Filter Replacement needs 1 Fuel Filter
(3, 5, 1), -- Voltage Regulator Replacement needs 1 Voltage Regulator
(5, 10, 1); -- Cylinder Head Inspection may need 1 Gasket Set