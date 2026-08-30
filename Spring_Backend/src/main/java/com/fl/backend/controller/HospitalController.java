package com.fl.backend.controller;

import com.fl.backend.entity.Hospital;
import com.fl.backend.entity.User;
import com.fl.backend.repository.HospitalRepository;
import com.fl.backend.repository.UserRepository;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/hospitals")
@RequiredArgsConstructor
public class HospitalController {

    private final HospitalRepository hospitalRepository;
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    @Data
    public static class AddHospitalRequest {
        private String name;
        private String contactEmail;
        private String username;
        private String password;
    }

    @PostMapping
    @Transactional
    public ResponseEntity<Hospital> addHospital(@RequestBody AddHospitalRequest request) {
        Hospital hospital = new Hospital();
        hospital.setName(request.getName());
        hospital.setContactEmail(request.getContactEmail());
        hospital = hospitalRepository.save(hospital);

        User user = new User();
        user.setUsername(request.getUsername());
        user.setPasswordHash(passwordEncoder.encode(request.getPassword()));
        user.setRole("HOSPITAL");
        user.setHospital(hospital);
        userRepository.save(user);

        return ResponseEntity.ok(hospital);
    }

    @GetMapping
    public ResponseEntity<List<Hospital>> getHospitals() {
        return ResponseEntity.ok(hospitalRepository.findAll());
    }

    @Data
    public static class StatusUpdateRequest {
        private String status;
    }

    @PutMapping("/{id}/status")
    @Transactional
    public ResponseEntity<Hospital> updateStatus(@PathVariable Long id, @RequestBody StatusUpdateRequest request) {
        Hospital hospital = hospitalRepository.findById(id).orElseThrow();
        hospital.setStatus(request.getStatus());
        return ResponseEntity.ok(hospitalRepository.save(hospital));
    }
}
