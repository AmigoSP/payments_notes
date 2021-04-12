import imaplib
import email
import base64

login = ''
password = ''
mail_connect = imaplib.IMAP4_SSL('imap.yandex.ru')
mail_connect.login(login, password)


def get_body(msg):
    if msg.is_multipart():
        return get_body(msg.get_payload(0))
    else:
        return msg.get_payload(decode=True)


def get_attachments(msg, write_file=False):
    result = []
    for part in msg.walk():
        check_attachment = part.get('Content-Disposition')
        if check_attachment and 'attachment' in check_attachment:
            file_name = part.get_filename()
            if file_name:
                file_name_parts = file_name.split('?')
                if len(file_name_parts) > 4:
                    file_name = base64.b64decode(file_name_parts[3]).decode(file_name_parts[1])
                else:
                    file_name = file_name_parts[0]
                    if write_file:
                        with open(file_name, 'wb') as wrt_file:
                            wrt_file.write(part.get_payload(decode=True))
                result.append(file_name)
    return result


def get_message(email_uid):
    new_result, data = mail_connect.uid('fetch', email_uid, '(RFC822)')
    raw_email = data[0][1]
    raw_message = email.message_from_bytes(raw_email)
    return raw_message


def main():
    all_emails = {}
    search_folders = ['"&BBI- &BB4EPwQ7BDAEQgRD-"', '"&BBIEQQQ1BBgEPQRBBEIEQARDBDwENQQ9BEIESw-"',
                      '"&BBgEPAQ,BD4EQARCBBwENQRFBDAEPQQ4BDoEMA-"']
    mail_connect.select(search_folders[0], readonly=True)  # Папка "В Оплату"

    result, data = mail_connect.uid('search', "ALL")
    latest_email_uid = data[0].split()[-6]
    raw_message = get_message(latest_email_uid)
    clear_message = get_body(raw_message).decode().split('</div>')[0].replace('<div>', '')
    attachments = get_attachments(raw_message)
    all_emails[latest_email_uid.decode()] = {'body': clear_message, 'attachments': attachments}
    print('ok')


if __name__ == '__main__':
    main()
