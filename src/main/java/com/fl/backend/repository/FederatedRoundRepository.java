package com.fl.backend.repository;

import com.fl.backend.entity.FederatedRound;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface FederatedRoundRepository extends JpaRepository<FederatedRound, Long> {
    List<FederatedRound> findBySessionId(Long sessionId);
}
