# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :activities/validators.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.core.exceptions import ValidationError

def validate_image(image):
    filesize = image.size
    megabyte_limit = 5
    if filesize > megabyte_limit * 1024 * 1024:
        raise ValidationError(f"Image file too large ( > {megabyte_limit}MB )")
    
    valid_mime_types = ['image/jpeg', 'image/png', 'image/webp']
    if hasattr(image, 'content_type'):
        if image.content_type not in valid_mime_types:
            raise ValidationError("Unsupported file type. Only JPG, PNG and WEBP allowed.")
