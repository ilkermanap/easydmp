from psycopg2.extras import DateRange

from django import forms
from django.core.exceptions import ValidationError
from django.forms.widgets import MultiWidget
from django.utils.translation import ugettext_lazy as _

from .widgets import *

__all__ = [
    'DateRangeField',
    'NamedURLField',
    'ChoiceNotListedField',
    'MultipleChoiceNotListedField',
    'DMPTypedReasonField',
]


class DateRangeField(forms.MultiValueField):
    widget = DateRangeWidget
    default_error_messages = {'invalid': _('Enter two valid dates.')}
    base_field = forms.DateField
    range_type = DateRange
    default_error_messages = {
        'invalid': _('Enter two valid values.'),
        'bound_ordering': _('The start of the range must not exceed the end of the range.'),
    }
    required = True
    require_all_fields = True

    def __init__(self, *args, **kwargs):
        fields = [
            self.base_field(), self.base_field()
        ]
        super().__init__(fields, *args, **kwargs)

    def prepare_value(self, value):
        lower_base, upper_base = self.fields
        if isinstance(value, self.range_type):
            return [
                lower_base.prepare_value(value.lower),
                upper_base.prepare_value(value.upper),
            ]
        if not value:
            return [
                lower_base.prepare_value(None),
                upper_base.prepare_value(None),
            ]
        return value

    def compress(self, values):
        if not values:
            return None
        lower, upper = values
        if lower is not None and upper is not None and lower > upper:
            raise ValidationError(
                self.error_messages['bound_ordering'],
                code='bound_ordering',
            )
        try:
            range_value = self.range_type(lower, upper)
        except TypeError:
            raise ValidationError(
                self.error_messages['invalid'],
                code='invalid',
            )
        else:
            return range_value


class NamedURLField(forms.MultiValueField):

    def __init__(self, *args, **kwargs):
        kwargs['widget'] = NamedURLWidget
        kwargs['require_all_fields'] = False
        fields = [
            forms.URLField(
                required=True,
                error_messages={
                    'incomplete': 'Enter at least a URL',
                }
            ),
            forms.CharField(required=False),
        ]
        super().__init__(fields, *args, **kwargs)

    def compress(self, value):
        if self.required:
            if not value[0]:
                raise ValidationError('URL not entered')
            return {'url': value[0], 'name': value[1]}
        return {}


class NotListedMixin:

    def __init__(self, widget, fields, attrs=None, choices=(), *args, **kwargs):
        error_messages = {
            'incomplete': 'At least one of the fields must be filled out',
        }
        kwargs['require_all_fields'] = True
        self.original_required = kwargs.get('required', None)
        kwargs['required'] = False
        super().__init__(fields=fields, widget=widget,
                         error_messages=error_messages, *args, **kwargs)

    def _validate(self, value):
        values = (value.get('choices', False), value.get('not-listed', False))
        if not any(values):
            raise ValidationError(self.error_messages['incomplete'], code='incomplete')

    def validate(self, value):
        if self.original_required:
            self._validate(value)

    def compress(self, value):
        if not any(value):
            return {}
        return {'choices': value[0], 'not-listed': value[1]}


class ChoiceNotListedField(NotListedMixin, forms.MultiValueField):

    def __init__(self, attrs=None, choices=(), *args, **kwargs):
        widget = SelectNotListed(attrs=attrs, choices=choices)
        fields = [
            forms.ChoiceField(required=False, choices=choices),
            forms.BooleanField(required=False),
        ]
        super().__init__(fields=fields, widget=widget, *args, **kwargs)


class MultipleChoiceNotListedField(NotListedMixin, forms.MultiValueField):

    def __init__(self, attrs=None, choices=(), *args, **kwargs):
        widget = SelectMultipleNotListed(attrs=attrs, choices=choices)
        fields = [
            forms.MultipleChoiceField(required=False, choices=choices),
            forms.BooleanField(required=False),
        ]
        super().__init__(fields=fields, widget=widget, *args, **kwargs)


class DMPTypedReasonField(forms.MultiValueField):

    def __init__(self, *args, **kwargs):
        kwargs['widget'] = DMPTypedReasonWidget
        kwargs['require_all_fields'] = True
        kwargs['required'] = False
        fields = [
            forms.CharField(
                required=True, error_messages={'incomplete': 'Enter a data type.'},
            ),
            forms.CharField(
                required=True, error_messages={'incomplete': 'Enter a reason.'},
            ),
            forms.URLField(required=False),
        ]
        super().__init__(fields, *args, **kwargs)

    def compress(self, value):
        if not value:
            raise ValidationError(self.error_messages['incomplete'], code='incomplete')
        return {'type': value[0], 'reason': value[1], 'url': value[2]}
