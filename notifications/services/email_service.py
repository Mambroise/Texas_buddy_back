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

from ads.utils import generate_invoice_pdf
from .company_service import CompanyService

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


def send_invoice_email(invoice):
    try:
        company_info = CompanyService.get_company_info()

        subject = _('Your invoice for advertisement: {title}').format(title=invoice.advertisement.title)
        from_email = company_info.email
        to_email = invoice.advertisement.contract.partner.contact_email
        bcc_email = [company_info.email]

        email_body = {
            'company_info': company_info,
            'invoice': invoice,
        }

        html_content = render_to_string('email/invoice_email.html', email_body)
        text_content = _('Votre client mail ne supporte pas le HTML.')

        email = EmailMultiAlternatives(
            subject,
            text_content,
            from_email,
            [to_email],
            bcc=bcc_email
        )
        email.attach_alternative(html_content, "text/html")

        # Génération du PDF via la fonction séparée
        pdf_buffer = generate_invoice_pdf(invoice, company_info)
        filename = f"invoice_{invoice.id}.pdf"
        email.attach(filename, pdf_buffer.read(), "application/pdf")

        # Attacher les images éventuelles
        email = attach_pic_to_email(email)

        email.send()
        return True

    except Exception as e:
        print(f"Erreur lors de l'envoi de la facture par email : {e}")
        return False


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
