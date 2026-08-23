package com.fl.backend.service.impl;

import com.fl.backend.entity.ModelVersion;
import com.fl.backend.entity.Prediction;
import com.fl.backend.repository.HospitalRepository;
import com.fl.backend.repository.ModelVersionRepository;
import com.fl.backend.repository.PredictionRepository;
import com.fl.backend.service.PredictionService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Slf4j
@Service
@RequiredArgsConstructor
public class PredictionServiceImpl implements PredictionService {

    private final PredictionRepository predictionRepository;
    private final HospitalRepository hospitalRepository;
    private final ModelVersionRepository modelVersionRepository;

    @Override
    @Transactional
    public Prediction runPrediction(Long hospitalId, String patientFeaturesJson) {
        log.info("Running prediction for hospitalId: {}", hospitalId);
        // TODO: Replace with gRPC client call to FastAPI to run prediction
        
        Prediction prediction = new Prediction();
        if (hospitalId != null) {
            prediction.setHospital(hospitalRepository.findById(hospitalId).orElse(null));
        }
        
        // Find active model version
        ModelVersion activeModel = modelVersionRepository.findByIsActiveTrue().orElse(null);
        prediction.setModelVersion(activeModel);
        
        prediction.setPatientFeatures(patientFeaturesJson);
        
        // Mock prediction result
        prediction.setResult("Mock Result: High Risk");
        
        return predictionRepository.save(prediction);
    }
}
