package com.fl.backend.dto;

import lombok.Data;

@Data
public class PredictionDto {
    private Long id;
    private Long hospitalId;
    private Long modelVersionId;
    private String patientFeatures;
    private String result;
}
