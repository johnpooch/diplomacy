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
