from app.config import settings
from app.mq.rabbitmq_client import RabbitMQPublisher, build_publisher

_publisher: RabbitMQPublisher = build_publisher(settings.rabbitmq_url)


def get_publisher() -> RabbitMQPublisher:
    return _publisher
