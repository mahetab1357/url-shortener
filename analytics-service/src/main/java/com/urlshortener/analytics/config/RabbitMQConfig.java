package com.urlshortener.analytics.config;

import org.springframework.amqp.core.Queue;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class RabbitMQConfig {

    @Bean
    public Queue clickEventsQueue(@Value("${app.rabbitmq.click-events-queue}") String queueName) {
        // durable=true matches core-service's queue_declare - both sides
        // must agree, or RabbitMQ rejects a redeclaration with mismatched
        // arguments.
        return new Queue(queueName, true);
    }
}
