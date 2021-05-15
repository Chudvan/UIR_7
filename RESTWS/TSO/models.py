from django.db import models


class Pump(models.Model):
    number = models.IntegerField(verbose_name='Номер ТРК', unique=True)

    def __str__(self):
        return str(self.number)

    def __int__(self):
        return self.number


class PumpState(models.Model):
    datetime = models.DateTimeField(db_index=True)
    number = models.ForeignKey(Pump, verbose_name='Номер ТРК', on_delete=models.CASCADE)
    PUMP_STATUS = ['FREE', 'BUSY', 'UNAVAILABLE']
    PUMP_STATUS = ((status, status) for status in PUMP_STATUS)
    status = models.CharField(verbose_name='Статус ТРК', choices=PUMP_STATUS, max_length=30)

    def __str__(self):
        return str(self.datetime) + ' | ' + str(self.number) + ' | ' + self.status


class Petrol(models.Model):
    datetime = models.DateTimeField(db_index=True)
    PETROL_TYPE = ['OR92', 'OR95', 'OR98', 'DIESEL']
    PETROL_TYPE = ((type, type) for type in PETROL_TYPE)
    petrolType = models.CharField(verbose_name='Вид НП', choices=PETROL_TYPE, max_length=30)
    price = models.FloatField(verbose_name='Цена')

    def __str__(self):
        return str(self.datetime) + ' | ' + self.petrolType + ' | ' + str(self.price)


class Terminal(models.Model):
    terminalNumber = models.IntegerField(verbose_name='Номер Терминала', unique=True)

    def __str__(self):
        return str(self.terminalNumber)


class ErrorType(models.Model):
    ERROR_TYPE = ['OK', 'SCANER', 'PAPER', 'CURRENCYDETECTOR', 'INK', 'POS', 'OTHER']
    ERROR_TYPE = ((type, type) for type in ERROR_TYPE)
    errortype = models.CharField(verbose_name='Ограничения ТСО', choices=ERROR_TYPE, unique=True, max_length=50)

    def __str__(self):
        return self.errortype


class Error(models.Model):
    dateTime = models.DateTimeField(db_index=True)
    terminalNumber = models.ForeignKey(Terminal, verbose_name='Номер Терминала', on_delete=models.PROTECT)
    errorType = models.ForeignKey(ErrorType, verbose_name='Ограничения ТСО', on_delete=models.PROTECT)


class DateTimeTerminal(models.Model):
    dateTime = models.DateTimeField(db_index=True)
    terminalNumber = models.ForeignKey(Terminal, verbose_name='Номер Терминала', on_delete=models.PROTECT)


class Order(models.Model):
    orderId = models.IntegerField()
    terminalNumber = models.ForeignKey(Terminal, verbose_name='Номер Терминала', on_delete=models.PROTECT)
    dateTime = models.DateTimeField(db_index=True)

    ORDER_TYPE = ['PETROL', 'OTHER']
    ORDER_TYPE = ((type, type) for type in ORDER_TYPE)
    orderType = models.CharField(verbose_name='Тип заказа', choices=ORDER_TYPE, max_length=20)
    barCode = models.CharField(verbose_name='Штрих-код', unique=True, max_length=30)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['orderId', 'terminalNumber'], name='uniqueId')
        ]

    def __str__(self):
        return str(self.id)


class CustomerDetail(models.Model):
    telephone = models.CharField(verbose_name='Телефон', max_length=20, null=True, blank=True)
    email = models.CharField(verbose_name='email', max_length=50, null=True, blank=True)

    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(fields=['telephone', 'email'], name='uniqueCustomer')
    #     ]

    def __str__(self):
        return str(self.telephone) + ' | ' + str(self.email)


class PayType(models.Model):
    PAY_TYPE = ['CASH', 'CARD', 'PCARD']
    PAY_TYPE = ((type, type) for type in PAY_TYPE)
    payType = models.CharField(verbose_name='Тип оплаты', choices=PAY_TYPE, unique=True, max_length=30)

    def __str__(self):
        return self.payType


class OtherType(models.Model):
    OTHER_TYPE = ['MTS', 'TELE2', 'BEELINE', 'MEGAFON', 'EWALLET']
    OTHER_TYPE = ((type, type) for type in OTHER_TYPE)
    otherType = models.CharField(verbose_name='Тип услуги', choices=OTHER_TYPE, unique=True, max_length=20)

    def __str__(self):
        return self.otherType


class OrderOther(models.Model):
    orderId = models.OneToOneField(Order, verbose_name='Номер заказа', related_name='order1',
                                   on_delete=models.CASCADE, primary_key=True)
    fromId = models.OneToOneField(Order, verbose_name='Предыдущий заказ', related_name='order0',
                                  on_delete=models.PROTECT)
    number = models.CharField(verbose_name='Номер', max_length=20)
    amount = models.FloatField(verbose_name='Снято')
    otherType = models.ForeignKey(OtherType, verbose_name='Тип услуги', on_delete=models.PROTECT)
    cash = models.FloatField(verbose_name='Остаток')
    change = models.ForeignKey('self', verbose_name='Перевод сдачи',
                               null=True, blank=True, on_delete=models.PROTECT)

    def __str__(self):
        return str(self.orderId)


class OrderPetrol(models.Model):
    orderId = models.OneToOneField(Order, verbose_name='Номер заказа',
                                   on_delete=models.CASCADE, primary_key=True)
    pump = models.ForeignKey(PumpState, verbose_name='Состояние ТРК', on_delete=models.PROTECT)
    petrol = models.ForeignKey(Petrol, verbose_name='НП', on_delete=models.PROTECT)
    volume = models.FloatField(verbose_name='Объём')
    amount = models.FloatField(verbose_name='Заплачено')
    #customerDetails = models.ForeignKey(CustomerDetail, verbose_name='Персональные данные', on_delete=models.PROTECT)
    telephone = models.CharField(verbose_name='Телефон', max_length=30, null=True, blank=True)
    email = models.CharField(verbose_name='e-mail', max_length=30, null=True, blank=True)
    payType = models.ForeignKey(PayType, verbose_name='Тип оплаты', on_delete=models.PROTECT)
    change = models.ForeignKey('OrderOther', verbose_name='Перевод сдачи',
                               null=True, blank=True, on_delete=models.PROTECT)

    def __str__(self):
        return str(self.orderId)


class Scan(models.Model):
    dateTime = models.DateTimeField(db_index=True)
    terminalNumber = models.ForeignKey(Terminal, verbose_name='Номер Терминала', on_delete=models.PROTECT)
    barCode = models.CharField(verbose_name='Штрих-код', max_length=30)
