from django.contrib import admin
from trading.models import Fund, Portfolio, Position, TradeItem, BBGData
from trading.models import Calendar, CalendarDate

# Register models
admin.site.register(Fund)
admin.site.register(Portfolio)
admin.site.register(Position)
admin.site.register(TradeItem)
admin.site.register(BBGData)
admin.site.register(Calendar)
admin.site.register(CalendarDate)
