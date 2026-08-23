package com.fl.backend.entity;

import jakarta.persistence.*;
import lombok.EqualsAndHashCode;

@Data
@EqualsAndHashCode(callSuper = false)
@Entity
@Table(name = "training_session")
public class TrainingSession extends Auditable {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String status; // PENDING, IN_PROGRESS, COMPLETE, FAILED

    @Column(name = "total_rounds", nullable = false)
    private Integer totalRounds;

    @Column(name = "idempotency_key", nullable = false, unique = true)
    private String idempotencyKey;
}
