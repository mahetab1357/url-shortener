package com.urlshortener.analytics.repository;

import com.urlshortener.analytics.model.UrlClickStats;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface UrlClickStatsRepository extends JpaRepository<UrlClickStats, Long> {
    Optional<UrlClickStats> findByShortCode(String shortCode);
}
