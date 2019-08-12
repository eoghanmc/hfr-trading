from django.contrib import admin
from trading.models import Fund, Portfolio, Position, TradeItem, BBGData

# Register models
admin.site.register(Fund)
admin.site.register(Portfolio)
admin.site.register(Position)
admin.site.register(TradeItem)
admin.site.register(BBGData)
