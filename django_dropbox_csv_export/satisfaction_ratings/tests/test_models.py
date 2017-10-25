from django.test import TestCase

from ..models import SatisfactionRating


class SatisfactionRatingTest(TestCase):
    def test_save_satisfaction_rating(self):
        satisfaction_rating = SatisfactionRating()
        satisfaction_rating.customer_name = 'Pronto'
        satisfaction_rating.score = 9
        satisfaction_rating.save()

        satisfaction_rating = SatisfactionRating.objects.last()

        self.assertEqual(satisfaction_rating.customer_name, 'Pronto')
        self.assertEqual(satisfaction_rating.score, 9)
