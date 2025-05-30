# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :texasbuddy/notifications/services/email_service.py
# Author : Morice
# ---------------------------------------------------------------------------

import os
from django.utils.translation import gettext as _
from django.conf import settings
from email.mime.image import MIMEImage
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

def send_credentials_email(user):
    try:
        object_content = _("Texas Buddy: Your credentials for the mobile app")
        
        context = {
            'user' : user
        }

        # Render the email template with context data
        subject = object_content
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = user.email
        text_content = 'your email client does not support HTML content'

        html_credential_content = render_to_string('email/credentials_email.html',context)

        # Create the email message
        email = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        email.attach_alternative(html_credential_content, 'text/html')

        # attach picture to email
        email = attach_pic_to_email(email)

        # Send the email
        email.send()

        
    except Exception as e:
        print('send_credentials_email email error:', {e})


def send_2fa_code_email(user, code):
    try:
        object_content = _("Texas Buddy: Your two-step verification code")
        
        context = {
            'user' : user,
            'code' : code
        }

        # Render the email template with context data
        subject = object_content
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = user.email
        text_content = 'your email client does not support HTML content'

        html_twofa_content = render_to_string('email/twofa_email.html',context)

        # Create the email message
        email = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        email.attach_alternative(html_twofa_content, 'text/html')

        # attach picture to email
        email = attach_pic_to_email(email)

        # Send the email
        email.send()

        
    except Exception as e:
        print('send_2fa_code_email email error:', {e})






def attach_pic_to_email(email):
    # Attachez les images nécessaires avec Content-ID
    image_paths = {
            'austin': 'static/images/austin_colorado.jpg',
        }

    for cid, img_path in image_paths.items():
        absolute_path = os.path.join(settings.BASE_DIR, img_path)
        with open(absolute_path, 'rb') as img:
            mime_img = MIMEImage(img.read())
            mime_img.add_header('Content-ID', f'<{cid}>')
            mime_img.add_header('Content-Disposition', 'inline')
            email.attach(mime_img)
    return email