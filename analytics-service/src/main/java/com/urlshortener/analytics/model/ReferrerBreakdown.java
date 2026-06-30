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
        name = "referrer_breakdown",
        schema = "analytics",
        uniqueConstraints = @UniqueConstraint(columnNames = {"short_code", "referrer_domain"}))
public class ReferrerBreakdown {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "short_code", nullable = false)
    private String shortCode;

    @Column(name = "referrer_domain", nullable = false)
    private String referrerDomain;

    @Column(name = "click_count", nullable = false)
    private long clickCount;

    protected ReferrerBreakdown() {
        // JPA
    }

    public ReferrerBreakdown(String shortCode, String referrerDomain) {
        this.shortCode = shortCode;
        this.referrerDomain = referrerDomain;
        this.clickCount = 0;
    }

    public Long getId() {
        return id;
    }

    public String getShortCode() {
        return shortCode;
    }

    public String getReferrerDomain() {
        return referrerDomain;
    }

    public long getClickCount() {
        return clickCount;
    }

    public void increment() {
        this.clickCount += 1;
    }
}
