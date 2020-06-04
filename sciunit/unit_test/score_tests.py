"""Unit tests for scores and score collections"""

import unittest

from IPython.display import display
import numpy as np

from sciunit import ScoreMatrix, ScoreArray, Score
from sciunit.scores import (
    ZScore,
    CohenDScore,
    PercentScore,
    BooleanScore,
    FloatScore,
    RatioScore,
)
from sciunit.scores import (
    ErrorScore,
    NAScore,
    TBDScore,
    NoneScore,
    InsufficientDataScore,
    RandomScore,
)
from sciunit.scores.collections_m2m import ScoreArrayM2M, ScoreMatrixM2M
from sciunit.tests import RangeTest, Test
from sciunit.models import Model
from sciunit.unit_test.base import SuiteBase
from sciunit.utils import NotebookTools
from pandas.core.frame import DataFrame
from pandas.core.series import Series
from sciunit.errors import InvalidScoreError
from quantities import Quantity
from pandas import DataFrame


class ScoresTestCase(SuiteBase, unittest.TestCase, NotebookTools):

    path = "."

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
        self.assertTrue(sm["test1"][m1].score)
        self.assertTrue(sm[m1]["test1"].score)
        self.assertFalse(sm[t2][m1].score)
        self.assertEqual(sm[(m1, t1)].score, True)
        self.assertEqual(sm[(m1, t2)].score, False)
        sm = t.judge([m1, m2])
        self.assertEqual(sm.stature(t1, m1), 1)
        self.assertEqual(sm.stature(t1, m2), 2)
        display(sm)

        ######### m2m #################
        t1.observation = [2, 3]
        smm2m = ScoreMatrixM2M(
            test=t1, models=[m1], scores=[[Score(1), Score(1)], [Score(1), Score(1)]]
        )

        self.assertIsInstance(smm2m.__getattr__("score"), DataFrame)
        self.assertIsInstance(smm2m.__getattr__("norm_scores"), DataFrame)
        self.assertIsInstance(smm2m.__getattr__("related_data"), DataFrame)
        self.assertRaises(KeyError, smm2m.get_by_name, "Not Exist")
        self.assertIsInstance(smm2m.norm_scores, DataFrame)
        self.assertRaises(KeyError, smm2m.get_by_name, "Not Exist")
        self.assertRaises(TypeError, smm2m.get_group, [0])
        self.assertIsInstance(smm2m.get_group([m1.name, t1.name]), Score)
        self.assertEqual(smm2m.get_group([m1.name, t1.name]).score, 1)
        self.assertIsInstance(smm2m.get_group([m1, t1]), Score)
        self.assertEqual(smm2m.get_group([m1, t1]).score, 1)

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

        ######### m2m #################
        sam2m = ScoreArrayM2M(
            test=t1, models=[m1], scores=[[Score(1), Score(1)], [Score(1), Score(1)]]
        )
        self.assertRaises(KeyError, sam2m.get_by_name, "Not Exist")

    def test_regular_score_types_1(self):
        self.assertEqual(PercentScore(0).norm_score, 0)
        self.assertEqual(PercentScore(100).norm_score, 1)

        score = PercentScore(42)
        self.assertRaises(InvalidScoreError, PercentScore, 101)
        self.assertRaises(InvalidScoreError, PercentScore, -1)
        self.assertEqual(str(score), "42.0%")
        self.assertEqual(score.norm_score, 0.42)

        self.assertEqual(1, ZScore(0.0).norm_score)
        self.assertEqual(0, ZScore(1e12).norm_score)
        self.assertEqual(0, ZScore(-1e12).norm_score)

        ZScore(0.7)
        score = ZScore.compute({"mean": 3.0, "std": 1.0}, {"value": 2.0})

        self.assertIsInstance(
            ZScore.compute({"mean": 3.0}, {"value": 2.0}), InsufficientDataScore
        )
        self.assertIsInstance(
            ZScore.compute({"mean": 3.0, "std": -1.0}, {"value": 2.0}),
            InsufficientDataScore,
        )
        self.assertIsInstance(
            ZScore.compute({"mean": np.nan, "std": np.nan}, {"value": np.nan}),
            InsufficientDataScore,
        )
        self.assertEqual(score.score, -1.0)

        self.assertEqual(1, CohenDScore(0.0).norm_score)
        self.assertEqual(0, CohenDScore(1e12).norm_score)
        self.assertEqual(0, CohenDScore(-1e12).norm_score)
        CohenDScore(-0.3)
        score = CohenDScore.compute(
            {"mean": 3.0, "std": 1.0}, {"mean": 2.0, "std": 1.0}
        )

        self.assertAlmostEqual(-0.707, score.score, 3)
        self.assertEqual("D = -0.71", str(score))

        score = CohenDScore.compute(
            {"mean": 3.0, "std": 10.0, "n": 10}, {"mean": 2.5, "std": 10.0, "n": 10}
        )
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
        self.assertRaises(
            InvalidScoreError, score.check_score, Quantity([1, 2, 3], "J")
        )

        obs = np.array([1.0, 2.0, 3.0])
        pred = np.array([1.0, 2.0, 4.0])
        score = FloatScore.compute_ssd(obs, pred)
        self.assertEqual(str(score), "1")
        self.assertEqual(score.score, 1.0)

        score = RatioScore(1.2)
        self.assertEqual(1, RatioScore(1.0).norm_score)
        self.assertEqual(0, RatioScore(1e12).norm_score)
        self.assertEqual(0, RatioScore(1e-12).norm_score)

        self.assertEqual(str(score), "Ratio = 1.20")

        self.assertRaises(InvalidScoreError, RatioScore, -1.0)
        score = RatioScore.compute({"mean": 4.0, "std": 1.0}, {"value": 2.0})

        self.assertEqual(score.score, 0.5)

    def test_irregular_score_types(self):
        e = Exception("This is an error")
        score = ErrorScore(e)
        score = NAScore(None)
        score = TBDScore(None)
        score = NoneScore(None)
        score = NoneScore("this is a string")
        self.assertIsInstance(str(score), str)
        self.assertRaises(InvalidScoreError, NoneScore, ["this is a string list"])

        score = InsufficientDataScore(None)
        self.assertEqual(score.norm_score, None)

    def test_only_lower_triangle(self):
        """Test validation of observations against the `observation_schema`."""
        self.do_notebook("test_only_lower_triangle")

    def test_RandomScore(self):
        """Note: RandomScore is only used for debugging purposes"""
        score = RandomScore(0.5)
        self.assertEqual("0.5", str(score))

    def test_Score(self):
        self.assertIsInstance(Score.compute({}, {}), NotImplementedError)
        score = Score(0.5)
        self.assertEqual(score.norm_score, 0.5)
        self.assertAlmostEqual(score.log_norm_score, -0.693, 2)
        self.assertAlmostEqual(score.log2_norm_score, -1.0, 1)
        self.assertAlmostEqual(score.log10_norm_score, -0.301, 1)
        self.assertIsInstance(score.raw, str)
        score._raw = "this is a string"
        self.assertIsNone(score.raw)
        self.assertIsInstance(score.__repr__(), str)
        self.assertIsInstance(score.__str__(), str)

        self.assertFalse(score.__ne__(score))
        self.assertTrue(score.__ne__(Score(998.0)))
        self.assertFalse(score.__ne__(0.5))
        self.assertTrue(score.__ne__(0.6))

        self.assertFalse(score.__gt__(score))
        self.assertTrue(score.__gt__(Score(0.2)))
        self.assertFalse(score.__gt__(0.5))
        self.assertTrue(score.__gt__(0.2))

        self.assertFalse(score.__lt__(score))
        self.assertTrue(score.__lt__(Score(0.9)))
        self.assertFalse(score.__lt__(0.5))
        self.assertTrue(score.__lt__(0.9))

        self.assertTrue(score.__le__(score))
        self.assertTrue(score.__le__(Score(0.5)))
        self.assertTrue(score.__le__(0.5))
        self.assertTrue(score.__le__(0.5))
        self.assertFalse(score.__le__(0.1))
        self.assertFalse(score.__le__(Score(0.1)))

        self.assertIsInstance(score.score_type, str)

    def test_ErrorScore(self):
        score = ErrorScore(0.5)
        self.assertEqual(0.0, score.norm_score)
        self.assertIsInstance(score.summary, str)
        self.assertIsInstance(score._describe(), str)
        self.assertIsInstance(str(score), str)


if __name__ == "__main__":
    unittest.main()
