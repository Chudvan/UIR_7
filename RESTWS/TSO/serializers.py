from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError
from .models import PumpState, Petrol, ErrorType, DateTimeTerminal, \
    Terminal, OtherType, Order, OrderOther, OrderPetrol, \
    CustomerDetail, PayType, Pump, Scan
import random
import string


BARCODE_LEN = 12

'''
class PumpStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PumpState
        fields = ('number', 'status')
'''


class PumpStateSerializer(serializers.Serializer):
    number = serializers.IntegerField()

    PUMP_STATUS = ['FREE', 'BUSY', 'UNAVAILABLE']
    status = serializers.ChoiceField(choices=PUMP_STATUS)


class PetrolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Petrol
        fields = ('petrolType', 'price')


class ErrorTypeSerializer(serializers.Serializer):
    ERROR_TYPE = ['OK', 'SCANER', 'PAPER', 'CURRENCYDETECTOR', 'INK', 'POS', 'OTHER']
    errortype = serializers.ChoiceField(choices=ERROR_TYPE)

    def create(self, validated_data):
        return ErrorType(**validated_data)


def findTerminal(terminalNumber):
    try:
        terminal = Terminal.objects.get(terminalNumber=terminalNumber)
        return terminal
    except Terminal.DoesNotExist:
        return


class DateTimeTerminalSerializer(serializers.Serializer):
    dateTime = serializers.DateTimeField()
    terminalNumber = serializers.IntegerField()

    def create(self, validated_data):
        terminal = findTerminal(validated_data['terminalNumber'])
        if terminal is None:
            return Response("Terminal doesn't exist!", status=status.HTTP_400_BAD_REQUEST)
        validated_data['terminalNumber'] = terminal
        return DateTimeTerminal(**validated_data)


class OtherTypeSerializer(serializers.Serializer):
    OTHER_TYPE = ['MTS', 'TELE2', 'BEELINE', 'MEGAFON', 'EWALLET']
    otherType = serializers.ChoiceField(choices=OTHER_TYPE)

    def create(self, validated_data):
        return OtherType(**validated_data)


def buildblock(size):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(size))


def isUniqueBarcode(barcode):
    try:
        Order.objects.get(barCode=barcode)
        return False
    except Order.DoesNotExist:
        return True


def findOrder(pk):
    try:
        order = Order.objects.get(pk=pk)
        return order
    except Order.DoesNotExist:
        return


def countCash(order, amount):
    if order.orderType == 'OTHER':
        lastCash = OrderOther.objects.get(orderId=order).cash
    elif order.orderType == 'PETROL':
        price = OrderPetrol.objects.get(orderId=order).petrol.price
        volume = OrderPetrol.objects.get(orderId=order).volume
        lastAmount = OrderPetrol.objects.get(orderId=order).amount
        lastCash = lastAmount - price * volume
    return lastCash - amount


class OrderOtherSerializer(serializers.Serializer):
    terminalNumber = serializers.IntegerField()
    id = serializers.IntegerField()
    fromId = serializers.IntegerField()
    dateTime = serializers.DateTimeField()
    otherType = serializers.CharField()
    number = serializers.CharField()
    amount = serializers.FloatField()

    def create(self, validated_data):
        terminal = findTerminal(validated_data['terminalNumber'])
        if terminal is None:
            return Response("Terminal doesn't exist!", status=status.HTTP_400_BAD_REQUEST)
        barcode = buildblock(BARCODE_LEN)
        while not isUniqueBarcode(barcode):
            barcode = buildblock(BARCODE_LEN)
        try:
            orderId = Order(orderId=validated_data['id'],
                  terminalNumber=terminal,
                  dateTime=validated_data['dateTime'],
                  orderType='OTHER',
                  barCode=barcode)
            orderId.save()
            #print(orderId)
        except IntegrityError:
            #print(validated_data['id'], terminal, validated_data['dateTime'], barcode)
            return Response("Order still exists!", status=status.HTTP_400_BAD_REQUEST)
        else:
            fromId = findOrder(validated_data['fromId'])
            if fromId is None:
                return Response("Order fromId doesn't exist!", status=status.HTTP_400_BAD_REQUEST)
            serializer = OtherTypeSerializer(data={"otherType": validated_data['otherType']})
            if serializer.is_valid(raise_exception=True):
                #print("\n\n\n\nHERE\n\n\n\n")
                otherType = OtherType.objects.get(otherType=validated_data['otherType'])
                #print("\n\n\n\nHERE2\n\n\n\n")
                cash = countCash(fromId, validated_data['amount'])
                #print("\n\n\n\nHERE3\n\n\n\n")
                orderOther = OrderOther.objects.create(orderId=orderId,
                                                 fromId=fromId,
                                                 number=validated_data['number'],
                                                 amount=validated_data['amount'],
                                                 otherType=otherType,
                                                 cash=cash)
                if fromId.orderType == 'OTHER':
                    previous = OrderOther.objects.get(orderId=fromId)
                    previous.change = orderOther
                    previous.save()
                elif fromId.orderType == 'PETROL':
                    previous = OrderPetrol.objects.get(orderId=fromId)
                    previous.change = orderOther
                    previous.save()
                return orderOther


class CustomerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerDetail
        fields = ('telephone', 'email')


class PayTypeSerializer(serializers.Serializer):
    PAY_TYPE = ['CASH', 'CARD', 'PCARD']
    payType = serializers.ChoiceField(choices=PAY_TYPE)

    def create(self, validated_data):
        return PayType(**validated_data)


def findPump(number):
    try:
        pump = Pump.objects.get(number=number)
        return pump
    except Pump.DoesNotExist:
        return


def findCustomerDetail(telephone, email):
    try:
        customerDetail = CustomerDetail.objects.get(telephone=telephone, email=email)
        return customerDetail
    except CustomerDetail.DoesNotExist:
        return


class OrderPetrolSerializer(serializers.Serializer):
    terminalNumber = serializers.IntegerField()
    id = serializers.IntegerField()
    dateTime = serializers.DateTimeField()
    pump = PumpStateSerializer()
    petrol = PetrolSerializer()
    volume = serializers.FloatField()
    amount = serializers.FloatField()
    customerDetails = CustomerDetailSerializer()
    payType = serializers.CharField()

    def create(self, validated_data):
        terminal = findTerminal(validated_data['terminalNumber'])
        if terminal is None:
            return Response("Terminal doesn't exist!", status=status.HTTP_400_BAD_REQUEST)
        pump = findPump(validated_data['pump']['number'])
        if pump is None:
            return Response("Pump doesn't exist!", status=status.HTTP_400_BAD_REQUEST)
        pumpStates = PumpState.objects.all().filter(number=pump, status=validated_data['pump']['status'])
        if not list(pumpStates):
            return Response("PumpState doesn't exist!", status=status.HTTP_400_BAD_REQUEST)
        pumpState = pumpStates.order_by("-datetime")[0]
        petrols = Petrol.objects.all().filter(petrolType=validated_data['petrol']['petrolType'],
                                              price=validated_data['petrol']['price'])
        if not list(petrols):
            return Response("Petrol doesn't exist!", status=status.HTTP_400_BAD_REQUEST)
        petrol = petrols.order_by("-datetime")[0]
        try:
            customerDetail = CustomerDetail(telephone=validated_data['customerDetails']['telephone'],
                           email=validated_data['customerDetails']['email'])
            customerDetail.save()
        except IntegrityError:
            customerDetail = findCustomerDetail(telephone=validated_data['customerDetails']['telephone'],
                                                email=validated_data['customerDetails']['email'])
        serializers = PayTypeSerializer(data={'payType': validated_data['payType']})
        if serializers.is_valid(raise_exception=True):
            payType = PayType.objects.get(payType=validated_data['payType'])
        barcode = buildblock(BARCODE_LEN)
        while not isUniqueBarcode(barcode):
            barcode = buildblock(BARCODE_LEN)
        try:
            orderId = Order(orderId=validated_data['id'],
                            terminalNumber=terminal,
                            dateTime=validated_data['dateTime'],
                            orderType='PETROL',
                            barCode=barcode)
            orderId.save()
            #print(orderId)
        except IntegrityError:
            #print(validated_data['id'], terminal, validated_data['dateTime'], barcode)
            return Response("Order still exists!", status=status.HTTP_400_BAD_REQUEST)
        orderPetrol = OrderPetrol.objects.create(orderId=orderId,
                                                 pump=pumpState,
                                                 petrol=petrol,
                                                 volume=validated_data['volume'],
                                                 amount=validated_data['amount'],
                                                 customerDetails=customerDetail,
                                                 payType=payType)
        return orderPetrol


class ScanSerializer(serializers.Serializer):
    terminalNumber = serializers.IntegerField()
    dateTime = serializers.DateTimeField()
    barCode = serializers.CharField()

    def create(self, validated_data):
        terminal = findTerminal(validated_data['terminalNumber'])
        if terminal is None:
            return Response("Terminal doesn't exist!", status=status.HTTP_400_BAD_REQUEST)
        scan = Scan.objects.create(terminalNumber=terminal,
                                   dateTime=validated_data['dateTime'],
                                   barCode=validated_data['barCode'])
        return scan
