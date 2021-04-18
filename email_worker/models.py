from django.db import models


# Create your models here.


class EmailMessage(models.Model):
    uid_message = models.IntegerField(verbose_name='message_uid')
    title = models.TextField(verbose_name='заголовок')
    body = models.TextField(verbose_name='тело письма')
    date = models.DateTimeField(verbose_name='получено')
    attachments = models.TextField(verbose_name='вложения')
    is_processed = models.BooleanField(default=False, verbose_name='обработано')

    class Meta:
        verbose_name = 'Сообщение почты'
        verbose_name_plural = 'Сообщения почты'


class Attachments(models.Model):
    attachment_path = models.FilePathField()
    attachment_name = models.CharField(max_length=255, verbose_name='имя файла')
    attachment_clear_name = models.CharField(max_length=255, verbose_name='имя файла без UID')
    email_message = models.ForeignKey(EmailMessage, on_delete=models.CASCADE, verbose_name='вложение сообщения',
                                      related_name='attachments_message')
