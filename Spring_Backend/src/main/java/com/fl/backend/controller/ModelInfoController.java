package com.fl.backend.controller;

import com.fl.backend.dto.ModelVersionDto;
import com.fl.backend.mapper.DtoMapper;
import com.fl.backend.repository.ModelVersionRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/model")
@RequiredArgsConstructor
public class ModelInfoController {

    private final ModelVersionRepository modelVersionRepository;
    private final DtoMapper mapper;

    @GetMapping("/info")
    public ResponseEntity<ModelVersionDto> getModelInfo() {
        return modelVersionRepository.findByIsActiveTrue()
                .map(mapper::toModelVersionDto)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }
}
