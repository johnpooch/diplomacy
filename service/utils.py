import json
import re

from core import models
from core.models.base import OrderType

hold_regex = r'^(?P<source>[\w.() \-]+?(?= HOLD)) (?P<type>HOLD) -> (?P<outcome>[\w.() \-]+)'
move_regex = r'^(?P<source>[\w.() \-]+?(?= MOVE| RETREAT)) (?P<type>MOVE|RETREAT) (?P<target>[\w.() \-]+) -> (?P<outcome>[\w.() \-]+)'
aux_regex = r'^(?P<source>[\w.() \-]+?(?= MOVE| HOLD| CONVOY| SUPPORT| RETREAT)) (?P<type>MOVE|HOLD|SUPPORT|CONVOY|RETREAT) (?P<aux>[\w.() \-]+?(?= to)) to (?P<target>[\w.() \-]+) -> (?P<outcome>[\w.() \-]+)'
build_regex = r'^(?P<type>BUILD|DISBAND) (?P<piece_type>fleet|army) (?P<source>[\w.() \-]+) -> (?P<outcome>[\w.() \-]+)'


def form_to_data(form):
    result = {}
    for name, field in form.fields.items():
        result[name] = field_to_dict(field)
    return result


def field_to_dict(field):
    data = {
        "type": field.__class__.__name__,
        "widget_type": field.widget.__class__.__name__,
        "hidden": field.widget.is_hidden,
        "required": field.widget.is_required,
        "label": field.label,
        "help_text": field.help_text,
        "initial_value": field.initial,
    }
    choices = getattr(field, 'choices', None)
    if choices:
        data['choices'] = choices

    min_value = getattr(field, 'max_value', None)
    max_value = getattr(field, 'min_value', None)
    min_length = getattr(field, 'min_length', None)
    max_length = getattr(field, 'max_length', None)

    if min_value:
        data['min_value'] = min_value
    if max_value:
        data['max_value'] = max_value
    if min_length:
        data['min_length'] = min_length
    if max_length:
        data['max_length'] = max_length
    return data


def text_to_order_data(text):
    """
    Tool to convert order history from Play Diplomacy to json data.
    """
    orders = []
    nation_dict = {
        'Austria': 'Austria-Hungary'
    }
    territory_dict = {
        'st. petersburg (south coast)': 'st. petersburg',
        'st. petersburg (north coast)': 'st. petersburg',
    }
    regex_dict = {
        OrderType.HOLD: hold_regex,
        OrderType.MOVE: move_regex,
        OrderType.RETREAT: move_regex,
        OrderType.SUPPORT: aux_regex,
        OrderType.CONVOY: aux_regex,
        OrderType.BUILD: build_regex,
    }

    def _lower_groups(groups):
        for k, v in groups.items():
            if v:
                groups[k] = v.lower()
        return groups

    order_blocks = text.split('\n\n')
    for block in order_blocks:
        lines = block.split('\n')
        nation = lines[0].lower()
        nation = nation.title()
        nation = nation_dict.get(nation, nation)

        for line in lines[1:]:
            m = re.search('MOVE|HOLD|SUPPORT|CONVOY|BUILD', line)
            if not m:
                break
            order = m.group(0)
            regex = regex_dict[order.lower()]
            m = re.search(regex, line)
            data = _lower_groups(m.groupdict())
            data['nation'] = nation
            if '(' in data['source'] and data['type'] == OrderType.BUILD:
                coast = data['source'].replace('(', '')
                data['target_coast'] = coast.replace(')', '')
            data['source'] = territory_dict.get(data['source'], data['source'])
            target = data.get('target')
            if target:
                if '(' in data['target']:
                    coast = data['target'].replace('(', '')
                    data['target_coast'] = coast.replace(')', '')
                data['target'] = territory_dict.get(data['target'], data['target'])
            aux = data.get('aux')
            if aux:
                data['aux'] = territory_dict.get(aux, data['aux'])
            outcome = data.pop('outcome')
            orders.append(
                {
                    'outcome': outcome,
                    'order': data
                }
            )
    return json.dumps(orders)


def text_to_orders(text):
    """
    Tool to convert order history from Play Diplomacy to order models.
    """
    orders = []
    nation_dict = {
        'Austria': 'Austria-Hungary'
    }
    territory_dict = {
        'bulgaria (south coast)': 'bulgaria',
        'bulgaria (north coast)': 'bulgaria',
        'spain (south coast)': 'spain',
        'spain (north coast)': 'spain',
        'st. petersburg (north coast)': 'st. petersburg',
        'st. petersburg (south coast)': 'st. petersburg',
    }
    regex_dict = {
        OrderType.HOLD: hold_regex,
        OrderType.MOVE: move_regex,
        OrderType.RETREAT: move_regex,
        OrderType.SUPPORT: aux_regex,
        OrderType.CONVOY: aux_regex,
        OrderType.BUILD: build_regex,
    }

    def _lower_groups(groups):
        for k, v in groups.items():
            if v:
                groups[k] = v.lower()
        return groups

    order_blocks = text.split('\n\n')
    for block in order_blocks:
        lines = block.split('\n')
        nation = lines[0].lower()
        nation = nation.title()
        nation = nation_dict.get(nation, nation)

        for line in lines[1:]:
            m = re.search('MOVE|HOLD|SUPPORT|CONVOY|BUILD|RETREAT|DISBAND', line)
            if not m:
                break
            order = m.group(0)
            regex = regex_dict[order.lower()]
            m = re.search(regex, line)
            data = _lower_groups(m.groupdict())
            data['nation'] = nation
            if '(' in data['source'] and data['type'] == OrderType.BUILD:
                coast = data['source'].replace('(', '')
                data['target_coast'] = coast.replace(')', '')
            data['source'] = territory_dict.get(data['source'], data['source'])
            target = data.get('target')
            if target:
                if '(' in data['target'] and data['type'] in [OrderType.BUILD, OrderType.MOVE]:
                    coast = data['target'].replace('(', '')
                    data['target_coast'] = coast.replace(')', '')
                target = territory_dict.get(data['target'], data['target'])
            aux = data.get('aux')
            if aux:
                aux = territory_dict.get(data['aux'], data['aux'])
            source = data['source']

            target_coast = data.get('target_coast')

            if source:
                data['source'] = models.Territory.objects.get(name=source)
            if target:
                if target == 'hold':
                    target = aux
                data['target'] = models.Territory.objects.get(name=target)
            if aux:
                data['aux'] = models.Territory.objects.get(name=aux)
            if target_coast:
                data['target_coast'] = models.NamedCoast.objects.get(name=target_coast)
            data['nation'] = models.Nation.objects.get(
                name=data['nation'],
                variant__name='Standard'
            )
            data.pop('outcome')
            orders.append(models.Order(**data))
    return orders
