package com.fl.backend.entity;

import jakarta.persistence.*;
import lombok.Data;

@Data
@Entity
@Table(name = "federated_round")
public class FederatedRound {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "session_id", nullable = false)
    private TrainingSession session;

    @Column(name = "round_number", nullable = false)
    private Integer roundNumber;

    @Column(name = "global_accuracy")
    private Double globalAccuracy;

    @Column(name = "global_loss")
    private Double globalLoss;

    @Column(name = "checkpoint_path", length = 500)
    private String checkpointPath;
}
