from django.conf import settings
from django.db import models

class BlogPost(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    text = models.TextField('Текст')
    date_added = models.DateTimeField('Дата публикации', auto_now_add=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Автор')

    def __str__(self):
        return self.title
