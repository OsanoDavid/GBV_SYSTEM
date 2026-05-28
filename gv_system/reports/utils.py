from django.core.mail import get_connection
from django.conf import settings

def check_email_connection():
    try:
        connection = get_connection(fail_silently=False)
        connection.open()
        connection.close()
        return True
    except:
        return False