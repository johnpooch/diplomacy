from rest_framework import renderers

from .renderers import CamelCaseRenderer
from .parsers import SnakeCaseParser


class ToCamelCase(renderers.JSONRenderer):
    renderer_classes = (CamelCaseRenderer, )


class FromCamelCase:
    parser_classes = (SnakeCaseParser, )
