package com.fl.backend.controller;

import com.fl.backend.dto.AuthRequest;
import com.fl.backend.dto.AuthResponse;
import com.fl.backend.entity.User;
import com.fl.backend.security.CustomUserDetailsService;
import com.fl.backend.security.JwtUtil;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthenticationManager authenticationManager;
    private final CustomUserDetailsService userDetailsService;
    private final JwtUtil jwtUtil;

    @PostMapping("/login")
    public ResponseEntity<AuthResponse> login(@Valid @RequestBody AuthRequest request) {
        authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(request.getUsername(), request.getPassword())
        );

        UserDetails userDetails = userDetailsService.loadUserByUsername(request.getUsername());
        User user = userDetailsService.getUserByUsername(request.getUsername());
        Long hospitalId = user.getHospital() != null ? user.getHospital().getId() : null;
        
        String token = jwtUtil.generateToken(userDetails, hospitalId);
        return ResponseEntity.ok(new AuthResponse(token, user.getRole(), hospitalId));
    }
}
