package com.urlshortener.analytics.repository;

import com.urlshortener.analytics.model.HourlyClickBucket;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface HourlyClickBucketRepository extends JpaRepository<HourlyClickBucket, Long> {
    Optional<HourlyClickBucket> findByShortCodeAndBucketStart(String shortCode, Instant bucketStart);

    List<HourlyClickBucket> findByShortCodeOrderByBucketStartAsc(String shortCode);
}
