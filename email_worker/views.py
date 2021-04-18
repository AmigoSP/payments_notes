from django.shortcuts import render

# Create your views here.
from .utils import *

login = ''
password = ''


def index(request):
    content = EmailHandler(login, password).get_content(start_uid=195)
    return render(request, 'email_worker/index.html', {'all_emails': content})
