package com.fl.backend.service.impl;

import com.fl.backend.entity.AuditLog;
import com.fl.backend.repository.AuditLogRepository;
import com.fl.backend.repository.UserRepository;
import com.fl.backend.service.AuditService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Slf4j
@Service
@RequiredArgsConstructor
public class AuditServiceImpl implements AuditService {

    private final AuditLogRepository auditLogRepository;
    private final UserRepository userRepository;

    @Override
    @Transactional
    public void logAction(String username, String action, String resourceId, String ipAddress) {
        log.info("Audit log entry: User={}, Action={}, Resource={}, IP={}", username, action, resourceId, ipAddress);
        AuditLog auditLog = new AuditLog();
        if (username != null) {
            userRepository.findByUsername(username).ifPresent(auditLog::setUser);
        }
        auditLog.setAction(action);
        auditLog.setResourceId(resourceId);
        auditLog.setIpAddress(ipAddress);
        auditLogRepository.save(auditLog);
    }
}
