import unittest
import quantities as pq
class ValidatorTestCase(unittest.TestCase):
    def register_test(self):
        class TestClass():
            intValue = 0
            def getIntValue(self):
                return self.intValue
        from sciunit.validators import register_quantity, register_type
        register_type(TestClass, "TestType1")
        q = pq.Quantity([1,2,3], 'J')
        register_quantity(q, "TestType2")