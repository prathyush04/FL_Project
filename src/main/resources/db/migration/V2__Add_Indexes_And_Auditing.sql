ALTER TABLE hospital ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE hospital ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

ALTER TABLE user ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE user ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

ALTER TABLE training_session ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE training_session ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

-- Add indexes for common queries
CREATE INDEX idx_user_hospital_id ON user(hospital_id);
CREATE INDEX idx_federated_round_session_id ON federated_round(session_id);
CREATE INDEX idx_client_round_status_round_id ON client_round_status(round_id);
CREATE INDEX idx_client_round_status_hospital_id ON client_round_status(hospital_id);
CREATE INDEX idx_model_version_session_id ON model_version(session_id);
CREATE INDEX idx_prediction_hospital_id ON prediction(hospital_id);
CREATE INDEX idx_comparison_result_session_id ON comparison_result(session_id);
