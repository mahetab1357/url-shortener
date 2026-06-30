package com.urlshortener.analytics.repository;

import com.urlshortener.analytics.model.ReferrerBreakdown;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ReferrerBreakdownRepository extends JpaRepository<ReferrerBreakdown, Long> {
    Optional<ReferrerBreakdown> findByShortCodeAndReferrerDomain(
            String shortCode, String referrerDomain);

    List<ReferrerBreakdown> findByShortCode(String shortCode);
}
