package com.urlshortener.analytics.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.when;

import com.urlshortener.analytics.repository.DeviceBreakdownRepository;
import com.urlshortener.analytics.repository.HourlyClickBucketRepository;
import com.urlshortener.analytics.repository.ReferrerBreakdownRepository;
import com.urlshortener.analytics.repository.UrlClickStatsRepository;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class AnalyticsQueryServiceTest {

    @Mock private UrlClickStatsRepository urlClickStatsRepository;
    @Mock private HourlyClickBucketRepository hourlyClickBucketRepository;
    @Mock private ReferrerBreakdownRepository referrerBreakdownRepository;
    @Mock private DeviceBreakdownRepository deviceBreakdownRepository;

    @Test
    void unknownShortCodeReturnsZeroedStatsInsteadOfThrowing() {
        when(urlClickStatsRepository.findByShortCode("nope")).thenReturn(Optional.empty());
        when(hourlyClickBucketRepository.findByShortCodeOrderByBucketStartAsc("nope"))
                .thenReturn(List.of());
        when(referrerBreakdownRepository.findByShortCode("nope")).thenReturn(List.of());
        when(deviceBreakdownRepository.findByShortCode("nope")).thenReturn(List.of());

        var service =
                new AnalyticsQueryService(
                        urlClickStatsRepository,
                        hourlyClickBucketRepository,
                        referrerBreakdownRepository,
                        deviceBreakdownRepository);

        var stats = service.getStats("nope");

        assertThat(stats.totalClicks()).isZero();
        assertThat(stats.lastClickedAt()).isNull();
        assertThat(stats.hourlyClicks()).isEmpty();
        assertThat(stats.dailyClicks()).isEmpty();
    }
}
