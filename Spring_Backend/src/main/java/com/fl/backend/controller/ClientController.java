package com.fl.backend.controller;

import com.fl.backend.dto.HospitalDto;
import com.fl.backend.mapper.DtoMapper;
import com.fl.backend.repository.HospitalRepository;
import com.fl.backend.security.JwtUtil;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/v1/clients")
@RequiredArgsConstructor
public class ClientController {

    private final HospitalRepository hospitalRepository;
    private final JwtUtil jwtUtil;
    private final DtoMapper mapper;

    @GetMapping
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<List<HospitalDto>> getAllClients() {
        return ResponseEntity.ok(hospitalRepository.findAll().stream()
                .map(mapper::toHospitalDto)
                .collect(Collectors.toList()));
    }

    @GetMapping("/me")
    @PreAuthorize("hasRole('HOSPITAL')")
    public ResponseEntity<HospitalDto> getMyClient(HttpServletRequest request) {
        String token = request.getHeader("Authorization").substring(7);
        Long hospitalId = jwtUtil.extractHospitalId(token);
        
        if (hospitalId == null) {
            return ResponseEntity.badRequest().build();
        }
        
        return hospitalRepository.findById(hospitalId)
                .map(mapper::toHospitalDto)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }
}
