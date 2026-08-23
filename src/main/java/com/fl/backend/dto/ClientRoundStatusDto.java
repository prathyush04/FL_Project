package com.fl.backend.dto;

import lombok.Data;

@Data
public class ClientRoundStatusDto {
    private Long id;
    private Long roundId;
    private Long hospitalId;
    private Double localAccuracy;
    private Double localLoss;
    private Integer sampleCount;
}
