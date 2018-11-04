import json

from rest_framework.renderers import JSONRenderer
from rest_framework.utils.serializer_helpers import ReturnList, ReturnDict


class ProfileJSONRenderer(JSONRenderer):

    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):

        if type(data) != ReturnList:
            errors = data.get('errors', None)
            if errors is not None:
                return super().render(data)

        if type(data) != ReturnDict:
            return json.dumps({
                'profiles': data
            })
        else:
            return json.dumps({
                'profiles': data
            })
