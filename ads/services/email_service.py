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
from notifications.services.company_service import CompanyService

logger = logging.getLogger("texasbuddy")  


def send_invoice_email(invoice):
    try:
        company_info = CompanyService.get_company_info()

        subject = _('Your invoice for advertisement: {title}').format(title=invoice.advertisement.io_reference_number)
        from_email = company_info.email
        to_email = invoice.advertisement.contract.partner.contact_email
        bcc_email = [company_info.email]

        email_body = {
            'company_info': company_info,
            'invoice': invoice,
        }

        html_content = render_to_string('admin/email/invoice_email.html', email_body)
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
