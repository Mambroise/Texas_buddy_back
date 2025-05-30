import random
from notifications.services.email_service import send_2fa_code_email
from users.models.twofa import TwoFACode

def generate_2fa_code(user):
    # Supprimer les anciens codes non utilisés
    TwoFACode.objects.filter(user=user, is_used=False).delete()

    code = f"{random.randint(100000, 999999)}"
    twofa = TwoFACode.objects.create(user=user, code=code)

    send_2fa_code_email(user, code)
    return twofa
