# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :notifications/admin.py
# Author : Morice
# ---------------------------------------------------------------------------   

 
from django.contrib import admin

from .models import CompanyInfo

@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ("name", 'ein', 'siren', 'legal_structure','vat_number', "email", "address", 'tax_math', 'tax_info', 'phone', "is_in_texas")


