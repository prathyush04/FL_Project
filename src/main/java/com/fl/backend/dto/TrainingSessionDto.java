package com.fl.backend.dto;

import lombok.Data;

@Data
public class TrainingSessionDto {
    private Long id;
    private String status;
    private Integer totalRounds;
    private String idempotencyKey;
}
