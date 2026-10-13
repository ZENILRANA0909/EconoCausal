import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import pandas as pd
import pytest
from app.data.generator import generate_customers
from app.data.validation import validate_dataset
from app.optimization.optimizer import optimize_allocations
from app.monitoring.drift import evaluate_drift


def test_generator_reproducible():
    a,ta=generate_customers(500,7); b,tb=generate_customers(500,7)
    pd.testing.assert_frame_equal(a,b); pd.testing.assert_frame_equal(ta,tb)

def test_truth_is_separate_from_training_data():
    data,truth=generate_customers(500,42)
    assert 'true_cate' not in data and 'propensity_true' not in data
    assert len(data)==len(truth)

def test_validation_clean_and_bad():
    data,_=generate_customers(500,42)
    assert validate_dataset(data)['valid']
    bad=data.drop(columns=['income'])
    assert not validate_dataset(bad)['valid']

def test_optimizer_respects_budget_and_one_offer():
    s=pd.DataFrame([
      {'customer_id':'A','discount_pct':0,'expected_discount_cost':0,'incremental_profit':0},
      {'customer_id':'A','discount_pct':10,'expected_discount_cost':30,'incremental_profit':50},
      {'customer_id':'B','discount_pct':0,'expected_discount_cost':0,'incremental_profit':0},
      {'customer_id':'B','discount_pct':10,'expected_discount_cost':30,'incremental_profit':45},
    ])
    result=optimize_allocations(s,30,[0,10])
    assert result['feasible'] and result['discount_cost'] <= 30+1e-6
    assert len({x['customer_id'] for x in result['allocations']})==len(result['allocations'])
    assert result['incremental_profit']==50

def test_drift_empty_is_honest():
    result=evaluate_drift(pd.DataFrame(),pd.DataFrame({'x':[1]}))
    assert result['available'] is False and result['status']=='no_evaluation'
