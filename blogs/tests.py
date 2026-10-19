from datetime import timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .models import BlogPost

class BlogTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.alice = User.objects.create_user('alice', password='Strong-pass-123')
        self.bob = User.objects.create_user('bob', password='Strong-pass-123')
        self.old = BlogPost.objects.create(owner=self.alice, title='Старая запись', text='Первый текст')
        self.new = BlogPost.objects.create(owner=self.bob, title='Новая запись', text='Второй текст')
        BlogPost.objects.filter(pk=self.old.pk).update(date_added=timezone.now() - timedelta(days=2))

    def test_public_read_and_order(self):
        response = self.client.get(reverse('blogs:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Старая запись')
        self.assertContains(response, 'Новая запись')
        self.assertEqual(list(response.context['posts']), [self.new, self.old])
        self.assertNotContains(response, 'Написать публикацию')

    def test_empty_state(self):
        BlogPost.objects.all().delete()
        self.assertContains(self.client.get(reverse('blogs:index')), 'Публикаций пока нет')

    def test_login_required_for_create(self):
        self.assertEqual(self.client.get(reverse('blogs:post_new')).status_code, 302)
        self.assertEqual(self.client.post(reverse('blogs:post_new'),
                                       {'title': 'Аноним', 'text': 'Текст'}).status_code, 302)

    def test_author_assigned_automatically(self):
        self.client.force_login(self.alice)
        self.client.post(reverse('blogs:post_new'),
            {'title': 'Моя', 'text': 'Текст', 'owner': self.bob.pk})
        self.assertEqual(BlogPost.objects.get(title='Моя').owner, self.alice)

    def test_owner_can_edit_without_owner_change(self):
        self.client.force_login(self.alice)
        response = self.client.post(reverse('blogs:post_edit', args=[self.old.pk]),
            {'title': 'Исправлено', 'text': 'Другой текст', 'owner': self.bob.pk})
        self.assertRedirects(response, reverse('blogs:index'))
        self.old.refresh_from_db()
        self.assertEqual(self.old.title, 'Исправлено')
        self.assertEqual(self.old.owner, self.alice)

    def test_other_user_cannot_edit_and_link_hidden(self):
        self.client.force_login(self.alice)
        url = reverse('blogs:post_edit', args=[self.new.pk])
        self.assertEqual(self.client.get(url).status_code, 404)
        self.assertEqual(self.client.post(url, {'title': 'Сломано', 'text': 'x'}).status_code, 404)
        response = self.client.get(reverse('blogs:index'))
        self.assertNotContains(response, 'href="' + url + '"')

    def test_missing_post_404(self):
        self.client.force_login(self.alice)
        self.assertEqual(self.client.get(reverse('blogs:post_edit', args=[999999])).status_code, 404)

    def test_registration(self):
        response = self.client.post(reverse('users:register'), {
            'username': 'new_student', 'password1': 'Strong-pass-123',
            'password2': 'Strong-pass-123'})
        self.assertRedirects(response, reverse('blogs:index'))
        self.assertTrue(get_user_model().objects.filter(username='new_student').exists())
        self.assertContains(self.client.get(reverse('blogs:index')), 'new_student')

    def test_logout_post_only(self):
        self.client.force_login(self.alice)
        url = reverse('users:logout')
        self.assertEqual(self.client.get(url).status_code, 405)
        self.assertTrue(self.client.session.get('_auth_user_id'))
        self.client.post(url)
        self.assertFalse(self.client.session.get('_auth_user_id'))
