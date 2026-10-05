from django.test import TestCase

from questions.models import AnswerOption, Category, ChoiceQuestion, NumericQuestion


class QuestionBankFixtureTests(TestCase):
    fixtures = ["questions/question_bank.json"]

    def test_fixture_counts(self):
        self.assertEqual(Category.objects.count(), 6)
        self.assertEqual(ChoiceQuestion.objects.count(), 12)
        self.assertEqual(AnswerOption.objects.count(), 48)
        self.assertEqual(NumericQuestion.objects.count(), 12)

    def test_every_choice_question_has_four_options(self):
        for question in ChoiceQuestion.objects.all():
            self.assertEqual(question.answeroption_set.count(), 4, question.text)

    def test_every_choice_question_has_one_correct_option(self):
        for question in ChoiceQuestion.objects.all():
            correct = question.answeroption_set.filter(is_correct=True).count()
            self.assertEqual(correct, 1, question.text)
            question.validate_answer_options()

    def test_every_numeric_question_has_integer_answer(self):
        for question in NumericQuestion.objects.all():
            self.assertIsInstance(question.correct_answer, int, question.text)
            question.full_clean()
