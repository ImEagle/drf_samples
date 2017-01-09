from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase

from chat.models import Message


class MessageAPITestCase(APITestCase):
    url_login = reverse('accounts:login')

    def setUp(self):
        self.user_1 = User.objects.create_user('user_1', password='user_1_p')
        self.user_2 = User.objects.create_user('user_2', password='user_2_p')

    def _login(self, username, password):
        user_data = {
            'username': username,
            'password': password,
        }

        response = self.client.post(self.url_login, user_data)
        self.assertEqual(200, response.status_code)
        self.client.cookies = response.cookies


class MessageUnreadCountApiViewTestCase(MessageAPITestCase):
    url_message_create = reverse('chat:messages')

    def test_get_unauthorized(self):
        response = self.client.get(self.url_message_create)

        self.assertEqual(403, response.status_code)

    def test_unread_count_sender(self):
        self._login('user_1', 'user_1_p')

        Message.objects.send(self.user_1, self.user_2, "Foo Bar")

        response = self.client.get(self.url_message_create)

        message_data = response.json()
        self.assertIn('unread', message_data)
        self.assertEqual(0, message_data['unread'])

    def test_unread_count_receiver(self):
        self._login('user_2', 'user_2_p')
        Message.objects.send(self.user_1, self.user_2, "Foo Bar")

        response = self.client.get(self.url_message_create)

        message_data = response.json()
        self.assertIn('unread', message_data)
        self.assertEqual(1, message_data['unread'])


class MessageCreateApiViewTestCase(MessageAPITestCase):
    url_list_create = reverse('chat:messages')

    def test_send_message(self):
        self._login('user_1', 'user_1_p')

        message_data = {
            'receiver': self.user_2.id,
            'content': 'Foo Bar content msg',
        }

        response = self.client.post(self.url_list_create, message_data)
        self.assertEqual(201, response.status_code)

    def test_send_message_unread_count_sender(self):
        self.test_send_message()

        self._login('user_1', 'user_1_p')
        response = self.client.get(self.url_list_create)

        message_data = response.json()
        self.assertIn('unread', message_data)
        self.assertEqual(0, message_data['unread'])

    def test_send_message_unread_count_receiver(self):
        self.test_send_message()

        self._login('user_2', 'user_2_p')
        response = self.client.get(self.url_list_create)

        message_data = response.json()
        self.assertIn('unread', message_data)
        self.assertEqual(1, message_data['unread'])

    def test_invalid_receiver(self):
        self._login('user_1', 'user_1_p')

        message_data = {
            'receiver_id': 7,
            'content': 'Foo Bar content msg',
        }

        response = self.client.post(self.url_list_create, message_data)
        self.assertEqual(400, response.status_code)


class MessageListApiViewTestCase(MessageAPITestCase):
    url_message_create = reverse('chat:messages')

    def _create_messages(self, sender, receiver, count=1):
        for i in xrange(0, count):
            Message.objects.send(sender, receiver, 'msg {}'.format(i))

    def test_get_conversation_main_sender_no_mark_as_read(self):
        self._create_messages(self.user_1, self.user_2, 3)

        self._login('user_1', 'user_1_p')

        url_list = reverse('chat:list', args=(self.user_1.id,))
        response_first = self.client.get(url_list)
        self.assertEqual(200, response_first.status_code)

        messages_first = response_first.json()

        self.assertEqual(3, len(messages_first))

        for msg in messages_first:
            self.assertEqual(self.user_1.id, msg['sender_id'])
            self.assertEqual(self.user_2.id, msg['receiver_id'])
            self.assertEqual(True, msg['is_new'])

        response_snd = self.client.get(url_list)
        self.assertEqual(200, response_snd.status_code)

        messages_snd = response_snd.json()

        self.assertEqual(3, len(messages_snd))

        for msg in messages_snd:
            self.assertEqual(self.user_1.id, msg['sender_id'])
            self.assertEqual(self.user_2.id, msg['receiver_id'])
            self.assertEqual(True, msg['is_new'])

    def test_get_conversation_main_receiver_mark_as_read(self):
        self._create_messages(self.user_1, self.user_2, 3)

        self._login('user_2', 'user_2_p')

        url_list = reverse('chat:list', args=(self.user_1.id,))
        response_first = self.client.get(url_list)
        self.assertEqual(200, response_first.status_code)

        messages_first = response_first.json()

        self.assertEqual(3, len(messages_first))

        for msg in messages_first:
            self.assertEqual(self.user_1.id, msg['sender_id'])
            self.assertEqual(self.user_2.id, msg['receiver_id'])
            self.assertEqual(True, msg['is_new'])

        response_snd = self.client.get(url_list)
        self.assertEqual(200, response_snd.status_code)

        messages_snd = response_snd.json()

        self.assertEqual(3, len(messages_snd))

        for msg in messages_snd:
            self.assertEqual(self.user_1.id, msg['sender_id'])
            self.assertEqual(self.user_2.id, msg['receiver_id'])
            self.assertEqual(False, msg['is_new'])

    def test_get_unread_count_sender(self):
        self._create_messages(self.user_1, self.user_2, 3)
        self._login('user_1', 'user_1_p')

        response = self.client.get(self.url_message_create)
        response_json = response.json()
        self.assertEqual(0, response_json['unread'])

    def test_get_unread_count_receiver(self):
        self._create_messages(self.user_1, self.user_2, 3)
        self._login('user_2', 'user_2_p')

        response = self.client.get(self.url_message_create)
        response_json = response.json()
        self.assertEqual(3, response_json['unread'])

        url_list = reverse('chat:list', args=(self.user_1.id,))
        self.client.get(url_list)

        response_snd = self.client.get(self.url_message_create)
        response_snd_json = response_snd.json()
        self.assertEqual(0, response_snd_json['unread'])
