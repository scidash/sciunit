"""Unit tests for scores and score collections"""

import unittest

from IPython.display import display
import numpy as np

from sciunit import ScoreMatrix, ScoreArray
from sciunit.scores import ZScore, CohenDScore, PercentScore, BooleanScore,\
                           FloatScore, RatioScore
from sciunit.scores import ErrorScore, NAScore, TBDScore, NoneScore,\
                           InsufficientDataScore, RandomScore
from sciunit.tests import RangeTest, Test
from sciunit.models import Model
from sciunit.unit_test.base import SuiteBase
from sciunit.utils import NotebookTools
from pandas.core.frame import DataFrame
from pandas.core.series import Series
from sciunit.errors import InvalidScoreError
from quantities import Quantity
class ScoresTestCase(SuiteBase, unittest.TestCase, NotebookTools):
    
    path = '.'
    
    def test_score_matrix_constructor(self):
        tests = [Test([1, 2, 3])]
        models = [Model()]
        scores = np.array([ZScore(1.0)])
        scoreArray = ScoreArray(tests)
        scoreMatrix = ScoreMatrix(tests, models, scores)
        scoreMatrix = ScoreMatrix(tests, models, scores, transpose=True)

        tests = Test([1, 2, 3])
        models = Model()
        scoreMatrix = ScoreMatrix(tests, models, scores)

    def test_score_matrix(self):
        t, t1, t2, m1, m2 = self.prep_models_and_tests()
        sm = t.judge(m1)

        self.assertRaises(TypeError, sm.__getitem__, 0)
        
        self.assertEqual(str(sm.get_group((t1, m1))), "Pass")
        self.assertEqual(str(sm.get_group((m1, t1))), "Pass")
        self.assertEqual(str(sm.get_group((m1.name, t1.name))), "Pass")
        self.assertEqual(str(sm.get_group((t1.name, m1.name))), "Pass")

        self.assertRaises(TypeError, sm.get_group, (0, 0))
        self.assertRaises(KeyError, sm.get_by_name, "This name does not exist")
        
        self.assertIsInstance(sm.__getattr__("score"), DataFrame)
        self.assertIsInstance(sm.norm_scores, DataFrame)
        self.assertIsInstance(sm.T, ScoreMatrix)
        self.assertIsInstance(sm.to_html(True, True, True), str)
        self.assertIsInstance(sm.to_html(), str)

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
        self.assertIsInstance(sa.__getattr__("score"), Series)
        self.assertRaises(KeyError, sa.get_by_name, "This name does not exist")
        self.assertEqual(list(sa.norm_scores.values), [1.0, 0.0])
        self.assertEqual(sa.stature(t1), 1)
        self.assertEqual(sa.stature(t2), 2)
        self.assertEqual(sa.stature(t1), 1)
        display(sa)

    def test_regular_score_types_1(self):
        score = PercentScore(42)
        self.assertEqual(score.norm_score, 0.42)

        self.assertEqual(1, ZScore(0.0).norm_score)
        self.assertEqual(0, ZScore(1e12).norm_score)
        self.assertEqual(0, ZScore(-1e12).norm_score)

        ZScore(0.7)
        score = ZScore.compute({'mean': 3., 'std': 1.},
                               {'value': 2.})

        self.assertIsInstance(ZScore.compute({'mean': 3.}, {'value': 2.}), InsufficientDataScore)
        self.assertIsInstance(ZScore.compute({'mean': 3., 'std': -1.}, {'value': 2.}), InsufficientDataScore)
        self.assertIsInstance(ZScore.compute({'mean': np.nan, 'std': np.nan}, {'value': np.nan}), InsufficientDataScore)
        self.assertEqual(score.score, -1.)

        self.assertEqual(1, CohenDScore(0.0).norm_score)
        self.assertEqual(0, CohenDScore(1e12).norm_score)
        self.assertEqual(0, CohenDScore(-1e12).norm_score)
        CohenDScore(-0.3)
        score = CohenDScore.compute({'mean': 3., 'std': 1.},
                                    {'mean': 2., 'std': 1.})

        self.assertAlmostEqual(-0.707, score.score, 3)
        self.assertEqual('D = -0.71', str(score))

        score = CohenDScore.compute({'mean': 3.0, 'std': 10.0, 'n' : 10},
                                    {'mean': 2.5, 'std': 10.0, 'n' : 10})
        self.assertAlmostEqual(-0.05, score.score, 2)

    def test_regular_score_types_2(self):
        BooleanScore(True)
        BooleanScore(False)
        score = BooleanScore.compute(5, 5)
        self.assertEqual(score.norm_score, 1)
        score = BooleanScore.compute(4, 5)
        self.assertEqual(score.norm_score, 0)

        self.assertEqual(1, BooleanScore(True).norm_score)
        self.assertEqual(0, BooleanScore(False).norm_score)

        t = RangeTest([2, 3])
        score.test = t
        score.describe()
        score.description = "Lorem Ipsum"
        score.describe()

        score = FloatScore(3.14)
        self.assertRaises(InvalidScoreError, score.check_score, Quantity([1,2,3], 'J'))

        obs = np.array([1.0, 2.0, 3.0])
        pred = np.array([1.0, 2.0, 4.0])
        score = FloatScore.compute_ssd(obs, pred)
        self.assertEqual(str(score), '1')
        self.assertEqual(score.score, 1.0)

        score = RatioScore(1.2)
        self.assertEqual(1, RatioScore(1.0).norm_score)
        self.assertEqual(0, RatioScore(1e12).norm_score)
        self.assertEqual(0, RatioScore(1e-12).norm_score)

        self.assertEqual(str(score), 'Ratio = 1.20')

        self.assertRaises(InvalidScoreError, RatioScore, -1.0)
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

    def test_only_lower_triangle(self):
        """Test validation of observations against the `observation_schema`."""
        self.do_notebook('test_only_lower_triangle')

    def test_RandomScore(self):
        """Note: RandomScore is only used for debugging purposes"""
        score = RandomScore(0.5)
        self.assertEqual('0.5', str(score))


if __name__ == '__main__':
    unittest.main()