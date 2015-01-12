import csv
import math
import numpy as np
import pandas as pd

sources_file = 'external/source-metadata.csv'
count_file = '../csv-generator/output/stories-by-source-and-country.csv'
estimate_file = 'output/estimate.csv'

def index_lower(df):
    df.index = map(str.lower, df.index)
    return df

def columns_lower(df):
    df.columns = map(str.lower, df.columns)
    return df

def remove_domestic(count_df):
    '''Remove domestic counts for each source.'''
    # Get the column labels of the max for each source
    df = pd.DataFrame(count_df).dropna()
    max_df = df.transpose().idxmax()
    for url, label in max_df.iteritems():
        df.loc[url, label] = 0
    return df

def main():
    # Load source and count data
    source_df = pd.DataFrame.from_csv(sources_file)
    count_df = columns_lower(
        pd.DataFrame.from_csv(count_file)
        .transpose().reset_index()
    )
    # Set is_copy to False so pandas doesn't warn about modifying
    count_df.is_copy = False
    # Only consider the first url listed for each row
    for i, url in count_df['index'].iteritems():
        count_df.at[i,'index'] = url.split(',')[0]
    # Use url as index
    count_df.set_index('index', inplace=True)
    count_df.index.rename('url', inplace=True)
    foreign_df = remove_domestic(count_df)
    fraction_df = np.divide(foreign_df, (foreign_df.sum(1))[:,None])
    
    # Load estimate data
    est_df = pd.DataFrame.from_csv(estimate_file)
    
    # Remove rows with no estimate
    df = fraction_df.transpose()
    df = df.loc[est_df.index,:].transpose()
    dev_df = (df - est_df.transpose().iloc[0]).transpose()
    dev_df.to_csv('output/deviation.csv')

if __name__ == '__main__':
    main()