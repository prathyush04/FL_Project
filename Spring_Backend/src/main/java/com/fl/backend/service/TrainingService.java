package com.fl.backend.service;

import com.fl.backend.entity.TrainingSession;

public interface TrainingService {
    TrainingSession startTraining(Integer totalRounds);
    TrainingSession getTrainingStatus(Long sessionId);
    void joinTraining(Long hospitalId, String csvData);
}
