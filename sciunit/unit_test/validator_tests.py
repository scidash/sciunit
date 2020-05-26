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
        q = pq.Quantity([1,2,3], 'J')
        register_quantity(q, "TestType2")
        self.assertTrue(isinstance(Validator.types_mapping['TestType1'], TypeDefinition))
        self.assertTrue(isinstance(Validator.types_mapping['TestType2'], TypeDefinition))

if __name__ == '__main__':
    unittest.main()