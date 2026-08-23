package com.fl.backend.repository;

import com.fl.backend.entity.ClientRoundStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ClientRoundStatusRepository extends JpaRepository<ClientRoundStatus, Long> {
    List<ClientRoundStatus> findByHospitalId(Long hospitalId);
    List<ClientRoundStatus> findByRoundId(Long roundId);
}
