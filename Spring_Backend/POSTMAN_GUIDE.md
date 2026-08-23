# Manual Postman Testing Guide for FL Backend

This guide explains how to manually test the currently implemented endpoints in the Spring backend using Postman.

## 1) Start the backend

From the project root:

```bash
./mvnw spring-boot:run
```

Make sure MySQL is running and the DB from `application.yml` is available:

- URL: `jdbc:mysql://localhost:3306/fl_backend`
- User: `root`
- Password: `password`

## 2) Create the required test users

Because the app does not include user creation APIs, insert seed users manually into MySQL.

### Example SQL

```sql
INSERT INTO hospital (name, contact_email)
VALUES ('City General Hospital', 'admin@citygeneral.com');

INSERT INTO user (username, password_hash, role, hospital_id)
VALUES
  ('admin', '$2b$12$f6uSyWoGRtgy5q5rlHZ2C.uG1YzNDE/QbtSMAyaTfLdZcovFds3s2', 'ADMIN', NULL),
  ('hospital1', '$2b$12$f6uSyWoGRtgy5q5rlHZ2C.uG1YzNDE/QbtSMAyaTfLdZcovFds3s2', 'HOSPITAL', 1);
```

Notes:

- The password hash above corresponds to the plain password `password123`.
- `role` must be `ADMIN` or `HOSPITAL` because the app builds authorities as `ROLE_ADMIN` and `ROLE_HOSPITAL`.
- For hospital users, `hospital_id` should point to a valid hospital row.

## 3) Import Postman files

Import these files into Postman:

- [postman/FL_Backend_Manual_Test.postman_collection.json](postman/FL_Backend_Manual_Test.postman_collection.json)
- [postman/FL_Backend_Local.postman_environment.json](postman/FL_Backend_Local.postman_environment.json)

In Postman, set the current environment to `FL Backend Local`.

## 4) Test flow

### A. Login as admin

Use `Auth > Login as Admin`.

Request body:

```json
{
  "username": "admin",
  "password": "password123"
}
```

The login request will store the JWT into the `token` variable automatically.

### B. Login as hospital user

Use `Auth > Login as Hospital User`.

Request body:

```json
{
  "username": "hospital1",
  "password": "password123"
}
```

This stores the hospital JWT into `hospitalToken`.

### C. Test admin-only client endpoint

Call:

```http
GET /api/v1/clients
Authorization: Bearer {{token}}
```

Expected outcome: returns all hospitals.

### D. Test hospital-specific endpoint

Call:

```http
GET /api/v1/clients/me
Authorization: Bearer {{hospitalToken}}
```

Expected outcome: returns the hospital profile tied to the JWT's `hospital_id`.

### E. Test metrics endpoints

Admin token:

```http
GET /api/v1/metrics/global?sessionId=1
GET /api/v1/metrics/comparison?sessionId=1
```

These return metrics stored for a session. If there are no rows yet, they may return an empty array.

### F. Test active model endpoint

```http
GET /api/v1/model/info
Authorization: Bearer {{token}}
```

If there is no active model row in `model_version`, you will get a 404 response.

### G. Run prediction

Use hospital token.

```http
POST /api/v1/predict
Authorization: Bearer {{hospitalToken}}
Content-Type: application/json
```

Body example:

```json
{
  "age": 62,
  "sex": "M",
  "bmi": 28.4,
  "smoking": true,
  "blood_pressure": 138
}
```

This endpoint stores a prediction row and returns a mocked result string.

### H. View predictions

Hospital user:

```http
GET /api/v1/predictions
Authorization: Bearer {{hospitalToken}}
```

Admin user:

```http
GET /api/v1/predictions
Authorization: Bearer {{token}}
```

### I. Start training

Admin only:

```http
POST /api/v1/training/start?totalRounds=10
Authorization: Bearer {{token}}
```

This creates a `TrainingSession` and stores the returned `id` into `sessionId` automatically.

### J. Check training status

```http
GET /api/v1/training/status?sessionId={{sessionId}}
Authorization: Bearer {{token}}
```

## 5) Expected behavior notes

This backend is intentionally a mock/test scaffold. Some endpoints return:

- empty arrays when no DB rows exist
- `404` when no active model or session exists
- mocked prediction strings instead of real model inference
- a new training session without actual external orchestration

## 6) Useful checks for manual verification

These are the basic checks to confirm the app is working:

1. `POST /api/v1/auth/login` returns a JWT
2. `GET /api/v1/clients` works with admin token
3. `GET /api/v1/clients/me` works with hospital token
4. `POST /api/v1/predict` stores a prediction and returns 200
5. `GET /api/v1/predictions` returns the user-visible predictions
6. `POST /api/v1/training/start` returns a new training session
7. `GET /api/v1/training/status` returns the saved session status

## 7) Troubleshooting

### 401 Unauthorized

- Check if the token is expired
- Check if the `Authorization` header is exactly `Bearer <token>`
- Confirm the user exists in the database and the password hash matches the plain password

### 403 Forbidden

- If you use hospital token on an admin-only endpoint, you will get a forbidden error
- If you use admin token on `clients/me`, it may be rejected by the controller's `@PreAuthorize` rules

### 404 Not Found

- `model/info` may return 404 if `model_version` has no active row
- `training/status` may return 404 if the session ID does not exist

### Empty arrays

- This is expected if there are no corresponding rows in `federated_round`, `comparison_result`, or `prediction`

## 8) Example SQL for inserting a model row

If you want `GET /api/v1/model/info` to return data, insert one active model record manually:

```sql
INSERT INTO training_session (status, total_rounds, idempotency_key)
VALUES ('IN_PROGRESS', 10, 'session-001');

INSERT INTO model_version (session_id, round_number, model_path, accuracy, precision, recall, f1, is_active)
VALUES (1, 1, '/models/demo-model-v1.pkl', 0.91, 0.89, 0.90, 0.89, TRUE);
```

## 9) Example SQL for adding session metrics

```sql
INSERT INTO federated_round (session_id, round_number, global_accuracy, global_loss, checkpoint_path)
VALUES (1, 1, 0.89, 0.42, '/checkpoints/round1.ckpt');

INSERT INTO comparison_result (session_id, approach_type, accuracy, f1_score, training_time_sec)
VALUES (1, 'FEDERATED', 0.89, 0.87, 120);
```

That will make the metrics APIs return non-empty results.
