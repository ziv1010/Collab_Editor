import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Document

class DocumentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.document_id = self.scope['url_route']['kwargs']['document_id']
        self.room_group_name = f'document_{self.document_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Send initial content
        content = await self.get_document_content()
        await self.send(text_data=json.dumps({
            'type': 'initial_content',
            'content': content,
        }))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message')

        # Update the document content
        await self.save_document_content(message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'document_message',
                'message': message,
                'sender_channel_name': self.channel_name,
            }
        )

    # Receive message from room group
    async def document_message(self, event):
        message = event['message']
        sender_channel_name = event['sender_channel_name']

        # Prevent sending the message back to the sender
        if self.channel_name != sender_channel_name:
            # Send message to WebSocket
            await self.send(text_data=json.dumps({
                'type': 'update_content',
                'message': message,
            }))

    @database_sync_to_async
    def get_document_content(self):
        document = Document.objects.get(pk=self.document_id)
        return document.content

    @database_sync_to_async
    def save_document_content(self, content):
        Document.objects.filter(pk=self.document_id).update(content=content)