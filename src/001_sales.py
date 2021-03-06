
import feather
import gc
import numpy as np
import pandas as pd
import sys
import warnings

from tqdm import tqdm

from utils import save2pkl, line_notify, reduce_mem_usage, to_pickles
from utils import COLS_TEST1, COLS_TEST2

#===============================================================================
# preprocess sales
#===============================================================================

warnings.simplefilter(action='ignore')

def main(is_eval=False):
    # load csv
    if is_eval:
        df = pd.read_csv('../input/sales_train_evaluation.csv')
    else:
        df = pd.read_csv('../input/sales_train_validation.csv')

    sub = pd.read_csv('../input/sample_submission.csv')

    # split test data
    sub['is_test1']=sub['id'].apply(lambda x: True if '_validation' in x else False)
    sub['is_test2']=sub['id'].apply(lambda x: True if '_evaluation' in x else False)

    test1 = sub[sub['is_test1']]
    test2 = sub[sub['is_test2']]

    del sub
    gc.collect()

    # drop flags
    test1.drop(['is_test1','is_test2'],axis=1,inplace=True)
    test2.drop(['is_test1','is_test2'],axis=1,inplace=True)

    # change column name
    test1.columns = ['id']+COLS_TEST1
    test2.columns = ['id']+COLS_TEST2

    # change id
    test2['id'] = test2['id'].str.replace('_evaluation','_validation')

    # merge
    if not is_eval:
        df = df.merge(test1,on='id',how='left')

    df = df.merge(test2,on='id',how='left')

    del test1, test2
    gc.collect()

    # reduce memory usage
    df = reduce_mem_usage(df)

    # date columns
    cols_date = [c for c in df.columns if 'd_' in c]

    # melt sales data
    print('Melting sales data...')
    id_vars = ['id','item_id','dept_id','cat_id','store_id','state_id']
    df = pd.melt(df,id_vars=id_vars,var_name='d',value_name='demand')

    print('Melted sales train validation has {} rows and {} columns'.format(df.shape[0], df.shape[1]))

    # add numeric date
    df['d_numeric'] = df['d'].apply(lambda x: int(x[2:]))

    # drop old data (~2012/12/31)
    print('drop old data...')
    df = df[df['d_numeric']>=704]

    # drop christmas data
    print('drop christmas data...')
    df = df[df['d_numeric']!=331] # 2011-12-25
    df = df[df['d_numeric']!=697] # 2012-12-25
    df = df[df['d_numeric']!=1062] # 2013-12-25
    df = df[df['d_numeric']!=1427] # 2014-12-25
    df = df[df['d_numeric']!=1792] # 2015-12-25

    # add is zero flag
    df['is_zero'] = (df['demand']==0).astype(int)

    # save pkl
    to_pickles(df, '../feats/sales', split_size=3)

    # LINE notify
    line_notify('{} done.'.format(sys.argv[0]))

if __name__ == '__main__':
    main(is_eval=True)
