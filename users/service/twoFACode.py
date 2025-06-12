# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :texasbuddy/users/services/twoFACode.py
# Author : Morice
# ---------------------------------------------------------------------------

import logging
import random
from notifications.services.email_service import send_2fa_code_email
from users.models.twofa import TwoFACode

# ----- Logger Setup-------------------------------------------
logger = logging.getLogger('texasbuddy')

# ----- 2FA code generation and email expedition

def generate_2fa_code(user):
    # Supprimer les anciens codes non utilisés
    TwoFACode.objects.filter(user=user, is_used=False).delete()

    code = f"{random.randint(100000, 999999)}"
    twofa = TwoFACode.objects.create(user=user, code=code)
    logger.info('[ 2FA_GENERATION_METHOD]  2FA successfully generated for user %s', user.email)

    send_2fa_code_email(user, code)
    return twofa
