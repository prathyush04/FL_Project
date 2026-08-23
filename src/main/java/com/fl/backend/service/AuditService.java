package com.fl.backend.service;

import com.fl.backend.entity.AuditLog;

public interface AuditService {
    void logAction(String username, String action, String resourceId, String ipAddress);
}
