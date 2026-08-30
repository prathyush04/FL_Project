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
    private final org.springframework.web.client.RestTemplate restTemplate;

    @Override
    @Transactional
    public TrainingSession startTraining(Integer totalRounds) {
        log.info("Initiating new training session with {} rounds", totalRounds);
        
        try {
            restTemplate.postForObject("http://localhost:8000/server/start", null, String.class);
        } catch (Exception e) {
            log.error("Failed to start FL server in ML service", e);
        }

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
    
    @Override
    public void joinTraining(Long hospitalId, String csvData) {
        log.info("Hospital {} joining training", hospitalId);
        try {
            org.springframework.http.HttpHeaders headers = new org.springframework.http.HttpHeaders();
            headers.setContentType(org.springframework.http.MediaType.APPLICATION_JSON);
            
            // Build JSON manually or use Map to avoid escaping issues
            java.util.Map<String, Object> payload = new java.util.HashMap<>();
            payload.put("client_id", hospitalId);
            payload.put("csv_data", csvData);
            
            org.springframework.http.HttpEntity<java.util.Map<String, Object>> request = new org.springframework.http.HttpEntity<>(payload, headers);
            restTemplate.postForObject("http://localhost:8000/client/start", request, String.class);
        } catch (Exception e) {
            log.error("Failed to start FL client in ML service", e);
        }
    }
}
