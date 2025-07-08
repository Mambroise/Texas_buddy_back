# --------------------------------------------------------------------------- 
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   : texasbuddy/notifications/services/email_service.py
# Author : Morice
# ---------------------------------------------------------------------------

import os
import logging
from django.utils.translation import gettext as _
from django.conf import settings
from email.mime.image import MIMEImage
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives


logger = logging.getLogger("texasbuddy")  

def send_credentials_email(user):
    try:
        object_content = _("Texas Buddy: Your credentials for the mobile app")
        context = {'user': user}

        subject = object_content
        from_email = settings.EMAIL_HOST_USER
        to_email = user.email
        text_content = 'Your email client does not support HTML content'

        html_credential_content = render_to_string('email/credentials_email.html', context)

        email = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        email.attach_alternative(html_credential_content, 'text/html')
        email = attach_pic_to_email(email)
        email.send()

        logger.info(f"Credentials email sent successfully to user {user.email} (ID: {user.id})")

    except Exception as e:
        logger.error(f"Error sending credentials email to user {user.email}: {str(e)}", exc_info=True)


def send_2fa_code_email(user, code):
    try:
        object_content = _("Texas Buddy: Your two-step verification code")
        context = {
            'user': user,
            'code': code
        }

        subject = object_content
        from_email = settings.EMAIL_HOST_USER
        to_email = user.email
        text_content = 'Your email client does not support HTML content'

        html_twofa_content = render_to_string('email/twofa_email.html', context)

        email = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        email.attach_alternative(html_twofa_content, 'text/html')
        email = attach_pic_to_email(email)
        email.send()

        logger.info(f"2FA code email sent to user {user.email} (ID: {user.id}) with code {code}")

    except Exception as e:
        logger.error(f"Error sending 2FA code email to user {user.email}: {str(e)}", exc_info=True)


def attach_pic_to_email(email):
    image_paths = {
        'austin': 'static/images/austin_colorado.jpg',
    }

    for cid, img_path in image_paths.items():
        try:
            absolute_path = os.path.join(settings.BASE_DIR, img_path)
            with open(absolute_path, 'rb') as img:
                mime_img = MIMEImage(img.read())
                mime_img.add_header('Content-ID', f'<{cid}>')
                mime_img.add_header('Content-Disposition', 'inline')
                email.attach(mime_img)
                logger.debug(f"Image '{img_path}' attached to email with CID <{cid}>.")
        except FileNotFoundError:
            logger.warning(f"Image file not found: {img_path}")
        except Exception as e:
            logger.error(f"Failed to attach image {img_path}: {str(e)}", exc_info=True)

    return email
