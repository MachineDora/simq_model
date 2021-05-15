from os.path import dirname,join
from sklearn.preprocessing import LabelEncoder
import pandas as pd

LABEL_ENCODER = LabelEncoder().fit(['CLEAR', 'UNCLEAR'])


#get train and test data from labeled
def load_train_test(all_csv, train_csv, test_csv):
    df = pd.read_csv(all_csv)
    df.tags.fillna('', inplace=True)
    df.label = LABEL_ENCODER.transform(df.label)
    train_ids = pd.read_csv(train_csv)['id'].values
    train_df = df.loc[train_ids]
    X_train, y_train = train_df[['title', 'body', 'tags']].values, train_df.label

    test_ids = pd.read_csv(test_csv)['id'].values
    test_df = df.loc[test_ids]
    X_test, y_test = test_df[['title', 'body', 'tags']].values, test_df.label

    return X_train, y_train, train_ids, X_test, test_ids

#get clarq of the community
def load_clarqs(community):
    clarq_path = join(dirname(__file__), '../data/clarq/{}.csv'.format(community))
    return pd.read_csv(clarq_path)

#get posts of the community
def load_labeled(community):
    labeled_dir = join(dirname(__file__), '../data/labeled/')
    all_csv = join(labeled_dir, '{}.csv'.format(community))
    train_csv = join(labeled_dir, '{}_train.csv'.format(community))
    test_csv = join(labeled_dir, '{}_test.csv'.format(community))
    X_train, y_train, train_ids, X_test, test_ids = load_train_test(all_csv, train_csv, test_csv)


    return X_train, y_train, train_ids, X_test, test_ids

def load_raw(community):
    in_dir = join(dirname(__file__), '../data/labeled/')
    data_csv = join(in_dir, '{}.csv'.format(community))
    df = pd.read_csv(data_csv)
    df.tags.fillna('', inplace=True)
    df.label = LABEL_ENCODER.transform(df.label)
    return df