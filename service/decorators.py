from urllib.parse import urlencode

from django.http import QueryDict

from service.utils.cases import deep_snake_case_transform


def convert_query_params_to_snake_case(func):
    def func_wrapper(request, *args, **kwargs):
        updated_params = deep_snake_case_transform(request.GET)
        querystring = urlencode(updated_params)
        request.GET = QueryDict(querystring)
        return func(request, *args, **kwargs)
    return func_wrapper
