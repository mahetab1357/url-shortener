package com.urlshortener.analytics.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

/** Mirrors the JSON shape published by core-service in
 * app/services/click_event.py - keep the two in sync if either changes. */
public record ClickEventDto(
        @JsonProperty("short_code") String shortCode,
        @JsonProperty("timestamp") String timestamp,
        @JsonProperty("user_agent") String userAgent,
        @JsonProperty("referrer") String referrer,
        @JsonProperty("ip") String ip) {}
