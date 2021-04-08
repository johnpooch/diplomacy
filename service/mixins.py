from rest_framework import renderers

from .renderers import CamelCaseRenderer
from .parsers import SnakeCaseParser


class ToCamelCase(renderers.JSONRenderer):
    renderer_classes = (CamelCaseRenderer, renderers.BrowsableAPIRenderer)


class FromCamelCase:
    parser_classes = (SnakeCaseParser, )


class CamelCase(FromCamelCase, ToCamelCase):
    pass
