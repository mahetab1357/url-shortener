package com.urlshortener.analytics.service;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;

class ReferrerParserTest {

    private final ReferrerParser parser = new ReferrerParser();

    @Test
    void extractsBareDomain() {
        assertThat(parser.extractDomain("https://www.google.com/search?q=foo")).isEqualTo("google.com");
    }

    @Test
    void stripsWwwPrefix() {
        assertThat(parser.extractDomain("https://www.example.com/")).isEqualTo("example.com");
    }

    @Test
    void keepsNonWwwSubdomain() {
        assertThat(parser.extractDomain("https://news.ycombinator.com/item?id=1")).isEqualTo("news.ycombinator.com");
    }

    @Test
    void nullReferrerIsDirect() {
        assertThat(parser.extractDomain(null)).isEqualTo("direct");
    }

    @Test
    void blankReferrerIsDirect() {
        assertThat(parser.extractDomain("  ")).isEqualTo("direct");
    }

    @Test
    void malformedReferrerIsDirect() {
        assertThat(parser.extractDomain("not a url::: at all")).isEqualTo("direct");
    }
}
