package com.urlshortener.analytics.service;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;

class UserAgentParserTest {

    private final UserAgentParser parser = new UserAgentParser();

    @Test
    void parsesChromeOnWindowsAsDesktop() {
        String ua =
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        + "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36";
        var result = parser.parse(ua);
        assertThat(result.deviceType()).isEqualTo("Desktop");
        assertThat(result.browser()).isEqualTo("Chrome");
    }

    @Test
    void parsesSafariOnIphoneAsMobile() {
        String ua =
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 "
                        + "(KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1";
        var result = parser.parse(ua);
        assertThat(result.deviceType()).isEqualTo("Mobile");
        assertThat(result.browser()).isEqualTo("Safari");
    }

    @Test
    void parsesFirefoxOnLinuxAsDesktop() {
        String ua = "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0";
        var result = parser.parse(ua);
        assertThat(result.deviceType()).isEqualTo("Desktop");
        assertThat(result.browser()).isEqualTo("Firefox");
    }

    @Test
    void parsesEdgeNotAsChromeDespiteSharedChromiumTokens() {
        String ua =
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        + "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0";
        var result = parser.parse(ua);
        assertThat(result.browser()).isEqualTo("Edge");
    }

    @Test
    void parsesIpadAsTablet() {
        String ua =
                "Mozilla/5.0 (iPad; CPU OS 17_5 like Mac OS X) AppleWebKit/605.1.15 "
                        + "(KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1";
        var result = parser.parse(ua);
        assertThat(result.deviceType()).isEqualTo("Tablet");
    }

    @Test
    void blankOrNullUserAgentReturnsUnknown() {
        assertThat(parser.parse(null).browser()).isEqualTo("Unknown");
        assertThat(parser.parse("").deviceType()).isEqualTo("Unknown");
    }

    @Test
    void unrecognizedBrowserReturnsOther() {
        var result = parser.parse("SomeWeirdBot/1.0");
        assertThat(result.browser()).isEqualTo("Other");
    }
}
