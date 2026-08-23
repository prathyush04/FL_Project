package com.fl.backend.repository;

import com.fl.backend.entity.TrainingSession;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface TrainingSessionRepository extends JpaRepository<TrainingSession, Long> {
    Optional<TrainingSession> findByIdempotencyKey(String idempotencyKey);
}
