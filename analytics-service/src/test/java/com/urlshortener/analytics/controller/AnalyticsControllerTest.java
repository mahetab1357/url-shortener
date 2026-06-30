package com.urlshortener.analytics.controller;

import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.urlshortener.analytics.dto.AnalyticsStatsResponse;
import com.urlshortener.analytics.service.AnalyticsQueryService;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.web.servlet.MockMvc;

@WebMvcTest(AnalyticsController.class)
class AnalyticsControllerTest {

    @Autowired private MockMvc mockMvc;

    @MockBean private AnalyticsQueryService analyticsQueryService;

    @Test
    void getStatsReturnsJsonBody() throws Exception {
        var response =
                new AnalyticsStatsResponse(
                        "abc1234", 5L, null, List.of(), List.of(), List.of(), List.of());
        when(analyticsQueryService.getStats("abc1234")).thenReturn(response);

        mockMvc
                .perform(get("/api/analytics/abc1234/stats"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.shortCode").value("abc1234"))
                .andExpect(jsonPath("$.totalClicks").value(5));
    }
}
