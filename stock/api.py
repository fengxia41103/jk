# myapp/api.py
from django.http import HttpResponse
from tastypie import resources
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource

from stock.models import *


def build_content_type(format, encoding="utf-8"):
    """
    Appends character encoding to the provided format if not already present.
    """
    if "charset" in format:
        return format

    return "%s; charset=%s" % (format, encoding)


class MyModelResource(resources.ModelResource):
    def create_response(
        self, request, data, response_class=HttpResponse, **response_kwargs
    ):
        """
        Extracts the common "which-format/serialize/return-response" cycle.

        Mostly a useful shortcut/hook.
        """
        desired_format = self.determine_format(request)
        serialized = self.serialize(request, data, desired_format)
        return response_class(
            content=serialized,
            content_type=build_content_type(desired_format),
            **response_kwargs
        )
