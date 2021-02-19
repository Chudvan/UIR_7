from rest_framework.response import Response
from .models import ErrorType, Error, Order
from .serializers import ErrorTypeSerializer, DateTimeTerminalSerializer, \
    OrderOtherSerializer, OrderPetrolSerializer, ScanSerializer
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import status
from .serializers import countCash, isActivated, getPumpStates, getPetrols


ONLINE = True   #Заглушка для доступа к сети


@api_view(['GET'])
def api_pumps(request):

    if request.method == 'GET':
        #serializer = PumpStateSerializer(pumps, many=True)
        if ONLINE:
            pumpStates = getPumpStates()
            #return Response(serializer.data)
            return Response(pumpStates)
        else:
            return Response(None, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET'])
def api_petrols(request):

    if request.method == 'GET':
        if ONLINE:
            petrols = getPetrols()
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
                if is_list and errorList:
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
    def post(self, request):
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
    def post(self, request):
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
            if amount < 0:
                return Response("This scan has negative amount!",
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({'fromId': order.id, 'amount': amount})
