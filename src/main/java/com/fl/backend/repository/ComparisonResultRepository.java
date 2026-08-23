package com.fl.backend.repository;

import com.fl.backend.entity.ComparisonResult;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ComparisonResultRepository extends JpaRepository<ComparisonResult, Long> {
    List<ComparisonResult> findBySessionId(Long sessionId);
}
