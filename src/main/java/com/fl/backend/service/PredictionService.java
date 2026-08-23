package com.fl.backend.service;

import com.fl.backend.entity.Prediction;

public interface PredictionService {
    Prediction runPrediction(Long hospitalId, String patientFeaturesJson);
}
