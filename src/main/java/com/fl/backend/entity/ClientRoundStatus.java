package com.fl.backend.entity;

import jakarta.persistence.*;
import lombok.Data;

@Data
@Entity
@Table(name = "client_round_status")
public class ClientRoundStatus {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "round_id", nullable = false)
    private FederatedRound round;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "hospital_id", nullable = false)
    private Hospital hospital;

    @Column(name = "local_accuracy")
    private Double localAccuracy;

    @Column(name = "local_loss")
    private Double localLoss;

    @Column(name = "sample_count")
    private Integer sampleCount;
}
