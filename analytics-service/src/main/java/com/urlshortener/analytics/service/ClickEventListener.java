package com.urlshortener.analytics.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.urlshortener.analytics.dto.ClickEventDto;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;

@Component
public class ClickEventListener {

    private static final Logger log = LoggerFactory.getLogger(ClickEventListener.class);

    private final AggregationService aggregationService;
    private final ObjectMapper objectMapper;

    public ClickEventListener(AggregationService aggregationService, ObjectMapper objectMapper) {
        this.aggregationService = aggregationService;
        this.objectMapper = objectMapper;
    }

    @RabbitListener(queues = "${app.rabbitmq.click-events-queue}")
    public void onClickEvent(String rawMessage) {
        try {
            ClickEventDto event = objectMapper.readValue(rawMessage, ClickEventDto.class);
            aggregationService.process(event);
        } catch (Exception e) {
            // Swallow rather than rethrow: an exception here would cause
            // Spring AMQP to requeue/redeliver, and a permanently malformed
            // message would loop forever. A production system would route
            // failures like this to a dead-letter queue instead of
            // dropping them - listed as a future improvement.
            log.error("Failed to process click event, dropping message: {}", rawMessage, e);
        }
    }
}
