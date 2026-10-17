from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Block
from .serializers import BlockSerializer, ReportSerializer


class ReportCreateView(generics.CreateAPIView):
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]


class BlockListCreateView(generics.ListCreateAPIView):
    serializer_class = BlockSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Block.objects.filter(blocker=self.request.user)


class UnblockView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, user_id):
        deleted, _ = Block.objects.filter(blocker=request.user, blocked_user_id=user_id).delete()
        if not deleted:
            return Response(
                {"error": True, "message": "Block not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
