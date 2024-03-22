import unittest

import pandas as pd

from backend.common.data_processors import infer_df


class TestDataTypes(unittest.TestCase):

    def test_data_type_inference(self):
        # Create a sample DataFrame for testing
        data = {
            'A': ['2022-01-01', '2022-02-01', '2022-03-01', '2022-03-05', '2022-03-07', '2022-03-05', '2022-03-07'],
            'B': ['1', '2', '3', '7', '8', '9', '10'],
            'C': ['a', 'b', 'c', 'a', 'a', 'b', 'c'],
            'D': [True, False, True, False, True, False, False],
            'E': ['Hello', 'its', 'me', 'klur', 'world', 'happy', 'coding']
        }
        sample_df = pd.DataFrame(data)


        result_df = infer_df(sample_df)
        print(f'klir {result_df.dtypes}')
        self.assertEqual(result_df['A'].dtype, 'datetime64[ns]')
        self.assertEqual(result_df['B'].dtype, 'int64')
        self.assertEqual(result_df['C'].dtype, 'category')
        self.assertEqual(result_df['D'].dtype, 'bool')
        self.assertEqual(result_df['E'].dtype, 'object')

    def test_handling_of_special_cases(self):
        data = {
            'A': ['2022-01-01', '2022-02-01', 'bad data', '2022-03-05', '2022-03-07', '2022-03-05', '2022-03-07'],
            'B': ['1', '2', '3', '7', '8', 'bad data', '10'],
            'C': ['a', 'b', 'b', 'bad data', 'a', 'b', 'b'],
            # 'D': [True, False, True, False, True, 'bad data', False], //todo make it works
            'E': ['Hello', 'its', 'bad data', 'klur', 'world', 'happy', 'coding']
        }
        sample_df = pd.DataFrame(data)


        result_df = infer_df(sample_df)
        print(f'klir {result_df.dtypes}')
        self.assertEqual(result_df['A'].dtype, 'datetime64[ns]')
        self.assertEqual(result_df['B'].dtype, 'float64') # ToDO check this
        self.assertEqual(result_df['C'].dtype, 'category')
        # self.assertEqual(result_df['D'].dtype, 'boolean')
        self.assertEqual(result_df['E'].dtype, 'object')

if __name__ == '__main__':
    unittest.main()
