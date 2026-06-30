package com.urlshortener.analytics.service;

import org.springframework.stereotype.Component;

/**
 * Small heuristic UA parser - intentionally not a full library (uap-java
 * etc.) to avoid an extra Maven dependency for a feature where rough
 * accuracy is enough for this project. Order of the browser checks matters:
 * Chrome's UA string also contains "Safari/", and Edge/Opera UAs also
 * contain "Chrome/", so more specific tokens must be checked first.
 */
@Component
public class UserAgentParser {

    public record ParsedUserAgent(String deviceType, String browser) {}

    public ParsedUserAgent parse(String userAgent) {
        if (userAgent == null || userAgent.isBlank()) {
            return new ParsedUserAgent("Unknown", "Unknown");
        }
        return new ParsedUserAgent(detectDeviceType(userAgent), detectBrowser(userAgent));
    }

    private String detectDeviceType(String ua) {
        if (ua.contains("iPad") || ua.contains("Tablet")) {
            return "Tablet";
        }
        if (ua.contains("Mobi") || ua.contains("iPhone") || ua.contains("Android")) {
            return "Mobile";
        }
        return "Desktop";
    }

    private String detectBrowser(String ua) {
        if (ua.contains("Edg/")) {
            return "Edge";
        }
        if (ua.contains("OPR/") || ua.contains("Opera")) {
            return "Opera";
        }
        if (ua.contains("Chrome/") || ua.contains("CriOS/")) {
            return "Chrome";
        }
        if (ua.contains("Firefox/") || ua.contains("FxiOS/")) {
            return "Firefox";
        }
        if (ua.contains("Safari/")) {
            return "Safari";
        }
        return "Other";
    }
}
