from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import TestCase

from questions.models import AnswerOption, Category, ChoiceQuestion, NumericQuestion


def add_options(question, correct_flags):
    for index, is_correct in enumerate(correct_flags):
        AnswerOption.objects.create(
            question=question,
            text=f"Option {index + 1}",
            is_correct=is_correct,
        )


class CategoryTests(TestCase):
    def test_create_category_with_valid_name(self):
        category = Category.objects.create(name="История")

        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(category.name, "История")
        self.assertEqual(str(category), "История")

    def test_category_name_is_unique(self):
        Category.objects.create(name="История")

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Category.objects.create(name="История")

    def test_duplicate_category_name_fails_validation(self):
        Category.objects.create(name="История")

        with self.assertRaises(ValidationError):
            Category(name="История").full_clean()

    def test_category_with_choice_question_cannot_be_deleted(self):
        category = Category.objects.create(name="История")
        ChoiceQuestion.objects.create(category=category, text="Въпрос?")

        with self.assertRaises(ProtectedError):
            category.delete()
        self.assertTrue(Category.objects.filter(pk=category.pk).exists())

    def test_category_with_numeric_question_cannot_be_deleted(self):
        category = Category.objects.create(name="История")
        NumericQuestion.objects.create(category=category, text="Въпрос?", correct_answer=1)

        with self.assertRaises(ProtectedError):
            category.delete()
        self.assertTrue(Category.objects.filter(pk=category.pk).exists())


class ChoiceQuestionTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="География")
        self.question = ChoiceQuestion.objects.create(
            category=self.category,
            text="Коя е столицата на България?",
        )

    def test_create_valid_choice_question(self):
        add_options(self.question, [True, False, False, False])

        self.question.validate_answer_options()
        self.assertEqual(self.question.category, self.category)
        self.assertEqual(self.question.text, "Коя е столицата на България?")
        self.assertEqual(self.question.answeroption_set.count(), 4)
        self.assertEqual(self.question.answeroption_set.filter(is_correct=True).count(), 1)
        self.assertIn(self.question, self.category.choicequestions.all())

    def test_fewer_than_four_options_is_invalid(self):
        add_options(self.question, [True, False, False])

        with self.assertRaises(ValidationError):
            self.question.validate_answer_options()

    def test_more_than_four_options_is_invalid(self):
        add_options(self.question, [True, False, False, False, False])

        with self.assertRaises(ValidationError):
            self.question.validate_answer_options()

    def test_no_correct_option_is_invalid(self):
        add_options(self.question, [False, False, False, False])

        with self.assertRaises(ValidationError):
            self.question.validate_answer_options()

    def test_more_than_one_correct_option_is_invalid(self):
        add_options(self.question, [True, True, False, False])

        with self.assertRaises(ValidationError):
            self.question.validate_answer_options()

    def test_deleting_question_deletes_answer_options(self):
        add_options(self.question, [True, False, False, False])

        self.question.delete()

        self.assertEqual(AnswerOption.objects.count(), 0)


class AnswerOptionTests(TestCase):
    def test_is_correct_defaults_to_false(self):
        category = Category.objects.create(name="Наука")
        question = ChoiceQuestion.objects.create(category=category, text="Въпрос?")
        option = AnswerOption.objects.create(question=question, text="Отговор")

        self.assertFalse(option.is_correct)
        self.assertEqual(option.question, question)


class NumericQuestionTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="История")

    def test_create_numeric_question(self):
        question = NumericQuestion.objects.create(
            category=self.category,
            text="През коя година е Освобождението на България?",
            correct_answer=1878,
        )

        self.assertEqual(question.category, self.category)
        self.assertEqual(question.correct_answer, 1878)
        self.assertIn(question, self.category.numericquestions.all())

    def test_correct_answer_is_required(self):
        question = NumericQuestion(category=self.category, text="Въпрос?")

        with self.assertRaises(ValidationError):
            question.full_clean()

    def test_correct_answer_must_be_integer(self):
        question = NumericQuestion(category=self.category, text="Въпрос?", correct_answer="abc")

        with self.assertRaises(ValidationError):
            question.full_clean()
