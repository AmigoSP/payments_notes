import imaplib
import email
import os.path
from email.header import decode_header
import datetime
from typing import Any
from django.conf import settings

login = ''
password = ''


class EmailHandler:

    def __init__(self, login: str, password: str, imap_addr: str = 'imap.yandex.ru'):
        self.login = login
        self.password = password
        self.imap_addr = imap_addr
        self._search_folders = ['"&BBI- &BB4EPwQ7BDAEQgRD-"', '"&BBIEQQQ1BBgEPQRBBEIEQARDBDwENQQ9BEIESw-"',
                                '"&BBgEPAQ,BD4EQARCBBwENQRFBDAEPQQ4BDoEMA-"']
        self.date = datetime.date(2021, 1, 1).strftime("%d-%b-%Y")
        self.mail_connect = imaplib.IMAP4_SSL('imap.yandex.ru')
        self.mail_connect.login(self.login, self.password)
        self.mail_connect.select(self._search_folders[0], readonly=True)  # Папка "В Оплату"

    def get_body(self, msg):
        if msg.is_multipart():
            return self.get_body(msg.get_payload(0))
        else:
            return msg.get_payload(decode=True)

    @staticmethod
    def get_attachments(msg, email_uid, write_file=False):
        attachments_names = []
        attachments_path = []
        for part in msg.walk():
            check_attachment = part.get('Content-Disposition')
            if check_attachment and 'attachment' in check_attachment:
                file_name = part.get_filename()
                if file_name:
                    raw_name, format_decoder = decode_header(file_name)[0]
                    if format_decoder:
                        raw_name = raw_name.decode(format_decoder)
                    attachments_names.append({'full_name': f'{email_uid}_{raw_name}',
                                              'clear_name': raw_name})
                    if write_file:
                        file_path = os.path.join(settings.LOCALE_UPLOAD_FILES, f'{email_uid}_{raw_name}')
                        with open(file_path, 'wb') as wrt_file:
                            wrt_file.write(part.get_payload(decode=True))
                        attachments_path.append(file_path)

        return attachments_names, attachments_path

    def get_message(self, email_uid):
        new_result, data = self.mail_connect.uid('fetch', email_uid, '(RFC822)')
        raw_email = data[0][1]
        raw_message = email.message_from_bytes(raw_email)
        return raw_message

    @staticmethod
    def get_title(msg):
        raw_title, format_decoder = decode_header(msg.get('Subject'))[0]
        if format_decoder:
            return raw_title.decode(format_decoder)
        return raw_title

    @staticmethod
    def _check_uid(email_uid: bytes, all_uid: list):
        try:
            all_uid = all_uid[all_uid.index(email_uid) + 1:]
        except ValueError:
            return None
        else:
            return all_uid

    def get_content(self, start_uid: Any = None, write_attachments: bool = True):
        all_emails = []
        result, data = self.mail_connect.uid('search', f'(SINCE {self.date})')
        all_email_uid = data[0].split()
        if start_uid:
            start_uid = str(start_uid).encode()
            all_email_uid = self._check_uid(start_uid, all_email_uid)
        if all_email_uid:
            for email_uid in all_email_uid:
                raw_message = self.get_message(email_uid)
                title = self.get_title(raw_message)
                clear_message = self.get_body(raw_message).decode().split('</div>')[0].replace('<div>', '')
                attachments, attachments_path = self.get_attachments(raw_message, write_file=write_attachments,
                                                                     email_uid=email_uid.decode())
                all_emails.append(
                    {'body': clear_message, 'attachments': attachments, 'title': title, 'date': self.date,
                     'email_uid': int(email_uid), 'attachments_path': attachments_path})
        return all_emails


if __name__ == '__main__':
    content = EmailHandler(login=login, password=password)
    content.get_content(start_uid=200)
