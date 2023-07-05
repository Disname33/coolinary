from datetime import datetime

from channels.middleware import BaseMiddleware


class SendModifyMiddleware(BaseMiddleware):
    def __init__(self, inner):
        super().__init__(inner)

    async def __call__(self, scope, receive, send):
        # Получите сообщение
        message = await receive()

        # Обработайте сообщение перед отправкой
        sender = str(scope["user"])
        timestamp = datetime.now().timestamp()

        # Добавьте информацию об отправителе и времени отправки к сообщению
        message["sender"] = sender
        message["timestamp"] = timestamp

        # Отправьте сообщение
        await self.inner(scope, receive, send)
