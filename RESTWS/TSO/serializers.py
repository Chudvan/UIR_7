from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError
from .models import PumpState, Petrol, ErrorType, DateTimeTerminal, \
    Terminal, OtherType, Order, OrderOther, OrderPetrol, \
    CustomerDetail, PayType, Pump, Scan
import random
import string
import datetime


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


def createBarcode():
    barcode = buildblock(BARCODE_LEN)
    while not isUniqueBarcode(barcode):
        barcode = buildblock(BARCODE_LEN)
    return barcode


def findOrder(pk):
    try:
        order = Order.objects.get(pk=pk)
        return order
    except Order.DoesNotExist:
        return


def isActivated(order):
    if order.orderType == 'OTHER':
        try:
            change = OrderOther.objects.get(orderId=order).change
        except OrderOther.DoesNotExist:
            return Response("Failed to find OrderOther!", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    elif order.orderType == 'PETROL':
        try:
            change = OrderPetrol.objects.get(orderId=order).change
        except OrderPetrol.DoesNotExist:
            return Response("Failed to find OrderPetrol!", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if change is not None:
        return True
    return False


def countCash(order, amount):
    if order.orderType == 'OTHER':
        lastCash = OrderOther.objects.get(orderId=order).cash
    elif order.orderType == 'PETROL':
        price = OrderPetrol.objects.get(orderId=order).petrol.price
        volume = OrderPetrol.objects.get(orderId=order).volume
        lastAmount = OrderPetrol.objects.get(orderId=order).amount
        lastCash = lastAmount - price * volume
    return lastCash - amount


def makeChange(fromId, orderOther):
    if fromId.orderType == 'OTHER':
        previous = OrderOther.objects.get(orderId=fromId)
        previous.change = orderOther
        previous.save()
    elif fromId.orderType == 'PETROL':
        previous = OrderPetrol.objects.get(orderId=fromId)
        previous.change = orderOther
        previous.save()


class OrderOtherSerializer(serializers.Serializer):
    terminalNumber = serializers.IntegerField()
    id = serializers.IntegerField()
    fromId = serializers.IntegerField()
    dateTime = serializers.DateTimeField()
    otherType = serializers.CharField()
    number = serializers.CharField()
    amount = serializers.FloatField()

    def create(self, validated_data):
        serializer = OtherTypeSerializer(data={"otherType": validated_data['otherType']})
        if serializer.is_valid(raise_exception=True):
            #print("\n\n\n\nHERE\n\n\n\n")
            otherType = OtherType.objects.get(otherType=validated_data['otherType'])
            #print("\n\n\n\nHERE2\n\n\n\n")

            terminal = findTerminal(validated_data['terminalNumber'])
            if terminal is None:
                return Response("Terminal doesn't exist!", status=status.HTTP_400_BAD_REQUEST)
            fromId = findOrder(validated_data['fromId'])
            if fromId is None:
                return Response("Order fromId doesn't exist!", status=status.HTTP_400_BAD_REQUEST)
            activation = isActivated(fromId)
            if type(activation) == Response:
                return activation
            if isActivated(fromId):
                return Response("This scan has already activated!", status=status.HTTP_403_FORBIDDEN)

            barcode = createBarcode()

            try:
                orderId = Order(orderId=validated_data['id'],
                                terminalNumber=terminal,
                                dateTime=validated_data['dateTime'],
                                orderType='OTHER',
                                barCode=barcode)
                orderId.save()
                # print(orderId)
            except IntegrityError:
                # print(validated_data['id'], terminal, validated_data['dateTime'], barcode)
                return Response("Order still exists!", status=status.HTTP_400_BAD_REQUEST)

            cash = countCash(fromId, validated_data['amount'])
            if cash < 0:
                orderId.delete()
                return Response("This OrderOther has negative cash!",
                                status=status.HTTP_400_BAD_REQUEST)
            #print("\n\n\n\nHERE3\n\n\n\n")
            try:
                orderOther = OrderOther.objects.create(orderId=orderId,
                                                 fromId=fromId,
                                                 number=validated_data['number'],
                                                 amount=validated_data['amount'],
                                                 otherType=otherType,
                                                 cash=cash)
            except IntegrityError:
                #LOGGING
                return Response("Failed to create OrderOther!", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            makeChange(fromId, orderOther)

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


def getPumpStates():
    pumpStates = []
    listDictPumps = list(PumpState.objects.all().values('number').distinct())
    # print('\n\n\n', listDictPumps, '\n\n\n')
    for dictPump in listDictPumps:
        pkPump = dictPump['number']
        # print(type(numberPump))
        pumpObject = Pump.objects.all().get(pk=pkPump)
        pumpStateObjects = PumpState.objects.all().filter(number=pumpObject)
        pumpState = pumpStateObjects.order_by('-datetime')[0]
        serializer = PumpStateSerializer(pumpState)
        pumpStates.append(serializer.data)
    return pumpStates


def getPetrols():
    petrols = []
    listDictPetrols = list(Petrol.objects.all().values('petrolType').distinct())
    for dictPetrol in listDictPetrols:
        petrolType = dictPetrol['petrolType']
        petrolObjects = Petrol.objects.all().filter(petrolType=petrolType)
        petrol = petrolObjects.order_by('-datetime')[0]
        serializer = PetrolSerializer(petrol)
        petrols.append(serializer.data)
    return petrols


def findPump(number):
    try:
        pump = Pump.objects.get(number=number)
        return pump
    except Pump.DoesNotExist:
        return


def isActualPumpState(pumpState):
    # print(getPumpStates())
    # print(dict(pumpState))
    # print(dict(pumpState) in getPumpStates())
    return dict(pumpState) in getPumpStates()


def isActualPetrol(petrol):
    return dict(petrol) in getPetrols()


def findCustomerDetail(telephone, email):
    try:
        customerDetail = CustomerDetail.objects.get(telephone=telephone, email=email)
        return customerDetail
    except CustomerDetail.DoesNotExist:
        return


def checkPumpState(validated_data):
    pump = findPump(validated_data['pump']['number'])
    if pump is None:
        return Response("Pump doesn't exist!", status=status.HTTP_400_BAD_REQUEST)
    pumpStates = PumpState.objects.all().filter(number=pump, status=validated_data['pump']['status'])
    if not list(pumpStates):
        return Response("PumpState doesn't exist!", status=status.HTTP_400_BAD_REQUEST)
    if not isActualPumpState(validated_data['pump']):
        return Response("PumpState is irrelevant!", status=status.HTTP_400_BAD_REQUEST)
    pumpStatus = validated_data['pump']['status']
    if pumpStatus != 'FREE':
        return Response("Pump is {status} now!".format(status=pumpStatus), status=status.HTTP_400_BAD_REQUEST)
    pumpState = pumpStates.order_by("-datetime")[0]
    return pump, pumpState


def checkPetrol(validated_data):
    petrols = Petrol.objects.all().filter(petrolType=validated_data['petrol']['petrolType'],
                                          price=validated_data['petrol']['price'])
    if not list(petrols):
        return Response("Petrol doesn't exist!", status=status.HTTP_400_BAD_REQUEST)
    if not isActualPetrol(validated_data['petrol']):
        return Response("Petrol is irrelevant!", status=status.HTTP_400_BAD_REQUEST)
    petrol = petrols.order_by("-datetime")[0]
    return petrol


def getCustomerDetail(validated_data):
    try:
        customerDetail = CustomerDetail(telephone=validated_data['customerDetails']['telephone'],
                                        email=validated_data['customerDetails']['email'])
        customerDetail.save()
    except IntegrityError:
        customerDetail = findCustomerDetail(telephone=validated_data['customerDetails']['telephone'],
                                            email=validated_data['customerDetails']['email'])
        return customerDetail


def checkPayType(validated_data):
    serializers = PayTypeSerializer(data={'payType': validated_data['payType']})
    if serializers.is_valid(raise_exception=True):
        payType = PayType.objects.get(payType=validated_data['payType'])
        return payType


def getOrderId(validated_data, terminal, barcode):
    try:
        orderId = Order(orderId=validated_data['id'],
                        terminalNumber=terminal,
                        dateTime=validated_data['dateTime'],
                        orderType='PETROL',
                        barCode=barcode)
        orderId.save()
        # print(orderId)
        return orderId
    except IntegrityError:
        # print(validated_data['id'], terminal, validated_data['dateTime'], barcode)
        return Response("Order still exists!", status=status.HTTP_400_BAD_REQUEST)


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

        result = checkPumpState(validated_data)
        if type(result) == Response:
            return result
        else:
            pump, pumpState = result

        petrol = checkPetrol(validated_data)
        if type(petrol) == Response:
            return petrol

        customerDetail = getCustomerDetail(validated_data)

        payType = checkPayType(validated_data)

        barcode = createBarcode()

        orderId = getOrderId(validated_data, terminal, barcode)
        if type(orderId) == Response:
            return orderId

        orderPetrol = OrderPetrol.objects.create(orderId=orderId,
                                                 pump=pumpState,
                                                 petrol=petrol,
                                                 volume=validated_data['volume'],
                                                 amount=validated_data['amount'],
                                                 customerDetails=customerDetail,
                                                 payType=payType)

        PumpState.objects.create(datetime=datetime.datetime.now(),
                                             status='BUSY', number=pump)
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
