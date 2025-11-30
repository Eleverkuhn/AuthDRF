from rest_framework.views import APIView

from authdrf.web.views.base_views import BaseViewMixin, ProtectedViewMixin
from authdrf.web.serializers.user_serializers import UserSerializer


class UserPageView(ProtectedViewMixin, BaseViewMixin, APIView):
    template_name = "my.xhtml"
    serializer_class = UserSerializer
