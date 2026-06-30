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
        name = "url_click_stats",
        schema = "analytics",
        uniqueConstraints = @UniqueConstraint(columnNames = "short_code"))
public class UrlClickStats {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "short_code", nullable = false)
    private String shortCode;

    @Column(name = "total_clicks", nullable = false)
    private long totalClicks;

    @Column(name = "last_clicked_at")
    private Instant lastClickedAt;

    protected UrlClickStats() {
        // JPA
    }

    public UrlClickStats(String shortCode) {
        this.shortCode = shortCode;
        this.totalClicks = 0;
    }

    public Long getId() {
        return id;
    }

    public String getShortCode() {
        return shortCode;
    }

    public long getTotalClicks() {
        return totalClicks;
    }

    public Instant getLastClickedAt() {
        return lastClickedAt;
    }

    public void recordClick(Instant clickedAt) {
        this.totalClicks += 1;
        this.lastClickedAt = clickedAt;
    }
}
