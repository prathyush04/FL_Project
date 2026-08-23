package com.fl.backend.dto;

import lombok.Data;

@Data
public class FederatedRoundDto {
    private Long id;
    private Long sessionId;
    private Integer roundNumber;
    private Double globalAccuracy;
    private Double globalLoss;
    private String checkpointPath;
}
