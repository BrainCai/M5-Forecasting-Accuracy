
import gc
import json
import lightgbm as lgb
import numpy as np
import pandas as pd
import warnings

from glob import glob
from tqdm import tqdm

from utils import submit
from utils import FEATS_EXCLUDED, COLS_TEST1, COLS_TEST2
from utils_lag import make_lags

#==============================================================================
# prediction by cat_id
#==============================================================================

warnings.filterwarnings('ignore')

def main():
    # load submission files
    sub_foods = pd.read_csv('../output/submission_lgbm_group_k_fold_foods.csv')
    sub_household = pd.read_csv('../output/submission_lgbm_group_k_fold_household.csv')
    sub_hobbies = pd.read_csv('../output/submission_lgbm_group_k_fold_hobbies.csv')

    # load oof files
    oof_foods = pd.read_csv('../output/oof_lgbm_group_k_fold_foods.csv')
    oof_household = pd.read_csv('../output/oof_lgbm_group_k_fold_household.csv')
    oof_hobbies = pd.read_csv('../output/oof_lgbm_group_k_fold_hobbies.csv')

    # merge
    sub = sub_foods.append(sub_household)
    sub = sub.append(sub_hobbies)

    oof = oof_foods.append(oof_household)
    oof = oof.append(oof_hobbies)

    del sub_foods, sub_household, sub_hobbies, oof_foods, oof_household, oof_hobbies
    gc.collect()

    # reshape
    sub = sub.pivot(index='id', columns='d', values='demand').reset_index()
    oof = oof.pivot(index='id', columns='d', values='demand').reset_index()

    # split test1 / test2
    sub1 = oof[['id']+COLS_TEST1]
    sub2 = sub[['id']+COLS_TEST2]

    # change column names
    sub1.columns = ['id'] + ['F' + str(d + 1) for d in range(28)]
    sub2.columns = ['id'] + ['F' + str(d + 1) for d in range(28)]

    # replace test1 id
    sub1['id']= sub1['id'].str.replace('_evaluation','_validation')

    # merge
    sub = sub1.append(sub2)

    # postprocesssing
    cols_f = [f'F{i}' for i in range(1,29)]
    sub.loc[:,cols_f] = sub[cols_f].where(sub[cols_f]>0,0)

    # save csv
    sub.to_csv(submission_file_name, index=False)

    # TODO: calc oof score

    # submission by API
    submit(submission_file_name, comment='model405 prediction by cat_id group k-fold')

if __name__ == '__main__':
    submission_file_name = "../output/submission_cat_id_group_k_fold.csv"
    main()
