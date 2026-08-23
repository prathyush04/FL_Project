package com.fl.backend.service.impl;

import com.fl.backend.entity.TrainingSession;
import com.fl.backend.repository.TrainingSessionRepository;
import com.fl.backend.service.TrainingService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
public class TrainingServiceImpl implements TrainingService {

    private final TrainingSessionRepository trainingSessionRepository;

    @Override
    @Transactional
    public TrainingSession startTraining(Integer totalRounds) {
        log.info("Initiating new training session with {} rounds", totalRounds);
        // TODO: Replace with gRPC client call to FastAPI to actually start training

        TrainingSession session = new TrainingSession();
        session.setStatus("IN_PROGRESS");
        session.setTotalRounds(totalRounds);
        session.setIdempotencyKey(UUID.randomUUID().toString());

        return trainingSessionRepository.save(session);
    }
    
    @Override
    @Transactional(readOnly = true)
    public TrainingSession getTrainingStatus(Long sessionId) {
        log.debug("Fetching training status for session ID: {}", sessionId);
        return trainingSessionRepository.findById(sessionId).orElse(null);
    }
}
