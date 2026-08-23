package com.fl.backend.controller;

import com.fl.backend.dto.ComparisonResultDto;
import com.fl.backend.dto.FederatedRoundDto;
import com.fl.backend.mapper.DtoMapper;
import com.fl.backend.repository.ComparisonResultRepository;
import com.fl.backend.repository.FederatedRoundRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/v1/metrics")
@RequiredArgsConstructor
public class MetricsController {

    private final FederatedRoundRepository federatedRoundRepository;
    private final ComparisonResultRepository comparisonResultRepository;
    private final DtoMapper mapper;

    @GetMapping("/global")
    public ResponseEntity<List<FederatedRoundDto>> getGlobalMetrics(@RequestParam Long sessionId) {
        return ResponseEntity.ok(federatedRoundRepository.findBySessionId(sessionId).stream()
                .map(mapper::toFederatedRoundDto)
                .collect(Collectors.toList()));
    }

    @GetMapping("/comparison")
    public ResponseEntity<List<ComparisonResultDto>> getComparisonMetrics(@RequestParam Long sessionId) {
        return ResponseEntity.ok(comparisonResultRepository.findBySessionId(sessionId).stream()
                .map(mapper::toComparisonResultDto)
                .collect(Collectors.toList()));
    }
}
