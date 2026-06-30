package com.urlshortener.analytics.controller;

import com.urlshortener.analytics.dto.AnalyticsStatsResponse;
import com.urlshortener.analytics.service.AnalyticsQueryService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class AnalyticsController {

    private final AnalyticsQueryService analyticsQueryService;

    public AnalyticsController(AnalyticsQueryService analyticsQueryService) {
        this.analyticsQueryService = analyticsQueryService;
    }

    // Returns zeroed-out stats for an unknown short_code rather than 404:
    // this service doesn't own short-code validity, core-service does -
    // "no clicks recorded" and "doesn't exist" look the same from here,
    // and that's fine because core-service is what fronts the public API.
    @GetMapping("/api/analytics/{shortCode}/stats")
    public AnalyticsStatsResponse getStats(@PathVariable String shortCode) {
        return analyticsQueryService.getStats(shortCode);
    }
}
