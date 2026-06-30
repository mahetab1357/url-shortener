package com.urlshortener.analytics.repository;

import com.urlshortener.analytics.model.DeviceBreakdown;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface DeviceBreakdownRepository extends JpaRepository<DeviceBreakdown, Long> {
    Optional<DeviceBreakdown> findByShortCodeAndDeviceTypeAndBrowser(
            String shortCode, String deviceType, String browser);

    List<DeviceBreakdown> findByShortCode(String shortCode);
}
