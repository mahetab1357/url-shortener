package com.urlshortener.analytics.service;

import com.urlshortener.analytics.dto.AnalyticsStatsResponse;
import com.urlshortener.analytics.dto.AnalyticsStatsResponse.DailyBucketDto;
import com.urlshortener.analytics.dto.AnalyticsStatsResponse.DeviceBreakdownDto;
import com.urlshortener.analytics.dto.AnalyticsStatsResponse.HourlyBucketDto;
import com.urlshortener.analytics.dto.AnalyticsStatsResponse.ReferrerBreakdownDto;
import com.urlshortener.analytics.model.HourlyClickBucket;
import com.urlshortener.analytics.repository.DeviceBreakdownRepository;
import com.urlshortener.analytics.repository.HourlyClickBucketRepository;
import com.urlshortener.analytics.repository.ReferrerBreakdownRepository;
import com.urlshortener.analytics.repository.UrlClickStatsRepository;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.springframework.stereotype.Service;

@Service
public class AnalyticsQueryService {

    private final UrlClickStatsRepository urlClickStatsRepository;
    private final HourlyClickBucketRepository hourlyClickBucketRepository;
    private final ReferrerBreakdownRepository referrerBreakdownRepository;
    private final DeviceBreakdownRepository deviceBreakdownRepository;

    public AnalyticsQueryService(
            UrlClickStatsRepository urlClickStatsRepository,
            HourlyClickBucketRepository hourlyClickBucketRepository,
            ReferrerBreakdownRepository referrerBreakdownRepository,
            DeviceBreakdownRepository deviceBreakdownRepository) {
        this.urlClickStatsRepository = urlClickStatsRepository;
        this.hourlyClickBucketRepository = hourlyClickBucketRepository;
        this.referrerBreakdownRepository = referrerBreakdownRepository;
        this.deviceBreakdownRepository = deviceBreakdownRepository;
    }

    public AnalyticsStatsResponse getStats(String shortCode) {
        var statsRow = urlClickStatsRepository.findByShortCode(shortCode);
        long totalClicks = statsRow.map(s -> s.getTotalClicks()).orElse(0L);
        var lastClickedAt = statsRow.map(s -> s.getLastClickedAt()).orElse(null);

        List<HourlyClickBucket> hourlyBuckets =
                hourlyClickBucketRepository.findByShortCodeOrderByBucketStartAsc(shortCode);

        List<HourlyBucketDto> hourlyDtos =
                hourlyBuckets.stream()
                        .map(b -> new HourlyBucketDto(b.getBucketStart(), b.getClickCount()))
                        .toList();

        List<DailyBucketDto> dailyDtos = rollUpToDaily(hourlyBuckets);

        List<DeviceBreakdownDto> deviceDtos =
                deviceBreakdownRepository.findByShortCode(shortCode).stream()
                        .map(d -> new DeviceBreakdownDto(d.getDeviceType(), d.getBrowser(), d.getClickCount()))
                        .toList();

        List<ReferrerBreakdownDto> referrerDtos =
                referrerBreakdownRepository.findByShortCode(shortCode).stream()
                        .map(r -> new ReferrerBreakdownDto(r.getReferrerDomain(), r.getClickCount()))
                        .toList();

        return new AnalyticsStatsResponse(
                shortCode, totalClicks, lastClickedAt, hourlyDtos, dailyDtos, deviceDtos, referrerDtos);
    }

    /** Daily totals are derived from the hourly buckets at query time rather
     * than maintained as a separate table - one fewer write path to keep
     * consistent, at the cost of a small in-memory roll-up here. */
    private List<DailyBucketDto> rollUpToDaily(List<HourlyClickBucket> hourlyBuckets) {
        DateTimeFormatter dayFormatter = DateTimeFormatter.ofPattern("yyyy-MM-dd").withZone(ZoneOffset.UTC);
        Map<String, Long> byDay = new LinkedHashMap<>();
        for (HourlyClickBucket bucket : hourlyBuckets) {
            String day = dayFormatter.format(bucket.getBucketStart());
            byDay.merge(day, bucket.getClickCount(), Long::sum);
        }
        return byDay.entrySet().stream().map(e -> new DailyBucketDto(e.getKey(), e.getValue())).toList();
    }
}
