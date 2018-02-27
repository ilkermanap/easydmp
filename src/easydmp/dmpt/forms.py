from datetime import date

from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from easydmp.eestore.models import EEStoreCache

from .models import Template
from .models import ExternalChoiceQuestion
from .fields import DateRangeField
from .fields import NamedURLField
from .fields import ChoiceNotListedField
from .fields import MultipleChoiceNotListedField
from .fields import DMPTypedReasonField
from .widgets import Select2Widget
from .widgets import Select2MultipleWidget


FORM_CLASS = 'blueForms'


class TemplateForm(forms.ModelForm):
    template_type = forms.ModelChoiceField(queryset=Template.objects.exclude(published=None))

    class Meta:
        model = Template
        fields = ['title']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # crispy forms
        self.helper = FormHelper()
        self.helper.form_id = 'id-plan'
        self.helper.form_class = FORM_CLASS
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Next'))


class DeleteForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # crispy forms
        self.helper = FormHelper()
        self.helper.form_id = 'id-plan'
        self.helper.form_class = FORM_CLASS
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Yes'))
        self.helper.add_input(Submit('cancel', 'No'))


class NotesForm(forms.Form):
    notes = forms.CharField(
        label='More information',
        help_text='If you need to go more in depth, do so here. This will be shown in the generated text',
        required=False,
        widget=forms.Textarea
    )

    def __init__(self, *args, **kwargs):
        kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)


class AbstractNodeMixin():

    def __init__(self, **kwargs):
        self.has_prevquestion = kwargs.pop('has_prevquestion', False)
        self.question = kwargs.pop('question')
        self.question_pk = self.question.pk
        label = self.question.label
        self.label = ' '.join((label, self.question.question))
        self.help_text = getattr(self.question, 'help_text', '')
        kwargs.pop('instance', None)
        initial = self.deserialize(kwargs.get('initial', []))
        kwargs['initial'] = initial
        kwargs['prefix'] = str(self.question_pk)
        super().__init__(**kwargs)


class AbstractNodeForm(AbstractNodeMixin, forms.Form):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._add_choice_field()

    def _add_choice_field(self):
        pass

    def deserialize(self, initial):
        return initial

    def serialize(self):
        return {
            'choice': self.cleaned_data['choice'],
        }

    def pprint(self):
        if self.is_valid():
            return self.cleaned_data['choice']
        return 'Not set'


class BooleanForm(AbstractNodeForm):

    def _add_choice_field(self):
        choices = (
            (True, 'Yes'),
            (False, 'No'),
        )
        self.fields['choice'] = forms.ChoiceField(
            required=False,
            label=self.label,
            help_text=self.help_text,
            choices=choices,
            widget=forms.RadioSelect,
        )

    def pprint(self):
        if self.is_valid():
            return 'Yes' if self.cleaned_data['choice'] else 'No'
        return 'Not set'

    def serialize(self):
        out = {
            'choice': None,
        }
        if self.is_valid():
            data = self.cleaned_data['choice']
            if data == 'True':
                out['choice'] = True
            if data == 'False':
                out['choice'] = False
            return out
        return {}


class ChoiceForm(AbstractNodeForm):

    def _add_choice_field(self):
        choices = self.question.canned_answers.values_list('choice', 'canned_text')
        fixed_choices = []
        for (k, v) in choices:
            if not v:
                v = k
            fixed_choices.append((k, v))
        self.fields['choice'] = forms.ChoiceField(
            required=False,
            label=self.label,
            help_text=self.help_text,
            choices=fixed_choices,
            widget=forms.RadioSelect,
        )


class MultipleChoiceOneTextForm(AbstractNodeForm):

    def _add_choice_field(self):
        choices = self.question.canned_answers.values_list('choice', 'choice')
        self.fields['choice'] = forms.MultipleChoiceField(
            required=False,
            label=self.label,
            help_text=self.help_text,
            choices=choices,
            widget=forms.CheckboxSelectMultiple,
        )


class DateRangeForm(AbstractNodeForm):

    def deserialize(self, initial):
        choice = initial.get('choice', {})
        if choice:
            start = choice.pop('start')
            end = choice.pop('end')
            question = {}
            question['lower'] = date(*map(int, start.split('-')))
            question['upper'] = date(*map(int, end.split('-')))
            initial['choice'] = question
        return initial

    def _add_choice_field(self):
        self.fields['choice'] = DateRangeField(
            required=False,
            label=self.label,
            help_text=self.help_text,
        )

    def serialize(self):
        data = self.cleaned_data.get('choice', None)
        if self.is_bound and data is not None:
            start, end = data.lower, data.upper
            return {
                'choice':
                    {
                        'start': start.isoformat(),
                        'end': end.isoformat(),
                    },
            }
        return {}

    def pprint(self):
        if self.is_valid():
            return '{}–{}'.format(self.serialize())
        return 'Not set'


class ReasonForm(AbstractNodeForm):

    def _add_choice_field(self):
        self.fields['choice'] = forms.CharField(
            required=False,
            label=self.label,
            help_text=self.help_text,
            widget=forms.Textarea,
        )


class PositiveIntegerForm(AbstractNodeForm):

    def _add_choice_field(self):
        self.fields['choice'] = forms.IntegerField(
            required=False,
            label=self.label,
            min_value=1,
            help_text=self.help_text,
        )


