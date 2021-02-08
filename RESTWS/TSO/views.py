from rest_framework.response import Response
from .models import PumpState, Pump, Petrol, ErrorType, Error, Order
from .serializers import PumpStateSerializer, PetrolSerializer, \
    ErrorTypeSerializer, DateTimeTerminalSerializer, OrderOtherSerializer, \
    OrderPetrolSerializer, ScanSerializer
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import status
from .serializers import countCash, isActivated


ONLINE = True   #Заглушка для доступа к сети


@api_view(['GET'])
def api_pumps(request):

    if request.method == 'GET':
        pumps = []
        listDictPumps = list(PumpState.objects.all().values('number').distinct())
        #print('\n\n\n', listDictPumps, '\n\n\n')
        for dictPump in listDictPumps:
            pkPump = dictPump['number']
            #print(type(numberPump))
            pumpObject = Pump.objects.all().get(pk=pkPump)
            pumpStateObjects = PumpState.objects.all().filter(number=pumpObject)
            pumpState = pumpStateObjects.order_by('-datetime')[0]
            serializer = PumpStateSerializer(pumpState)
            pumps.append(serializer.data)
        #serializer = PumpStateSerializer(pumps, many=True)
        if ONLINE:
            #return Response(serializer.data)
            return Response(pumps)
        else:
            return Response(None, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET'])
def api_petrols(request):

    if request.method == 'GET':
        petrols = []
        listDictPetrols = list(Petrol.objects.all().values('petrolType').distinct())
        for dictPetrol in listDictPetrols:
            petrolType = dictPetrol['petrolType']
            petrolObjects = Petrol.objects.all().filter(petrolType=petrolType)
            petrol = petrolObjects.order_by('-datetime')[0]
            serializer = PetrolSerializer(petrol)
            petrols.append(serializer.data)
        if ONLINE:
            return Response(petrols)
        else:
            return Response(None, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class SessionView(APIView):
    def get(self, request):
        if ONLINE:
            return Response()
        else:
            return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)

    def post(self, request):
        if ONLINE:
            serializer = DateTimeTerminalSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                errors = serializer.save()
                if type(errors) is Response:
                    return errors
                errorList = request.data.get('errorList', None)
                if errorList is None:
                    return Response("errorList - Обязательное поле.",
                                    status=status.HTTP_400_BAD_REQUEST)
                is_list = isinstance(errorList, list)
                if is_list:
                    for error in errorList:
                        serializer = ErrorTypeSerializer(data=error)
                        if serializer.is_valid(raise_exception=True):
                            errorString = dict(serializer.validated_data)['errortype']
                            errorType = ErrorType.objects.get(errortype=errorString)
                            errorObject = Error(dateTime=errors.dateTime,
                                                terminalNumber=errors.terminalNumber,
                                                errorType=errorType)
                            errorObject.save()
                    return Response()
                else:
                    return Response("Attribute errorList must be a list of Errors!",
                                    status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)


class OrderOtherView(APIView):
    def put(self, request):
        #print(request.data)
        if ONLINE:
            serializer = OrderOtherSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                result = serializer.save()
                if type(result) == Response:
                    return result
            '''
            fromId = request.data.get('fromId')
            if fromId is None or type(fromId) != int:
                raise("No fromId int atribute!")
            try:
                #fromIdObject = Order.objects.get(pk=fromId)
                otherType = request.data.get('otherType')
                if otherType is None or type(otherType) != str:
                    raise ("No otherType str atribute!")
                serializer = OtherTypeSerializer(data={'otherType': otherType})
                if serializer.is_valid(raise_exception=True):
                    serializer = DateTimeTerminalSerializer(data=request.data)
                    if serializer.is_valid(raise_exception=True):
                        DateTimeTerminal = serializer.save()
                        serializer = OrderSerializer(data=request.data)
                        if serializer.is_valid(raise_exception=True):
                            print("here")
            except Order.DoesNotExist:
                raise ("No Order!")
            '''
            return Response()
        else:
            return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)


class OrderPetrolView(APIView):
    def put(self, request):
        #print(request.data)
        if ONLINE:
            serializer = OrderPetrolSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                result = serializer.save()
                if type(result) == Response:
                    return result
            return Response()
        else:
            return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)


def findBarCode(barCode):
    try:
        order = Order.objects.get(barCode=barCode)
        return order
    except Order.DoesNotExist:
        return


class ScanView(APIView):
    def post(self, request):
        #print(request.data)
        serializer = ScanSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            result = serializer.save()
            if type(result) == Response:
                return result
            order = findBarCode(result.barCode)
            if order is None:
                return Response(status=status.HTTP_404_NOT_FOUND)
            if isActivated(order):
                return Response("This scan has already activated!", status=status.HTTP_403_FORBIDDEN)
            amount = countCash(order, 0)
            return Response({'fromId': order.id, 'amount': amount})
