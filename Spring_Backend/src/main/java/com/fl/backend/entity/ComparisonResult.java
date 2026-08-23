package com.fl.backend.entity;

import jakarta.persistence.*;
import lombok.Data;

@Data
@Entity
@Table(name = "comparison_result")
public class ComparisonResult {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "session_id", nullable = false)
    private TrainingSession session;

    @Column(name = "approach_type", length = 50)
    private String approachType; // e.g., FEDERATED, CENTRALIZED

    private Double accuracy;

    @Column(name = "f1_score")
    private Double f1Score;

    @Column(name = "training_time_sec")
    private Long trainingTimeSec;
}
