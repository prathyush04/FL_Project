package com.fl.backend.service.impl;

import com.fl.backend.entity.ModelVersion;
import com.fl.backend.entity.Prediction;
import com.fl.backend.repository.HospitalRepository;
import com.fl.backend.repository.ModelVersionRepository;
import com.fl.backend.repository.PredictionRepository;
import com.fl.backend.service.PredictionService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Slf4j
@Service
@RequiredArgsConstructor
public class PredictionServiceImpl implements PredictionService {

    private final PredictionRepository predictionRepository;
    private final HospitalRepository hospitalRepository;
    private final ModelVersionRepository modelVersionRepository;
    private final org.springframework.web.client.RestTemplate restTemplate;

    @Value("${app.ml-service.url:http://localhost:8000}")
    private String mlServiceUrl;

    @Override
    @Transactional
    public Prediction runPrediction(Long hospitalId, String patientFeaturesJson) {
        log.info("Running prediction for hospitalId: {}", hospitalId);

        Prediction prediction = new Prediction();
        if (hospitalId != null) {
            prediction.setHospital(hospitalRepository.findById(hospitalId).orElse(null));
        }

        // Find active model version
        ModelVersion activeModel = modelVersionRepository.findByIsActiveTrue().orElse(null);
        prediction.setModelVersion(activeModel);
        prediction.setPatientFeatures(patientFeaturesJson);

        String result = "Mock Result: High Risk";
        try {
            org.springframework.http.HttpHeaders headers = new org.springframework.http.HttpHeaders();
            headers.setContentType(org.springframework.http.MediaType.APPLICATION_JSON);
            org.springframework.http.HttpEntity<String> request =
                    new org.springframework.http.HttpEntity<>(patientFeaturesJson, headers);

            java.util.Map<String, String> response = restTemplate.postForObject(
                    mlServiceUrl + "/predict", request, java.util.Map.class);
            if (response != null && response.containsKey("prediction")) {
                result = response.get("prediction");
            }
        } catch (Exception e) {
            log.error("Failed to run prediction in ML service", e);
        }
        prediction.setResult(result);

        return predictionRepository.save(prediction);
    }
}
