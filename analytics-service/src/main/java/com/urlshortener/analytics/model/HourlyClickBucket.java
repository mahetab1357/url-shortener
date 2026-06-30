package com.urlshortener.analytics.model;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;
import java.time.Instant;

@Entity
@Table(
        name = "hourly_click_buckets",
        schema = "analytics",
        uniqueConstraints = @UniqueConstraint(columnNames = {"short_code", "bucket_start"}))
public class HourlyClickBucket {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "short_code", nullable = false)
    private String shortCode;

    @Column(name = "bucket_start", nullable = false)
    private Instant bucketStart;

    @Column(name = "click_count", nullable = false)
    private long clickCount;

    protected HourlyClickBucket() {
        // JPA
    }

    public HourlyClickBucket(String shortCode, Instant bucketStart) {
        this.shortCode = shortCode;
        this.bucketStart = bucketStart;
        this.clickCount = 0;
    }

    public Long getId() {
        return id;
    }

    public String getShortCode() {
        return shortCode;
    }

    public Instant getBucketStart() {
        return bucketStart;
    }

    public long getClickCount() {
        return clickCount;
    }

    public void increment() {
        this.clickCount += 1;
    }
}
