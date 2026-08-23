package com.fl.backend.entity;

import jakarta.persistence.*;
import lombok.Data;

@Data
@Entity
@Table(name = "model_version")
public class ModelVersion {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "session_id", nullable = false)
    private TrainingSession session;

    @Column(name = "round_number", nullable = false)
    private Integer roundNumber;

    @Column(name = "model_path", length = 500)
    private String modelPath;

    private Double accuracy;
    
    @Column(name = "`precision`")
    private Double precision;
    
    private Double recall;
    private Double f1;

    @Column(name = "is_active", columnDefinition = "boolean default false")
    private Boolean isActive;
}
