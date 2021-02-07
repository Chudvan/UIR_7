from django.contrib import admin

from .models import Pump, PumpState, Petrol, \
    Terminal, ErrorType, Error, \
    Order, CustomerDetail, PayType, OrderPetrol, \
    OtherType, OrderOther, Scan


class PumpAdmin(admin.ModelAdmin):
    list_display = ('id', 'number',)
    list_display_links = ('id', 'number',)
    search_fields = ('id', 'number',)


class PumpStateAdmin(admin.ModelAdmin):
    list_display = ('datetime', 'number', 'status')
    list_display_links = ('datetime', 'number', 'status')
    search_fields = ('datetime', 'number', 'status')


class PetrolAdmin(admin.ModelAdmin):
    list_display = ('datetime', 'petrolType', 'price')
    list_display_links = ('datetime', 'petrolType', 'price')
    search_fields = ('datetime', 'petrolType', 'price')


class TerminalAdmin(admin.ModelAdmin):
    list_display = ('terminalNumber',)
    list_display_links = ('terminalNumber',)
    search_fields = ('terminalNumber',)


class ErrorTypeAdmin(admin.ModelAdmin):
    list_display = ('errortype',)
    list_display_links = ('errortype',)
    search_fields = ('errortype',)


class ErrorAdmin(admin.ModelAdmin):
    list_display = ('dateTime', 'terminalNumber', 'errorType')
    list_display_links = ('dateTime', 'terminalNumber', 'errorType')
    search_fields = ('dateTime', 'terminalNumber', 'errorType')


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'orderId', 'terminalNumber', 'dateTime', 'orderType', 'barCode')
    list_display_links = ('id', 'orderId', 'terminalNumber', 'dateTime', 'orderType', 'barCode')
    search_fields = ('id', 'orderId', 'terminalNumber', 'dateTime', 'orderType', 'barCode')


class CustomerDetailAdmin(admin.ModelAdmin):
    list_display = ('telephone', 'email')
    list_display_links = ('telephone', 'email')
    search_fields = ('telephone', 'email')


class PayTypeAdmin(admin.ModelAdmin):
    list_display = ('payType',)
    list_display_links = ('payType',)
    search_fields = ('payType',)


class OrderPetrolAdmin(admin.ModelAdmin):
    list_display = ('orderId', 'pump', 'petrol', 'volume', 'amount', 'customerDetails', 'payType', 'change')
    list_display_links = ('orderId', 'pump', 'petrol', 'volume', 'amount', 'customerDetails', 'payType', 'change')
    search_fields = ('orderId', 'pump', 'petrol', 'volume', 'amount', 'customerDetails', 'payType', 'change')


class OtherTypeAdmin(admin.ModelAdmin):
    list_display = ('otherType',)
    list_display_links = ('otherType',)
    search_fields = ('otherType',)


class OrderOtherAdmin(admin.ModelAdmin):
    list_display = ('orderId', 'fromId', 'number', 'amount', 'otherType', 'cash', 'change')
    list_display_links = ('orderId', 'fromId', 'number', 'amount', 'otherType', 'cash', 'change')
    search_fields = ('payType',)


class ScanAdmin(admin.ModelAdmin):
    list_display = ('dateTime', 'terminalNumber', 'barCode',)
    list_display_links = ('dateTime', 'terminalNumber', 'barCode',)
    search_fields = ('dateTime', 'terminalNumber', 'barCode',)


admin.site.register(Pump, PumpAdmin)
admin.site.register(PumpState, PumpStateAdmin)
admin.site.register(Petrol, PetrolAdmin)
admin.site.register(Terminal, TerminalAdmin)
admin.site.register(ErrorType, ErrorTypeAdmin)
admin.site.register(Error, ErrorAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(CustomerDetail, CustomerDetailAdmin)
admin.site.register(PayType, PayTypeAdmin)
admin.site.register(OrderPetrol, OrderPetrolAdmin)
admin.site.register(OtherType, OtherTypeAdmin)
admin.site.register(OrderOther, OrderOtherAdmin)
admin.site.register(Scan, ScanAdmin)
