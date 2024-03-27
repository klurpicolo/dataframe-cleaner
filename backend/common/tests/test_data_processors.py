import unittest

import pandas as pd

from backend.common.data_processors import infer_col, infer_df, process_operation_apply_script


class TestDataTypes(unittest.TestCase):

    def test_defer_boolean(self):
        data = ['true', 'false', 'true', 'false', 'false']
        ser = pd.Series(data)

        result = infer_col(ser)
        self.assertEqual(result.dtype, 'bool')

    def test_defer_boolean_non_clean(self):
        data = ['true', 'false', 'true', 'false', 'false', 'false', 'false', 'true', 'false', 'N/A']
        expected_bool = [True, False, True, False, False, False, False, True, False, False]
        ser = pd.Series(data)

        result = infer_col(ser)
        self.assertEqual(result.dtype, 'bool')
        self.assertSequenceEqual(result.to_list(), expected_bool)

    def test_defer_date_ddmmyy(self):
        data = ['10/11/12', '10/11/13', '10/11/14', '10/12/15', '30/12/15']
        expected_dates = ['2012-11-10', '2013-11-10', '2014-11-10', '2015-12-10', '2015-12-30']
        ser = pd.Series(data)

        result = infer_col(ser)
        self.assertEqual(result.dtype, 'datetime64[ns]')
        for i, date in enumerate(result):
            self.assertEqual(date.strftime('%Y-%m-%d'), expected_dates[i])

    def test_defer_date_yyyymmdd(self):
        data = ['2011-02-01', '2011-03-01', '2011-04-01', '2015-01-01', '2019-01-14']
        expected_dates = ['2011-02-01', '2011-03-01', '2011-04-01', '2015-01-01', '2019-01-14']
        ser = pd.Series(data)

        result = infer_col(ser)
        self.assertEqual(result.dtype, 'datetime64[ns]')
        for i, date in enumerate(result):
            self.assertEqual(date.strftime('%Y-%m-%d'), expected_dates[i])

    def test_defer_category(self):
        # all 60 values, with 4 unique value. So the theshold is 4/60 = 0.06
        data = ['A', 'B', 'D', 'D', 'C', 'A', 'B', 'D', 'C', 'A', 'B', 'D', 'D', 'C', 'A', 'A','D', 'D', 'A', 'A',
            'A', 'B', 'D', 'D', 'C', 'A', 'B', 'D', 'C', 'A', 'B', 'D', 'D', 'C', 'A', 'A','D', 'D', 'A', 'A',
            'A', 'B', 'D', 'D', 'C', 'A', 'B', 'D', 'C', 'A', 'B', 'D', 'D', 'C', 'A', 'A','D', 'D', 'A', 'A']
        ser = pd.Series(data)

        result = infer_col(ser)
        self.assertEqual(result.dtype, 'category')

    def test_defer_string(self):
        # all 60 values, with 4 unique value. So the theshold is 4/60 = 0.06
        data = ['Hello', 'World', 'I am', 'Software', 'Engineer']
        ser = pd.Series(data)

        result = infer_col(ser)
        self.assertEqual(result.dtype, 'object')

    def test_data_type_inference_dataframe(self):
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
        self.assertEqual(result_df['A'].dtype, 'datetime64[ns]')
        self.assertEqual(result_df['B'].dtype, 'int64')
        self.assertEqual(result_df['C'].dtype, 'object')
        self.assertEqual(result_df['D'].dtype, 'bool')
        self.assertEqual(result_df['E'].dtype, 'object')

    def test_handling_of_bad_data_cases(self):
        data = {
            'A': ['2022-01-01', '2022-02-01', 'bad data', '2022-03-05', '2022-03-07', '2022-03-05', '2022-03-07'],
            'B': ['1', '2', '3', '7', '8', 'bad data', '10'],
            'C': ['a', 'b', 'b', 'bad data', 'a', 'b', 'b'],
            'D': ['True', 'False', 'True', 'False', 'True', 'bad data', 'False'],
            'E': ['Hello', 'its', 'bad data', 'klur', 'world', 'happy', 'coding']
        }
        sample_df = pd.DataFrame(data)

        result_df = infer_df(sample_df)
        self.assertEqual(result_df['A'].dtype, 'datetime64[ns]')
        self.assertEqual(result_df['B'].dtype, 'float64')
        self.assertEqual(result_df['C'].dtype, 'object') # Because the ratio of unique and len isn't low enough
        self.assertEqual(result_df['D'].dtype, 'bool')
        self.assertEqual(result_df['E'].dtype, 'object')

    def test_process_operation_apply_script(self):
        col = 'email'
        data = {
            col: [ 'bguzman@example.org',
                    'melendezmary@example.com',]
        }
        sample_df = pd.DataFrame(data)
        result = process_operation_apply_script(sample_df, col, "x.split('@')[0]")

        self.assertEqual(result[col][0], 'bguzman')
        self.assertEqual(result[col][1], 'melendezmary')


if __name__ == '__main__':
    unittest.main()
