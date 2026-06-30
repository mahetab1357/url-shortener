package com.urlshortener.analytics.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.urlshortener.analytics.dto.ClickEventDto;
import com.urlshortener.analytics.model.DeviceBreakdown;
import com.urlshortener.analytics.model.HourlyClickBucket;
import com.urlshortener.analytics.model.ReferrerBreakdown;
import com.urlshortener.analytics.model.UrlClickStats;
import com.urlshortener.analytics.repository.DeviceBreakdownRepository;
import com.urlshortener.analytics.repository.HourlyClickBucketRepository;
import com.urlshortener.analytics.repository.ReferrerBreakdownRepository;
import com.urlshortener.analytics.repository.UrlClickStatsRepository;
import java.time.Instant;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class AggregationServiceTest {

    @Mock private UrlClickStatsRepository urlClickStatsRepository;
    @Mock private HourlyClickBucketRepository hourlyClickBucketRepository;
    @Mock private ReferrerBreakdownRepository referrerBreakdownRepository;
    @Mock private DeviceBreakdownRepository deviceBreakdownRepository;

    private AggregationService aggregationService;

    @BeforeEach
    void setUp() {
        aggregationService =
                new AggregationService(
                        urlClickStatsRepository,
                        hourlyClickBucketRepository,
                        referrerBreakdownRepository,
                        deviceBreakdownRepository,
                        new UserAgentParser(),
                        new ReferrerParser());
    }

    private ClickEventDto sampleEvent(String shortCode) {
        return new ClickEventDto(
                shortCode,
                "2026-06-29T10:15:30Z",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/128.0.0.0 Safari/537.36",
                "https://www.google.com/search",
                "10.0.0.5");
    }

    @Test
    void newShortCodeCreatesStatsRowWithCountOne() {
        when(urlClickStatsRepository.findByShortCode("abc1234")).thenReturn(Optional.empty());
        when(hourlyClickBucketRepository.findByShortCodeAndBucketStart(any(), any()))
                .thenReturn(Optional.empty());
        when(referrerBreakdownRepository.findByShortCodeAndReferrerDomain(any(), any()))
                .thenReturn(Optional.empty());
        when(deviceBreakdownRepository.findByShortCodeAndDeviceTypeAndBrowser(any(), any(), any()))
                .thenReturn(Optional.empty());

        aggregationService.process(sampleEvent("abc1234"));

        ArgumentCaptor<UrlClickStats> captor = ArgumentCaptor.forClass(UrlClickStats.class);
        verify(urlClickStatsRepository).save(captor.capture());
        assertThat(captor.getValue().getTotalClicks()).isEqualTo(1);
        assertThat(captor.getValue().getShortCode()).isEqualTo("abc1234");
    }

    @Test
    void existingShortCodeIncrementsExistingStatsRow() {
        UrlClickStats existing = new UrlClickStats("abc1234");
        existing.recordClick(Instant.parse("2026-06-29T09:00:00Z"));
        when(urlClickStatsRepository.findByShortCode("abc1234")).thenReturn(Optional.of(existing));
        when(hourlyClickBucketRepository.findByShortCodeAndBucketStart(any(), any()))
                .thenReturn(Optional.empty());
        when(referrerBreakdownRepository.findByShortCodeAndReferrerDomain(any(), any()))
                .thenReturn(Optional.empty());
        when(deviceBreakdownRepository.findByShortCodeAndDeviceTypeAndBrowser(any(), any(), any()))
                .thenReturn(Optional.empty());

        aggregationService.process(sampleEvent("abc1234"));

        ArgumentCaptor<UrlClickStats> captor = ArgumentCaptor.forClass(UrlClickStats.class);
        verify(urlClickStatsRepository).save(captor.capture());
        assertThat(captor.getValue().getTotalClicks()).isEqualTo(2);
    }

    @Test
    void existingHourlyBucketIsIncrementedNotDuplicated() {
        Instant clickedAt = Instant.parse("2026-06-29T10:15:30Z");
        Instant bucketStart = Instant.parse("2026-06-29T10:00:00Z");
        HourlyClickBucket existingBucket = new HourlyClickBucket("abc1234", bucketStart);
        existingBucket.increment();

        when(urlClickStatsRepository.findByShortCode(any())).thenReturn(Optional.empty());
        when(hourlyClickBucketRepository.findByShortCodeAndBucketStart("abc1234", bucketStart))
                .thenReturn(Optional.of(existingBucket));
        when(referrerBreakdownRepository.findByShortCodeAndReferrerDomain(any(), any()))
                .thenReturn(Optional.empty());
        when(deviceBreakdownRepository.findByShortCodeAndDeviceTypeAndBrowser(any(), any(), any()))
                .thenReturn(Optional.empty());

        aggregationService.process(sampleEvent("abc1234"));

        ArgumentCaptor<HourlyClickBucket> captor = ArgumentCaptor.forClass(HourlyClickBucket.class);
        verify(hourlyClickBucketRepository).save(captor.capture());
        assertThat(captor.getValue().getClickCount()).isEqualTo(2);
        assertThat(captor.getValue().getBucketStart()).isEqualTo(bucketStart);
    }

    @Test
    void referrerIsExtractedAndAggregatedByDomain() {
        when(urlClickStatsRepository.findByShortCode(any())).thenReturn(Optional.empty());
        when(hourlyClickBucketRepository.findByShortCodeAndBucketStart(any(), any()))
                .thenReturn(Optional.empty());
        when(referrerBreakdownRepository.findByShortCodeAndReferrerDomain("abc1234", "google.com"))
                .thenReturn(Optional.empty());
        when(deviceBreakdownRepository.findByShortCodeAndDeviceTypeAndBrowser(any(), any(), any()))
                .thenReturn(Optional.empty());

        aggregationService.process(sampleEvent("abc1234"));

        ArgumentCaptor<ReferrerBreakdown> captor = ArgumentCaptor.forClass(ReferrerBreakdown.class);
        verify(referrerBreakdownRepository).save(captor.capture());
        assertThat(captor.getValue().getReferrerDomain()).isEqualTo("google.com");
        assertThat(captor.getValue().getClickCount()).isEqualTo(1);
    }

    @Test
    void noReferrerIsAggregatedAsDirect() {
        when(urlClickStatsRepository.findByShortCode(any())).thenReturn(Optional.empty());
        when(hourlyClickBucketRepository.findByShortCodeAndBucketStart(any(), any()))
                .thenReturn(Optional.empty());
        when(referrerBreakdownRepository.findByShortCodeAndReferrerDomain("abc1234", "direct"))
                .thenReturn(Optional.empty());
        when(deviceBreakdownRepository.findByShortCodeAndDeviceTypeAndBrowser(any(), any(), any()))
                .thenReturn(Optional.empty());

        ClickEventDto event =
                new ClickEventDto("abc1234", "2026-06-29T10:15:30Z", "Mozilla/5.0", null, "10.0.0.5");
        aggregationService.process(event);

        ArgumentCaptor<ReferrerBreakdown> captor = ArgumentCaptor.forClass(ReferrerBreakdown.class);
        verify(referrerBreakdownRepository).save(captor.capture());
        assertThat(captor.getValue().getReferrerDomain()).isEqualTo("direct");
    }

    @Test
    void deviceAndBrowserAreParsedAndAggregated() {
        when(urlClickStatsRepository.findByShortCode(any())).thenReturn(Optional.empty());
        when(hourlyClickBucketRepository.findByShortCodeAndBucketStart(any(), any()))
                .thenReturn(Optional.empty());
        when(referrerBreakdownRepository.findByShortCodeAndReferrerDomain(any(), any()))
                .thenReturn(Optional.empty());
        when(deviceBreakdownRepository.findByShortCodeAndDeviceTypeAndBrowser(
                        "abc1234", "Desktop", "Chrome"))
                .thenReturn(Optional.empty());

        aggregationService.process(sampleEvent("abc1234"));

        ArgumentCaptor<DeviceBreakdown> captor = ArgumentCaptor.forClass(DeviceBreakdown.class);
        verify(deviceBreakdownRepository).save(captor.capture());
        assertThat(captor.getValue().getDeviceType()).isEqualTo("Desktop");
        assertThat(captor.getValue().getBrowser()).isEqualTo("Chrome");
        assertThat(captor.getValue().getClickCount()).isEqualTo(1);
    }
}
