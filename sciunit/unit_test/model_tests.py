"""Unit tests for models and capabilities"""

import unittest

class ModelsTestCase(unittest.TestCase):
    """Unit tests for the sciunit module"""

    def setUp(self):
        from sciunit.models.examples import UniformModel
        self.M = UniformModel

    def test_get_model_state(self):
        from sciunit import Model

        m = Model()
        state = m.__getstate__()
        self.assertEqual(m.__dict__, state)

    def test_get_model_capabilities(self):
        from sciunit.capabilities import ProducesNumber

        m = self.M(2, 3)
        self.assertEqual(m.capabilities, [ProducesNumber])

    def test_get_model_description(self):
        m = self.M(2, 3)
        m.describe()
        m.description = "Lorem Ipsum"
        m.describe()

    def test_check_model_capabilities(self):
        from sciunit.tests import RangeTest
        t = RangeTest([2,3])
        m = self.M(2,3)
        t.check(m)

    def test_regular_models(self):
        from sciunit.models.examples\
            import ConstModel, UniformModel, SharedModel

        m = ConstModel(3)
        self.assertEqual(m.produce_number(),3)

        m = UniformModel(3,4)
        self.assertTrue(3 < m.produce_number() < 4)

    def test_irregular_models(self):
        from sciunit.models.examples\
            import CacheByInstancePersistentUniformModel,\
            CacheByValuePersistentUniformModel

        a = CacheByInstancePersistentUniformModel(2,3)
        a1 = a.produce_number()
        a2 = a.produce_number()
        self.assertEqual(a1,a2)
        b = CacheByInstancePersistentUniformModel(2,3)
        b1 = b.produce_number()
        self.assertNotEqual(b1,a2)

        c = CacheByValuePersistentUniformModel(2,3)
        c1 = c.produce_number()
        c2 = c.produce_number()
        self.assertEqual(c1,c2)
        d = CacheByValuePersistentUniformModel(2,3)
        d1 = d.produce_number()
        self.assertEqual(d1,c2)


class CapabilitiesTestCase(unittest.TestCase):
    """Unit tests for sciunit Capability classes"""

    def test_capabilities(self):
        from sciunit import Model
        from sciunit.capabilities import ProducesNumber
        from sciunit.models import Model
        from sciunit.models.examples import UniqueRandomNumberModel,\
            RepeatedRandomNumberModel

        class MyModel(Model,ProducesNumber):
            def produce_number(self):
                return 3.14
        m = MyModel()
        self.assertEqual(m.produce_number(),3.14)

        m = UniqueRandomNumberModel()
        self.assertNotEqual(m.produce_number(),m.produce_number())

        m = RepeatedRandomNumberModel()
        self.assertEqual(m.produce_number(),m.produce_number())
