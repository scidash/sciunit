import unittest
import quantities as pq


class ValidatorTestCase(unittest.TestCase):

    def test_register(self):

        class TestClass():
            intValue = 0

            def getIntValue(self):
                return self.intValue

        from sciunit.validators import register_quantity, register_type
        from cerberus import TypeDefinition, Validator

        register_type(TestClass, "TestType1")
        q = pq.Quantity([1, 2, 3], 'J')
        register_quantity(q, "TestType2")
        self.assertIsInstance(Validator.types_mapping['TestType1'], TypeDefinition)
        self.assertIsInstance(Validator.types_mapping['TestType2'], TypeDefinition)

    def test_ObservationValidator(self):
        from sciunit.validators import ObservationValidator
        from sciunit import Test
        import random

        long_test_list = [None] * 100
        for index in range(100):
            long_test_list[index] = random.randint(1, 1000)

        test_dict = {'a': 1, 'b': 2, 'c': 3}
        # test constructor
        obsVal = ObservationValidator(test=Test(long_test_list))
        self.assertIsInstance(obsVal, ObservationValidator)
        self.assertRaises(BaseException, ObservationValidator)

        # test _validate_iterable
        obsVal._validate_iterable(True, "key", long_test_list)
        self.assertRaises(
            BaseException, obsVal._validate_iterable, is_iterable=True, key="Test key", value=0)

        # test _validate_units
        self.assertRaises(
            BaseException, obsVal._validate_units, has_units=True, key="Test Key", value=0)

        q = pq.Quantity([1, 2, 3], 'ft')
        units = q.simplified.units
        units.name = "UnitName"
        testObj = Test(long_test_list)
        obsVal = ObservationValidator(test=testObj)

        # units in test object is a dict
        testObj.units = {'TestKey': units}
        obsVal._validate_units(has_units=True, key="TestKey", value=q)

        # units in test object is q.simplified.units
        testObj.units = units
        obsVal._validate_units(has_units=True, key="TestKey", value=q)

        # Units dismatch
        q = pq.Quantity([1], 'J')
        self.assertRaises(
            BaseException, obsVal._validate_units, has_units=True, key="", value=q)

    def test_ParametersValidator(self):
        from sciunit.validators import ParametersValidator
        paraVal = ParametersValidator()

        # test validate_quantity
        q = pq.Quantity([1, 2, 3], 'A')
        paraVal.validate_quantity(q)
        self.assertRaises(
            BaseException, paraVal.validate_quantity, "I am not a quantity")

        q = pq.Quantity([1,2,3], pq.s)
        self.assertTrue(paraVal._validate_type_time(q))
        self.assertRaises(
            BaseException, paraVal._validate_type_voltage, q)
        self.assertRaises(
            BaseException, paraVal._validate_type_current, q)

        q = pq.Quantity([1,2,3], pq.V)
        self.assertTrue(paraVal._validate_type_voltage(q))
        self.assertRaises(
            BaseException, paraVal._validate_type_time, q)
        self.assertRaises(
            BaseException, paraVal._validate_type_current, q)

        q = pq.Quantity([1,2,3], pq.A)
        self.assertTrue(paraVal._validate_type_current(q))
        self.assertRaises(
            BaseException, paraVal._validate_type_voltage, q)
        self.assertRaises(
            BaseException, paraVal._validate_type_time, q)

if __name__ == '__main__':
    unittest.main()
