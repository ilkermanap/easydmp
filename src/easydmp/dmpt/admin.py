# -*- coding: utf-8 -*-
from django.contrib import admin

from guardian.admin import GuardedModelAdmin
from guardian.shortcuts import assign_perm
from guardian.shortcuts import get_objects_for_user

from easydmp.eestore.models import EEStoreMount
from easydmp.utils.admin import ObjectPermissionModelAdmin
from easydmp.utils.admin import SetPermissionsMixin
from easydmp.utils import get_model_name

from .models import Template
from .models import Section
from .models import Question
from .models import CannedAnswer

"""
The admin is simplified for non-superusers. Branching sections are disallowed,
hence all questions are obligatory.
"""


def get_templates_for_user(user):
    templates = get_objects_for_user(
        user,
        'dmpt.change_template',
        accept_global_perms=False,
    )
    return templates


def get_sections_for_user(user):
    templates = get_templates_for_user(user)
    return Section.objects.filter(template__in=templates)


def get_questions_for_user(user):
    sections = get_sections_for_user(user)
    return Question.objects.filter(section__in=sections)


def get_canned_answers_for_user(user):
    questions = get_questions_for_user(user)
    return CannedAnswer.objects.filter(question__in=questions)


@admin.register(Template)
class TemplateAdmin(SetPermissionsMixin, ObjectPermissionModelAdmin):
    list_display = ('id', 'title')
    list_display_links = ('title', 'id')
    set_permissions = ['use_template']
    has_object_permissions = True


@admin.register(Section)
class SectionAdmin(ObjectPermissionModelAdmin):
    list_display = (
        'template',
        'position',
        'section_depth',
        'id',
        'label',
        'title',
    )
    list_display_links = ('template', 'section_depth', 'id', 'position')
    list_filter = ('template',)
    actions = [
        'increment_position',
        'decrement_position',
    ]
    _model_slug = 'section'

    def get_limited_queryset(self, request):
        return get_sections_for_user(request.user)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'template' and not request.user.is_superuser:
            templates = get_templates_for_user(request.user)
            kwargs["queryset"] = templates
        if db_field.name == 'super_section':
            kwargs["queryset"] = self.get_queryset(request)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # actions

    def increment_position(self, request, queryset):
        for q in queryset.order_by('-position'):
            q.position += 1
            q.save()
    increment_position.short_description = 'Increment position by 1'

    def decrement_position(self, request, queryset):
        for q in queryset.order_by('position'):
            q.position -= 1
            q.save()
    decrement_position.short_description = 'Decrement position by 1'


@admin.register(CannedAnswer)
class CannedAnswerAdmin(ObjectPermissionModelAdmin):
    list_display = (
        'question',
        'choice',
        'position',
        'id',
        'has_edge',
    )
    list_display_links = ('id', 'question')
    actions = [
        'create_edge',
        'update_edge',
    ]
    list_filter = ('question',)
    _model_slug = 'canned_answer'

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ()
        return ('edge',)

    def get_limited_queryset(self, request):
        return get_canned_answers_for_user(request.user)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'question' and not request.user.is_superuser:
            question = get_questions_for_user(request.user)
            kwargs["queryset"] = question
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # actions

    def create_edge(self, request, queryset):
        for q in queryset.all():
            if not q.edge:
                q.create_edge()
    create_edge.short_description = 'Create edge'

    def update_edge(self, request, queryset):
        for q in queryset.all():
            if q.edge:
                q.update_edge()
            else:
                q.create_edge()
    update_edge.short_description = 'Update edge'

    # display fields

    def has_edge(self, obj):
        return True if obj.edge else False
    has_edge.short_description = 'Edge'
    has_edge.boolean = True


class CannedAnswerInline(admin.StackedInline):
    model = CannedAnswer

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ()
        return ('edge',)


class EEStoreMountInline(admin.StackedInline):
    model = EEStoreMount


class EEStoreTypeFilter(admin.SimpleListFilter):
    title = 'EEStore type'
    parameter_name = 'eestore'

    def lookups(self, request, model_admin):
        types = EEStoreMount.objects.values_list('eestore_type__name', flat=True).distinct()
        return tuple(zip(*(types, types)))

    def queryset(self, request, queryset):
        if self.value():
            queryset = queryset.filter(eestore__eestore_type__name=self.value())
        return queryset


class SectionFilter(admin.SimpleListFilter):
    title = 'Section'
    parameter_name = 'section'

    def lookups(self, request, model_admin):
        sections = Section.objects.all()
        template_id = request.GET.get('section__template__id__exact', None)
        if template_id:
            sections = sections.filter(template_id=template_id)
        lookups = []
        for section in sections:
            lookups.append((section.pk, str(section)))
        return lookups

    def queryset(self, request, queryset):
        if self.value():
            queryset = queryset.filter(section__id=self.value())
        return queryset


@admin.register(Question)
class QuestionAdmin(ObjectPermissionModelAdmin):
    list_display = (
        'position',
        'id',
        'label',
        'question',
        'section',
        'input_type',
        'obligatory',
        'has_node',
        'get_mount',
    )
    list_display_links = ('position', 'id', 'question')
    actions = [
        'create_node',
        'toggle_obligatory',
        'increment_position',
        'decrement_position',
    ]
    list_filter = [
        'obligatory',
        'section__template',
        SectionFilter,
        EEStoreTypeFilter,
    ]
    inlines = [
        CannedAnswerInline,
        EEStoreMountInline,
    ]
    save_on_top = True
    _model_slug = 'question'

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ()
        return ('node', 'obligatory')

    def get_queryset(self, request):
        return get_questions_for_user(request.user)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'section' and not request.user.is_superuser:
            sections = get_sections_for_user(request.user)
            kwargs["queryset"] = sections
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # display fields

    def has_node(self, obj):
        return True if obj.node else False
    has_node.short_description = 'Node'
    has_node.boolean = True

    def get_mount(self, obj):
        return obj.eestore.eestore_type if obj.eestore else ''
    get_mount.short_description = 'EEStore'
    get_mount.admin_order_field = 'eestore'

    # actions

    def create_node(self, request, queryset):
        for q in queryset.all():
            if not q.node:
                q.create_node()
    create_node.short_description = 'Create node'

    def toggle_obligatory(self, request, queryset):
        for q in queryset.all():
            q.obligatory = not q.obligatory
            q.save()
    toggle_obligatory.short_description = 'Toggle obligatoriness'

    def increment_position(self, request, queryset):
        for q in queryset.order_by('-position'):
            q.position += 1
            q.save()
    increment_position.short_description = 'Increment position by 1'

    def decrement_position(self, request, queryset):
        for q in queryset.order_by('position'):
            q.position -= 1
            q.save()
    decrement_position.short_description = 'Decrement position by 1'
