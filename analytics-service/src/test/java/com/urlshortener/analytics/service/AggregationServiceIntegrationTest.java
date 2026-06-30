package com.urlshortener.analytics.service;

import static org.assertj.core.api.Assertions.assertThat;

import com.urlshortener.analytics.dto.ClickEventDto;
import com.urlshortener.analytics.repository.DeviceBreakdownRepository;
import com.urlshortener.analytics.repository.HourlyClickBucketRepository;
import com.urlshortener.analytics.repository.ReferrerBreakdownRepository;
import com.urlshortener.analytics.repository.UrlClickStatsRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.jdbc.AutoConfigureTestDatabase;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.context.annotation.Import;

/** Exercises AggregationService against a real (H2, Postgres-compatibility
 * mode) Spring Data JPA stack rather than mocks, to prove the read-then-
 * increment logic actually accumulates correctly across several events -
 * including two events landing in the same hour bucket and two in
 * different ones. */
@DataJpaTest(
        properties = {
            "spring.datasource.url=jdbc:h2:mem:analytics_test_" + "${random.uuid};DB_CLOSE_DELAY=-1;MODE=PostgreSQL",
            "spring.jpa.hibernate.ddl-auto=update",
            "spring.jpa.properties.hibernate.default_schema=analytics",
            "spring.sql.init.mode=always"
        })
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@Import({AggregationService.class, UserAgentParser.class, ReferrerParser.class})
class AggregationServiceIntegrationTest {

    @Autowired private AggregationService aggregationService;
    @Autowired private UrlClickStatsRepository urlClickStatsRepository;
    @Autowired private HourlyClickBucketRepository hourlyClickBucketRepository;
    @Autowired private ReferrerBreakdownRepository referrerBreakdownRepository;
    @Autowired private DeviceBreakdownRepository deviceBreakdownRepository;

    private static final String CHROME_DESKTOP_UA =
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/128.0.0.0 Safari/537.36";
    private static final String FIREFOX_DESKTOP_UA =
            "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0";

    @Test
    void multipleEventsForSameShortCodeAccumulateCorrectly() {
        aggregationService.process(
                new ClickEventDto(
                        "abc1234", "2026-06-29T10:05:00Z", CHROME_DESKTOP_UA, "https://google.com", "1.1.1.1"));
        aggregationService.process(
                new ClickEventDto(
                        "abc1234", "2026-06-29T10:45:00Z", CHROME_DESKTOP_UA, "https://google.com", "1.1.1.2"));
        aggregationService.process(
                new ClickEventDto(
                        "abc1234", "2026-06-29T11:10:00Z", FIREFOX_DESKTOP_UA, null, "1.1.1.3"));

        assertThat(urlClickStatsRepository.findByShortCode("abc1234").orElseThrow().getTotalClicks())
                .isEqualTo(3);

        var hourlyBuckets = hourlyClickBucketRepository.findByShortCodeOrderByBucketStartAsc("abc1234");
        assertThat(hourlyBuckets).hasSize(2); // 10:00 bucket (2 clicks) + 11:00 bucket (1 click)
        assertThat(hourlyBuckets.get(0).getClickCount()).isEqualTo(2);
        assertThat(hourlyBuckets.get(1).getClickCount()).isEqualTo(1);

        var referrers = referrerBreakdownRepository.findByShortCode("abc1234");
        assertThat(referrers).hasSize(2); // google.com (2) + direct (1)

        var devices = deviceBreakdownRepository.findByShortCode("abc1234");
        assertThat(devices).hasSize(2); // Chrome (2) + Firefox (1)
    }

    @Test
    void differentShortCodesDoNotShareCounters() {
        aggregationService.process(
                new ClickEventDto("aaa1111", "2026-06-29T10:05:00Z", CHROME_DESKTOP_UA, null, "1.1.1.1"));
        aggregationService.process(
                new ClickEventDto("bbb2222", "2026-06-29T10:05:00Z", CHROME_DESKTOP_UA, null, "1.1.1.1"));

        assertThat(urlClickStatsRepository.findByShortCode("aaa1111").orElseThrow().getTotalClicks())
                .isEqualTo(1);
        assertThat(urlClickStatsRepository.findByShortCode("bbb2222").orElseThrow().getTotalClicks())
                .isEqualTo(1);
    }
}
