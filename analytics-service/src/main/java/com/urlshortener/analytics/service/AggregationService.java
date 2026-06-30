package com.urlshortener.analytics.service;

import com.urlshortener.analytics.dto.ClickEventDto;
import com.urlshortener.analytics.model.DeviceBreakdown;
import com.urlshortener.analytics.model.HourlyClickBucket;
import com.urlshortener.analytics.model.ReferrerBreakdown;
import com.urlshortener.analytics.model.UrlClickStats;
import com.urlshortener.analytics.repository.DeviceBreakdownRepository;
import com.urlshortener.analytics.repository.HourlyClickBucketRepository;
import com.urlshortener.analytics.repository.ReferrerBreakdownRepository;
import com.urlshortener.analytics.repository.UrlClickStatsRepository;
import com.urlshortener.analytics.service.UserAgentParser.ParsedUserAgent;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * Increments all aggregate tables for a single click event. Read-then-write
 * (find existing row, mutate, save) rather than an atomic SQL upsert -
 * correct because RabbitListener processes one message at a time on a
 * single consumer thread, so there's no concurrent writer to race against.
 * Scaling this service to multiple replicas/consumer threads would require
 * switching to atomic upserts or row-level locking.
 */
@Service
public class AggregationService {

    private final UrlClickStatsRepository urlClickStatsRepository;
    private final HourlyClickBucketRepository hourlyClickBucketRepository;
    private final ReferrerBreakdownRepository referrerBreakdownRepository;
    private final DeviceBreakdownRepository deviceBreakdownRepository;
    private final UserAgentParser userAgentParser;
    private final ReferrerParser referrerParser;

    public AggregationService(
            UrlClickStatsRepository urlClickStatsRepository,
            HourlyClickBucketRepository hourlyClickBucketRepository,
            ReferrerBreakdownRepository referrerBreakdownRepository,
            DeviceBreakdownRepository deviceBreakdownRepository,
            UserAgentParser userAgentParser,
            ReferrerParser referrerParser) {
        this.urlClickStatsRepository = urlClickStatsRepository;
        this.hourlyClickBucketRepository = hourlyClickBucketRepository;
        this.referrerBreakdownRepository = referrerBreakdownRepository;
        this.deviceBreakdownRepository = deviceBreakdownRepository;
        this.userAgentParser = userAgentParser;
        this.referrerParser = referrerParser;
    }

    @Transactional
    public void process(ClickEventDto event) {
        Instant clickedAt = Instant.parse(event.timestamp());
        String shortCode = event.shortCode();

        recordTotal(shortCode, clickedAt);
        recordHourlyBucket(shortCode, clickedAt);
        recordReferrer(shortCode, event.referrer());
        recordDevice(shortCode, event.userAgent());
    }

    private void recordTotal(String shortCode, Instant clickedAt) {
        UrlClickStats stats =
                urlClickStatsRepository
                        .findByShortCode(shortCode)
                        .orElseGet(() -> new UrlClickStats(shortCode));
        stats.recordClick(clickedAt);
        urlClickStatsRepository.save(stats);
    }

    private void recordHourlyBucket(String shortCode, Instant clickedAt) {
        Instant bucketStart = clickedAt.truncatedTo(ChronoUnit.HOURS);
        HourlyClickBucket bucket =
                hourlyClickBucketRepository
                        .findByShortCodeAndBucketStart(shortCode, bucketStart)
                        .orElseGet(() -> new HourlyClickBucket(shortCode, bucketStart));
        bucket.increment();
        hourlyClickBucketRepository.save(bucket);
    }

    private void recordReferrer(String shortCode, String referrer) {
        String domain = referrerParser.extractDomain(referrer);
        ReferrerBreakdown breakdown =
                referrerBreakdownRepository
                        .findByShortCodeAndReferrerDomain(shortCode, domain)
                        .orElseGet(() -> new ReferrerBreakdown(shortCode, domain));
        breakdown.increment();
        referrerBreakdownRepository.save(breakdown);
    }

    private void recordDevice(String shortCode, String userAgent) {
        ParsedUserAgent parsed = userAgentParser.parse(userAgent);
        DeviceBreakdown breakdown =
                deviceBreakdownRepository
                        .findByShortCodeAndDeviceTypeAndBrowser(
                                shortCode, parsed.deviceType(), parsed.browser())
                        .orElseGet(
                                () ->
                                        new DeviceBreakdown(
                                                shortCode, parsed.deviceType(), parsed.browser()));
        breakdown.increment();
        deviceBreakdownRepository.save(breakdown);
    }
}
