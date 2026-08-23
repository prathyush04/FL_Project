package com.fl.backend.controller;

import com.fl.backend.dto.PredictionDto;
import com.fl.backend.entity.Prediction;
import com.fl.backend.mapper.DtoMapper;
import com.fl.backend.repository.PredictionRepository;
import com.fl.backend.security.JwtUtil;
import com.fl.backend.service.AuditService;
import com.fl.backend.service.PredictionService;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/v1")
@RequiredArgsConstructor
public class PredictionController {

    private final PredictionService predictionService;
    private final PredictionRepository predictionRepository;
    private final JwtUtil jwtUtil;
    private final AuditService auditService;
    private final DtoMapper mapper;

    @PostMapping("/predict")
    public ResponseEntity<PredictionDto> runPrediction(@RequestBody String patientFeaturesJson,
                                                    HttpServletRequest request,
                                                    Authentication authentication) {
        String token = request.getHeader("Authorization").substring(7);
        Long hospitalId = jwtUtil.extractHospitalId(token);
        
        Prediction prediction = predictionService.runPrediction(hospitalId, patientFeaturesJson);
        auditService.logAction(authentication.getName(), "PREDICTION_RUN", prediction.getId().toString(), request.getRemoteAddr());
        
        return ResponseEntity.ok(mapper.toPredictionDto(prediction));
    }

    @GetMapping("/predictions")
    public ResponseEntity<List<PredictionDto>> getPredictions(HttpServletRequest request,
                                                           Authentication authentication) {
        List<Prediction> predictions;
        if (authentication.getAuthorities().stream().anyMatch(a -> a.getAuthority().equals("ROLE_ADMIN"))) {
            predictions = predictionRepository.findAll();
        } else {
            String token = request.getHeader("Authorization").substring(7);
            Long hospitalId = jwtUtil.extractHospitalId(token);
            if (hospitalId == null) {
                return ResponseEntity.badRequest().build();
            }
            predictions = predictionRepository.findByHospitalId(hospitalId);
        }
        
        return ResponseEntity.ok(predictions.stream()
                .map(mapper::toPredictionDto)
                .collect(Collectors.toList()));
    }
}
