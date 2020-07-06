"""Unit tests for models and capabilities"""

import unittest


class ModelsTestCase(unittest.TestCase):
    """Unit tests for the sciunit module"""

    def setUp(self):
        from sciunit.models.examples import UniformModel

        self.M = UniformModel

    def test_is_match(self):
        from sciunit import Model

        m = Model()
        m2 = Model()
        self.assertFalse(m.is_match(m2))
        self.assertTrue(m.is_match(m))
        self.assertTrue(m.is_match("Model"))

    def test_getattr(self):
        from sciunit import Model

        m = Model()
        self.assertEqual(m.name, m.__getattr__("name"))

    def test_curr_method(self):
        from sciunit import Model

        class TestModel(Model):
            def test_calling_curr_method(self):
                return self.curr_method()

        m = TestModel()
        test_method_name = m.test_calling_curr_method()
        self.assertEqual(test_method_name, "test_calling_curr_method")

    def test_failed_extra_capabilities(self):
        from sciunit import Model

        class TestModel(Model):
            def test_return_none_function(self):
                return None

        m = TestModel()
        m.extra_capability_checks = {TestModel: "test_return_none_function"}
        test_list = m.failed_extra_capabilities

        self.assertEqual(test_list[0], TestModel)
        self.assertEqual(len(test_list), 1)

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

        t = RangeTest([2, 3])
        m = self.M(2, 3)
        t.check(m)

    def test_check_missing_capabilities_1(self):
        from sciunit.capabilities import Runnable
        from sciunit.errors import CapabilityNotImplementedError

        m = self.M(
            2, 3, name="Not actually runnable due to lack of capability provision"
        )
        try:
            m.run()
        except AttributeError as e:
            pass
        else:
            self.fail("Unprovided capability was called and not caught")

    def test_check_missing_capabilities_2(self):
        from sciunit.capabilities import Runnable
        from sciunit.errors import CapabilityNotImplementedError

        class MyModel(self.M, Runnable):
            pass

        m = MyModel(
            2, 3, name="Not actually runnable due to lack of capability implementation"
        )
        try:
            m.run()
        except CapabilityNotImplementedError as e:
            pass
        else:
            self.fail("Unimplemented capability was called and not caught")

    def test_check_missing_capabilities_3(self):
        from sciunit.capabilities import Runnable
        from sciunit.errors import CapabilityNotImplementedError

        class MyModel(self.M, Runnable):
            def run(self):
                print("Actually running!")

        m = MyModel(2, 3, name="Now actually runnable")
        m.run()

    def test_regular_models(self):
        from sciunit.models.examples import (
            ConstModel,
            UniformModel,
            SharedModel,
            PersistentUniformModel,
        )

        m = ConstModel(3)
        self.assertEqual(m.produce_number(), 3)

        m = UniformModel(3, 4)
        self.assertTrue(3 < m.produce_number() < 4)

        m = PersistentUniformModel(3, 4)
        m.run()
        self.assertTrue(3 < m.produce_number() < 4)

    def test_irregular_models(self):
        from sciunit.models.examples import (
            CacheByInstancePersistentUniformModel,
            CacheByValuePersistentUniformModel,
        )

        a = CacheByInstancePersistentUniformModel(2, 3)
        a1 = a.produce_number()
        a2 = a.produce_number()
        self.assertEqual(a1, a2)
        b = CacheByInstancePersistentUniformModel(2, 3)
        b1 = b.produce_number()
        self.assertNotEqual(b1, a2)

        c = CacheByValuePersistentUniformModel(2, 3)
        c1 = c.produce_number()
        c2 = c.produce_number()
        self.assertEqual(c1, c2)
        d = CacheByValuePersistentUniformModel(2, 3)
        d1 = d.produce_number()
        self.assertEqual(d1, c2)


