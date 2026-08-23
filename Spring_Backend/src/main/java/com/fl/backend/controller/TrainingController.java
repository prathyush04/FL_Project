package com.fl.backend.controller;

import com.fl.backend.dto.TrainingSessionDto;
import com.fl.backend.entity.TrainingSession;
import com.fl.backend.mapper.DtoMapper;
import com.fl.backend.service.AuditService;
import com.fl.backend.service.TrainingService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/training")
@RequiredArgsConstructor
public class TrainingController {

    private final TrainingService trainingService;
    private final AuditService auditService;
    private final DtoMapper mapper;

    @PostMapping("/start")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<TrainingSessionDto> startTraining(@RequestParam(defaultValue = "10") Integer totalRounds,
                                                         Authentication authentication) {
        TrainingSession session = trainingService.startTraining(totalRounds);
        auditService.logAction(authentication.getName(), "START_TRAINING", session.getId().toString(), null);
        return ResponseEntity.ok(mapper.toTrainingSessionDto(session));
    }

    @GetMapping("/status")
    public ResponseEntity<TrainingSessionDto> getStatus(@RequestParam Long sessionId) {
        TrainingSession status = trainingService.getTrainingStatus(sessionId);
        if (status == null) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(mapper.toTrainingSessionDto(status));
    }
}
