from django.contrib import admin
from .models import Charger, Transaction, StatusLog
# Register your models here.
admin.site.register(Charger)
admin.site.register(Transaction)
admin.site.register(StatusLog)