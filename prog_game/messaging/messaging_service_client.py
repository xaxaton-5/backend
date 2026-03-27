import requests
from django.conf import settings
from django.contrib.auth.models import User


class SendingError(Exception):
    pass


class MessagingServiceClient:
    base_url = settings.MESSAGING_SERVICE_URL

    @classmethod
    def send_notification(cls, receiver_id: int) -> None:
        pass

    @classmethod
    def send_message(cls, sender: User, message_text: str) -> None:
        url = f'{cls.base_url}/message/send'
        params = {'account_id': sender.pk}
        data = {'text': message_text, 'sender_name': sender.username, 'sender_id': sender.pk}
        try:
            response = requests.post(url, params=params, json=data, timeout=5)
            response.raise_for_status()
        except requests.RequestException:
            raise SendingError('error attempting to send message to chat')
