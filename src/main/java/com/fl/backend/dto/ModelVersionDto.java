package com.fl.backend.dto;

import lombok.Data;

@Data
public class ModelVersionDto {
    private Long id;
    private Long sessionId;
    private Integer roundNumber;
    private String modelPath;
    private Double accuracy;
    private Double precision;
    private Double recall;
    private Double f1;
    private Boolean isActive;
}
