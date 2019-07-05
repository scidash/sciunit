"""Unit tests for scores and score collections"""

import unittest

from IPython.display import display
import numpy as np

from sciunit import ScoreMatrix, ScoreArray, ScorePanel
from sciunit.scores import ZScore, CohenDScore, PercentScore, BooleanScore,\
                           FloatScore, RatioScore
from sciunit.scores import ErrorScore, NAScore, TBDScore, NoneScore,\
                           InsufficientDataScore
from sciunit.tests import RangeTest

from sciunit.unit_test.base import SuiteBase


class ScoresTestCase(SuiteBase, unittest.TestCase):
    def test_score_matrix(self):
        t, t1, t2, m1, m2 = self.prep_models_and_tests()
        sm = t.judge(m1)
        self.assertTrue(type(sm) is ScoreMatrix)
        self.assertTrue(sm[t1][m1].score)
        self.assertTrue(sm['test1'][m1].score)
        self.assertTrue(sm[m1]['test1'].score)
        self.assertFalse(sm[t2][m1].score)
        self.assertEqual(sm[(m1, t1)].score, True)
        self.assertEqual(sm[(m1, t2)].score, False)
        sm = t.judge([m1, m2])
        self.assertEqual(sm.stature(t1, m1), 1)
        self.assertEqual(sm.stature(t1, m2), 2)
        display(sm)

    def test_score_arrays(self):
        t, t1, t2, m1, m2 = self.prep_models_and_tests()
        sm = t.judge(m1)
        sa = sm[m1]
        self.assertTrue(type(sa) is ScoreArray)
        self.assertEqual(list(sa.norm_scores.values), [1.0, 0.0])
        self.assertEqual(sa.stature(t1), 1)
        self.assertEqual(sa.stature(t2), 2)
        self.assertEqual(sa.stature(t1), 1)
        display(sa)

    @unittest.skip(("Currently failing because ScorePanel "
                    "just stores sm1 twice"))
    def test_score_panel(self):
        t, t1, t2, m1, m2 = self.prep_models_and_tests()
        sm1 = t.judge([m1, m2])
        sm2 = t.judge([m2, m1])
        sp = ScorePanel(data={1: sm1, 2: sm2})
        self.assertTrue(sp[1].equals(sm1))
        self.assertTrue(sp[2].equals(sm2))

    def test_regular_score_types_1(self):
        score = PercentScore(42)
        self.assertEqual(score.norm_score, 0.42)

        ZScore(0.7)
        score = ZScore.compute({'mean': 3., 'std': 1.},
                               {'value': 2.})
        self.assertEqual(score.score, -1.)

        CohenDScore(-0.3)
        score = CohenDScore.compute({'mean': 3., 'std': 1.},
                                    {'mean': 2., 'std': 1.})
        self.assertTrue(-0.708 < score.score < -0.707)

    def test_regular_score_types_2(self):
        BooleanScore(True)
        BooleanScore(False)
        score = BooleanScore.compute(5, 5)
        self.assertEqual(score.norm_score, 1)
        score = BooleanScore.compute(4, 5)
        self.assertEqual(score.norm_score, 0)

        t = RangeTest([2, 3])
        score.test = t
        score.describe()
        score.description = "Lorem Ipsum"
        score.describe()

        score = FloatScore(3.14)
        obs = np.array([1.0, 2.0, 3.0])
        pred = np.array([1.0, 2.0, 4.0])
        score = FloatScore.compute_ssd(obs, pred)
        self.assertEqual(score.score, 1.0)

        RatioScore(1.2)
        score = RatioScore.compute({'mean': 4., 'std': 1.}, {'value': 2.})
        self.assertEqual(score.score, 0.5)

    def test_irregular_score_types(self):
        e = Exception("This is an error")
        score = ErrorScore(e)
        score = NAScore(None)
        score = TBDScore(None)
        score = NoneScore(None)
        score = InsufficientDataScore(None)
        self.assertEqual(score.norm_score, None)