class CapabilitiesTestCase(unittest.TestCase):
    """Unit tests for sciunit Capability classes"""

    def test_capabilities(self):
        from sciunit.errors import CapabilityNotImplementedError
        from sciunit import Model
        from sciunit.capabilities import (
            ProducesNumber,
            Capability,
            ProducesNumber,
            Runnable,
        )
        from sciunit.models import Model
        from sciunit.models.examples import (
            UniqueRandomNumberModel,
            RepeatedRandomNumberModel,
        )

        class MyModel(Model, ProducesNumber):
            def produce_number(self):
                return 3.14

        m = MyModel()
        self.assertEqual(m.produce_number(), 3.14)

        m = UniqueRandomNumberModel()
        self.assertNotEqual(m.produce_number(), m.produce_number())

        m = RepeatedRandomNumberModel()
        self.assertEqual(m.produce_number(), m.produce_number())

        m = Runnable()
        self.assertRaises(BaseException, m.run)
        self.assertRaises(BaseException, m.set_run_params)
        self.assertRaises(BaseException, m.set_default_run_params)

        m = ProducesNumber()
        self.assertRaises(BaseException, m.produce_number)

        m = Capability()
        m.name = "test name"
        self.assertEqual(str(m), "test name")
    
    def test_source_check(self):
        
        from sciunit.errors import CapabilityNotImplementedError
        from sciunit import Model
        from sciunit.capabilities import Capability
        from sciunit.models import Model

        class MyCap1(Capability):
            def fn1(self):
                raise NotImplementedError("fn1 not implemented.")
        
        class MyCap2(Capability):
            def fn1(self):
                self.unimplemented("fn1 not implemented.")
        
        class MyCap3(Capability):
            def fn1(self):
                raise CapabilityNotImplementedError(model = self, capability = self.__class__, details = "fn1 not implemented.")


        class MyModel1(Model, MyCap1):
            def fn1(self):
                return "fn1 have been implemented"

        class MyModel2(Model, MyCap1):
            pass

        class MyModel3(Model, MyCap2):
            def fn1(self):
                return "fn1 have been implemented"

        class MyModel4(Model, MyCap2):
            pass

        class MyModel5(Model, MyCap3):
            def fn1(self):
                return "fn1 have been implemented"

        class MyModel6(Model, MyCap3):
            pass
        
        self.assertTrue(MyCap1.source_check(MyModel1()))
        self.assertFalse(MyCap1.source_check(MyModel2()))
        self.assertTrue(MyCap2.source_check(MyModel3()))
        self.assertFalse(MyCap2.source_check(MyModel4()))
        self.assertTrue(MyCap3.source_check(MyModel5()))
        self.assertFalse(MyCap3.source_check(MyModel6()))



class RunnableModelTestCase(unittest.TestCase):
    def test_backend(self):
        from sciunit.models import RunnableModel
        from sciunit.models.backends import Backend, register_backends, available_backends

        self.assertRaises(TypeError, RunnableModel, name="", attrs=1)
        model = RunnableModel(name="test name")
        self.assertIsInstance(model.get_backend(), Backend)
        self.assertRaises(TypeError, model.set_backend, 0)

        model.set_backend(None)
        self.assertRaises(Exception, model.set_backend, "invalid backend")

        model.set_attrs(test_attr="test attribute")
        model.set_run_params(test_run_params="test runtime parameter")
        model.check_run_params()
        model.reset_run_params()
        model.set_default_run_params(test_run_params="test runtime parameter")
        model.reset_default_run_params()
        self.assertIsInstance(model.state, dict)

        class MyBackend1(Backend):

            def _backend_run(self) -> str:
                return "test result 1"

        class MyBackend2(Backend):

            def _backend_run(self) -> str:
                return "test result 2"

        name_backend_dict = {"backend1" : MyBackend2, "backend2" : MyBackend2}
        backend_names = ["backend1", "backend2"]

        model = RunnableModel(name="test name")
        register_backends(name_backend_dict)
        model.set_backend(backend_names)
        model.print_run_params = True
        model.run()
        
        model = RunnableModel(name="test name")
        model.default_run_params = {"para1" : 1}
        model.use_default_run_params()


if __name__ == "__main__":
    unittest.main()
