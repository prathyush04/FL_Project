package com.fl.backend.dto;

import lombok.Data;

@Data
public class ComparisonResultDto {
    private Long id;
    private Long sessionId;
    private String approachType;
    private Double accuracy;
    private Double f1Score;
    private Long trainingTimeSec;
}
