from django.contrib import admin
from django.forms.models import BaseInlineFormSet

from .models import AnswerOption, Category, ChoiceQuestion, NumericQuestion


class AnswerOptionInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return

        options = []
        for form in self.forms:
            if not form.cleaned_data or self._should_delete_form(form):
                continue
            options.append(form.instance)

        self.instance.validate_answer_options(options)


class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption
    formset = AnswerOptionInlineFormSet
    extra = 4


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(ChoiceQuestion)
class ChoiceQuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "category")
    list_filter = ("category",)
    search_fields = ("text",)
    inlines = [AnswerOptionInline]


@admin.register(NumericQuestion)
class NumericQuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "category", "correct_answer")
    list_filter = ("category",)
    search_fields = ("text",)
