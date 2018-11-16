import json

from rest_framework.renderers import JSONRenderer


class ReportJSONRenderer(JSONRenderer):
    object_label = 'report'
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        """
        Render reports
        """
        if data is not None:
            if len(data) <= 1:
                return json.dumps({
                    'report': data
                })
            return json.dumps({
                'reports': data
            })
        return json.dumps({
            'report': 'No report found.'
        })