class ExternalChoiceForm(AbstractNodeForm):

    def _add_choice_field(self):
        question = self.question.get_instance()
        if question.eestore.sources.exists():
            sources = question.eestore.sources.all()
        else:
            sources = question.eestore.eestore_type.sources.all()
        qs = EEStoreCache.objects.filter(source__in=sources)
        choices = qs.values_list('eestore_pid', 'name')
        self.fields['choice'] = forms.ChoiceField(
            required=False,
            label=self.label,
            help_text=self.help_text,
            choices=choices,
            widget=Select2Widget,
        )


class ExternalChoiceNotListedForm(AbstractNodeForm):

    def _add_choice_field(self):
        question = self.question.get_instance()
        if question.eestore.sources.exists():
            sources = question.eestore.sources.all()
        else:
            sources = question.eestore.eestore_type.sources.all()
        qs = EEStoreCache.objects.filter(source__in=sources)
        choices = qs.values_list('eestore_pid', 'name')
        self.fields['choice'] = ChoiceNotListedField(
            required=False,
            label=self.label,
            help_text=self.help_text,
            choices=choices,
        )


class ExternalMultipleChoiceOneTextForm(AbstractNodeForm):

    def _add_choice_field(self):
        question = self.question.get_instance()
        if question.eestore.sources.exists():
            sources = question.eestore.sources.all()
        else:
            sources = question.eestore.eestore_type.sources.all()
        qs = EEStoreCache.objects.filter(source__in=sources)
        choices = qs.values_list('eestore_pid', 'name')
        self.fields['choice'] = forms.MultipleChoiceField(
            required=False,
            label=self.label,
            help_text=self.help_text,
            choices=choices,
            widget=Select2MultipleWidget,
        )


class ExternalMultipleChoiceNotListedOneTextForm(AbstractNodeForm):

    def _add_choice_field(self):
        question = self.question.get_instance()
        if question.eestore.sources.exists():
            sources = question.eestore.sources.all()
        else:
            sources = question.eestore.eestore_type.sources.all()
        qs = EEStoreCache.objects.filter(source__in=sources)
        choices = qs.values_list('eestore_pid', 'name')
        self.fields['choice'] = MultipleChoiceNotListedField(
            required=False,
            label=self.label,
            help_text=self.help_text,
            choices=choices,
        )


class NamedURLForm(AbstractNodeForm):
    # High magic form with node-magic that cannot be used in a formset

    def _add_choice_field(self):
        self.fields['choice'] = NamedURLField(
            required=False,
            label=self.label,
            help_text=self.help_text,
        )


# Formsets


class AbstractNodeFormSet(AbstractNodeMixin, forms.BaseFormSet):

    def deserialize(self, initial):
        data = initial.get('choice', [])
        for i, item in enumerate(data):
            data[i] = {'choice': item}
        return data

    @classmethod
    def generate_choice(cls, choice):
        raise NotImplemented

    def serialize(self):
        choices = []
        for form_choice in self.cleaned_data:
            if form_choice.get('DELETE', False): continue
            choice = form_choice.get('choice', None)
            if not choice: continue
            choice_dict = self.generate_choice(choice)
            choices.append(choice_dict)
        return {
            'choice': choices,
        }


class NamedURLFormSetForm(forms.Form):
    # Low magic form to be used in a formset
    #
    # The formset has the node-magic
    choice = NamedURLField(label='') # Hide the label from crispy forms


class AbstractMultiNamedURLOneTextFormSet(AbstractNodeFormSet):

    @classmethod
    def generate_choice(cls, choice):
        return {'url': choice['url'], 'name': choice['name']}


MultiNamedURLOneTextFormSet = forms.formset_factory(
    NamedURLFormSetForm,
    formset=AbstractMultiNamedURLOneTextFormSet,
    extra=2,
    can_delete=True,
)


class DMPTypedReasonFormSetForm(forms.Form):
    # Low magic form to be used in a formset
    #
    # The formset has the node-magic
    choice = DMPTypedReasonField(label='')


class AbstractMultiDMPTypedReasonOneTextFormSet(AbstractNodeFormSet):

    @classmethod
    def generate_choice(cls, choice):
        return {
            'reason': choice['reason'],
            'type': choice['type'],
            'access_url': choice.get('access_url', ''),
        }


MultiDMPTypedReasonOneTextFormSet = forms.formset_factory(
    DMPTypedReasonFormSetForm,
    formset=AbstractMultiDMPTypedReasonOneTextFormSet,
    extra=2,
    can_delete=True,
)


INPUT_TYPE_TO_FORMS = {
    'bool': BooleanForm,
    'choice': ChoiceForm,
    'multichoiceonetext': MultipleChoiceOneTextForm,
    'daterange': DateRangeForm,
    'reason': ReasonForm,
    'positiveinteger': PositiveIntegerForm,
    'externalchoice': ExternalChoiceForm,
    'extchoicenotlisted': ExternalChoiceNotListedForm,
    'externalmultichoiceonetext': ExternalMultipleChoiceOneTextForm,
    'extmultichoicenotlistedonetext': ExternalMultipleChoiceNotListedOneTextForm,
    'namedurl': NamedURLForm,
    'multinamedurlonetext': MultiNamedURLOneTextFormSet,
    'multidmptypedreasononetext': MultiDMPTypedReasonOneTextFormSet,
}


def make_form(question, **kwargs):
    kwargs.pop('prefix', None)
    kwargs.pop('instance', None)
    kwargs['question'] = question
    form_type = INPUT_TYPE_TO_FORMS.get(question.input_type, None)
    if form_type is None:
        assert False, 'Unknown input type: {}'.format(question.input_type)
    return form_type(**kwargs)
