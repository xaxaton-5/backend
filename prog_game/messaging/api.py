import http

from rest_framework.views import APIView, Response

from messaging.models import ChatMessage
from messaging.messaging_service_client import MessagingServiceClient, SendingError
from messaging.serializers import MessageSerializer
from users.decorators import with_authorization


class MessageList(APIView):
    @with_authorization
    def get(self, request):
        messages = ChatMessage.objects.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)


class MessageSend(APIView):
    @with_authorization
    def post(self, request):
        text = request.data.get('text')
        sender = request.user

        try:
            MessagingServiceClient.send_message(sender, text)
            ChatMessage.objects.create(text=text, from_user=sender)
        except SendingError:
            return Response({'status': 'FAIL'}, status=http.HTTPStatus.BAD_REQUEST)
        return Response({'status': 'OK'}, status=http.HTTPStatus.ACCEPTED)


message_list = MessageList.as_view()
message_send = MessageSend.as_view()
