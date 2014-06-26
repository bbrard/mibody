import io
import mibody
import unittest


# Two entries in binary form.
BINARY_DATA = b'\x01\xb2\x2a\x11\xc7\x05\xe8\x00\xdb\x00\x3a\x02\xaf\x01\x0a' \
              b'\x00\x45\x08\x0e\x02\x0c\x09\x18\x1e' \
              b'\x01\xb2\x2a\x11\xb3\x05\xe6\x00\xc1\x00\x4d\x02\xb1\x01\x0a' \
              b'\x00\x39\x08\x0e\x02\x0a\x08\x30\x3b'


class MibodyTests(unittest.TestCase):

    def test_scale_record_no_unit(self):
        record = mibody.ScaleRecord()
        self.assertTrue(record.unit == 'lb')

    def test_scale_record_unit(self):
        record = mibody.ScaleRecord('kg')
        self.assertTrue(record.unit == 'kg')

    def test_scale_record_bad_unit(self):
        record = mibody.ScaleRecord('g')
        self.assertTrue(record.unit == 'lb')

    def test_scale_record_construtor(self):
        record = mibody.ScaleRecord()
        self.assertEqual(record.user, 0)
        self.assertEqual(record.height, 0)
        self.assertEqual(record.age, 0)
        self.assertEqual(record.gender, 'M')
        self.assertEqual(record.fitness_level, 0)
        self.assertEqual(record.weight, 0)
        self.assertEqual(record.bmi, 0)
        self.assertEqual(record.fat, 0)
        self.assertEqual(record.water, 0)
        self.assertEqual(record.muscle, 0)
        self.assertEqual(record.visceral_fat, 0)
        self.assertEqual(record.bmr, 0)
        self.assertEqual(record.datetime.year, 2000)
        self.assertEqual(record.datetime.month, 1)
        self.assertEqual(record.datetime.day, 1)

    def test_scale_record_init(self):
        record = mibody.ScaleRecord()
        self.assertTrue(record.init(BINARY_DATA[:24]))
        self.assertEqual(record.user, 1)
        self.assertEqual(record.height, 178)
        self.assertEqual(record.age, 42)
        self.assertEqual(record.gender, 'M')
        self.assertEqual(record.fitness_level, 1)
        self.assertEqual(record.weight, 1479)
        self.assertEqual(record.bmi, 232)
        self.assertEqual(record.fat, 219)
        self.assertEqual(record.water, 570)
        self.assertEqual(record.muscle, 431)
        self.assertEqual(record.visceral_fat, 10)
        self.assertEqual(record.bmr, 2117)
        self.assertEqual(record.datetime.year, 2014)
        self.assertEqual(record.datetime.month, 2)
        self.assertEqual(record.datetime.day, 12)

    def test_scale_record_bad_init(self):
        record = mibody.ScaleRecord()
        # Incorrect length:
        self.assertFalse(record.init(BINARY_DATA[:23]))
        self.assertFalse(record.init(BINARY_DATA[:25]))
        # Bad user:
        binary_data = bytearray(BINARY_DATA[:24])
        binary_data[0] = 0  # Between 1 and 12.
        self.assertFalse(record.init(bytes(binary_data)))
        # Bad fitness level:
        binary_data = bytearray(BINARY_DATA[:24])
        binary_data[3] = 0b11110000  # 4 first bits between 1 and 3.
        self.assertFalse(record.init(bytes(binary_data)))
        # Bad padding:
        binary_data = bytearray(BINARY_DATA[:24])
        binary_data[15] = 1  # Zero expected.
        self.assertFalse(record.init(bytes(binary_data)))
        # Bad date
        binary_data = bytearray(BINARY_DATA[:24])

        binary_data[19] = 13  # Month.
        self.assertFalse(record.init(bytes(binary_data)))

    def test_scale_record_lb_to_kg(self):
        self.assertAlmostEqual(mibody.ScaleRecord.lb_to_kg(173.5), 78.698212)

    def test_scale_record_lb_to_st(self):
        self.assertAlmostEqual(mibody.ScaleRecord.lb_to_st(173.5), 12.39286209)

    def test_scale_record_str(self):
        record = mibody.ScaleRecord('kg')
        self.assertTrue(record.init(BINARY_DATA[:24]))
        expected_output = '2014-02-12 09:24:30\t1\t67.1\t23.2\t21.9\t57.0' \
                          '\t43.1\t10\t2117\t1\tM\t178\t42'
        self.assertEqual(str(record), expected_output)

    def test_scale_parser(self):
        # Valid input.
        stream = io.BytesIO(BINARY_DATA)
        parser = mibody.ScaleParser(stream)
        self.assertEqual(sum(1 for _ in parser), 2)
        # Incorrect length. No output expected.
        stream = io.BytesIO(BINARY_DATA[:26])
        parser = mibody.ScaleParser(stream)
        self.assertEqual(sum(1 for _ in parser), 0)
        # Correct length but invalid chunk. Parsing stopped after
        # the last valid chunk.
        binary_data = bytearray(BINARY_DATA)
        binary_data[39] = 1  # Zero expected.
        stream = io.BytesIO(bytes(binary_data*2))
        parser = mibody.ScaleParser(stream)
        self.assertEqual(sum(1 for _ in parser), 1)


def main():
    unittest.main()


if __name__ == '__main__':
    main()
