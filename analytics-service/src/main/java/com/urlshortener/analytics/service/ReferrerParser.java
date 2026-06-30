package com.urlshortener.analytics.service;

import java.net.URI;
import org.springframework.stereotype.Component;

@Component
public class ReferrerParser {

    private static final String DIRECT = "direct";

    /** Extracts a bare domain (no "www.", no path/query) from a referrer
     * URL, or "direct" for no-referrer traffic or anything unparseable. */
    public String extractDomain(String referrer) {
        if (referrer == null || referrer.isBlank()) {
            return DIRECT;
        }
        try {
            String host = URI.create(referrer).getHost();
            if (host == null || host.isBlank()) {
                return DIRECT;
            }
            return host.startsWith("www.") ? host.substring(4) : host;
        } catch (IllegalArgumentException e) {
            return DIRECT;
        }
    }
}
