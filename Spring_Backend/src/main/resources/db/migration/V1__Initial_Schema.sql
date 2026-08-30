CREATE TABLE hospital (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255) NOT NULL
);

CREATE TABLE app_user (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    hospital_id BIGINT,
    FOREIGN KEY (hospital_id) REFERENCES hospital(id)
);

CREATE TABLE training_session (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    status VARCHAR(50) NOT NULL,
    total_rounds INT NOT NULL,
    idempotency_key VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE federated_round (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id BIGINT NOT NULL,
    round_number INT NOT NULL,
    global_accuracy DOUBLE,
    global_loss DOUBLE,
    checkpoint_path VARCHAR(500),
    FOREIGN KEY (session_id) REFERENCES training_session(id)
);

CREATE TABLE client_round_status (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    round_id BIGINT NOT NULL,
    hospital_id BIGINT NOT NULL,
    local_accuracy DOUBLE,
    local_loss DOUBLE,
    sample_count INT,
    FOREIGN KEY (round_id) REFERENCES federated_round(id),
    FOREIGN KEY (hospital_id) REFERENCES hospital(id)
);

CREATE TABLE model_version (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id BIGINT NOT NULL,
    round_number INT NOT NULL,
    model_path VARCHAR(500),
    accuracy DOUBLE,
    `precision` DOUBLE,
    recall DOUBLE,
    f1 DOUBLE,
    is_active BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (session_id) REFERENCES training_session(id)
);

CREATE TABLE prediction (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    hospital_id BIGINT,
    model_version_id BIGINT,
    patient_features VARCHAR(2000),
    result VARCHAR(255),
    FOREIGN KEY (hospital_id) REFERENCES hospital(id),
    FOREIGN KEY (model_version_id) REFERENCES model_version(id)
);

CREATE TABLE comparison_result (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id BIGINT NOT NULL,
    approach_type VARCHAR(50),
    accuracy DOUBLE,
    f1_score DOUBLE,
    training_time_sec BIGINT,
    FOREIGN KEY (session_id) REFERENCES training_session(id)
);

CREATE TABLE audit_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT,
    action VARCHAR(255) NOT NULL,
    resource_id VARCHAR(255),
    ip_address VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES app_user(id)
);
