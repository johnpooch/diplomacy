import json
import re

from core.models.base import OrderType

hold_regex = r'^(?P<source>[\w.() \-]+?(?= HOLD)) (?P<type>HOLD) -> (?P<outcome>[\w.() \-]+)'
move_regex = r'^(?P<source>[\w.() \-]+?(?= MOVE| RETREAT)) (?P<type>MOVE|RETREAT) (?P<target>[\w.() \-]+) -> (?P<outcome>[\w.() \-]+)'
aux_regex = r'^(?P<source>[\w.() \-]+?(?= MOVE| HOLD| CONVOY| SUPPORT| RETREAT)) (?P<type>MOVE|HOLD|SUPPORT|CONVOY|RETREAT) (?P<aux>[\w.() \-]+?(?= to)) to (?P<target>[\w.() \-]+) -> (?P<outcome>[\w.() \-]+)'

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
    regex_dict = {
        OrderType.HOLD: hold_regex,
        OrderType.MOVE: move_regex,
        OrderType.RETREAT: move_regex,
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
            m = re.search('MOVE|HOLD', line)
            if not m:
                break
            order = m.group(0)
            regex = regex_dict[order.lower()]
            m = re.search(regex, line)
            data = _lower_groups(m.groupdict())
            data['nation'] = nation
            outcome = data.pop('outcome')
            orders.append(
                {
                    'outcome': outcome,
                    'order': data
                }
            )

    return json.dumps(orders)