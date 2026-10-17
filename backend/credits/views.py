from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CreditLedger
from .serializers import CreditBalanceSerializer, CreditLedgerSerializer


class CreditBalanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(CreditBalanceSerializer.from_user(request.user))


class CreditLedgerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        entries = CreditLedger.objects.filter(user=request.user)
        return Response(CreditLedgerSerializer(entries, many=True).data)
