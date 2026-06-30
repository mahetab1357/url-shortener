package com.urlshortener.analytics.model;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;

@Entity
@Table(
        name = "device_breakdown",
        schema = "analytics",
        uniqueConstraints =
                @UniqueConstraint(columnNames = {"short_code", "device_type", "browser"}))
public class DeviceBreakdown {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "short_code", nullable = false)
    private String shortCode;

    @Column(name = "device_type", nullable = false)
    private String deviceType;

    @Column(name = "browser", nullable = false)
    private String browser;

    @Column(name = "click_count", nullable = false)
    private long clickCount;

    protected DeviceBreakdown() {
        // JPA
    }

    public DeviceBreakdown(String shortCode, String deviceType, String browser) {
        this.shortCode = shortCode;
        this.deviceType = deviceType;
        this.browser = browser;
        this.clickCount = 0;
    }

    public Long getId() {
        return id;
    }

    public String getShortCode() {
        return shortCode;
    }

    public String getDeviceType() {
        return deviceType;
    }

    public String getBrowser() {
        return browser;
    }

    public long getClickCount() {
        return clickCount;
    }

    public void increment() {
        this.clickCount += 1;
    }
}
