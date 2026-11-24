import unittest
import numpy as np
import pandas as pd
import analyze_peloton as a

class ReleaseChecks(unittest.TestCase):
    def test_minimized_schema_and_time_split(self):
        data=a.load_data()
        self.assertEqual(set(data), {'ride_id','day_index',a.TARGET,*a.FEATURES})
        train,test=a.split(data)
        self.assertEqual((len(train),len(test)),(331,89))
        self.assertLess(train.day_index.max(),test.day_index.min())
        self.assertAlmostEqual(train[a.TARGET].mean(),0,places=10)

    def test_preprocessing_uses_training_partition(self):
        train,test=a.split(a.load_data())
        fitted=a.make_pipeline_for('Ridge regression').fit(train[a.FEATURES],train[a.TARGET])
        numeric=fitted.steps[0][1].named_transformers_['numeric']
        imputed=numeric.steps[0][1].transform(train[a.NUMERIC])
        np.testing.assert_allclose(numeric.steps[1][1].mean_,imputed.mean(axis=0))
        self.assertTrue(np.isfinite(fitted.predict(test[a.FEATURES])).all())

    def test_report_distinguishes_selection_and_later_results(self):
        late=pd.read_csv(a.ROOT/'results/model_scores.csv').set_index('model')
        dev=pd.read_csv(a.ROOT/'results/development_cv_summary.csv').set_index('model')
        self.assertEqual(late.MAE_index.idxmin(),'Ridge regression')
        self.assertEqual(dev['mean'].idxmin(),'Recent 28-day mean')
        self.assertTrue(late.loc['Recent 28-day mean','selected_by_development_cv'])

if __name__=='__main__': unittest.main()
