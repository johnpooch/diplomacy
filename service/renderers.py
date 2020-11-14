from rest_framework import renderers

from service.utils.cases import deep_camel_case_transform


class CamelCaseRenderer(renderers.JSONRenderer):
    def render(self, data, *args, **kwargs):
        camelized_data = deep_camel_case_transform(data)
        return super().render(camelized_data, *args, **kwargs)
