# ---------------------------------------------------------------------------
#                    T e x a s  B u d d y   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   : notifications/services/company_service.py
# Author : Morice
# ---------------------------------------------------------------------------


from ..models import CompanyInfo

class CompanyService:
    @staticmethod
    def get_company_info():
       return CompanyInfo.objects.all().first()
