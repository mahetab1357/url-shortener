package com.urlshortener.analytics.dto;

import java.time.Instant;
import java.util.List;

public record AnalyticsStatsResponse(
        String shortCode,
        long totalClicks,
        Instant lastClickedAt,
        List<HourlyBucketDto> hourlyClicks,
        List<DailyBucketDto> dailyClicks,
        List<DeviceBreakdownDto> deviceBreakdown,
        List<ReferrerBreakdownDto> referrerBreakdown) {

    public record HourlyBucketDto(Instant hourStart, long count) {}

    public record DailyBucketDto(String date, long count) {}

    public record DeviceBreakdownDto(String deviceType, String browser, long count) {}

    public record ReferrerBreakdownDto(String referrerDomain, long count) {}
}
