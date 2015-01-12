
import csv
import math
import numpy as np
import pandas as pd

sources_file = 'external/source-metadata.csv'
count_file = '../csv-generator/output/stories-by-source-and-country.csv'

dhl_file = 'external/dhl_gci_2011.csv'
gdp_file = 'external/gdp-2010.csv'
inet_file = 'external/internet_users.csv'
migrant_file = 'external/migrant-2010.csv'
pop_file = 'external/population-2010.csv'

def entropy(count_df):
    fraction_df = np.divide(count_df, (count_df.sum(1))[:,None])
    entropy_df = -1 * (fraction_df * np.log2(fraction_df)).sum(1)
    entropy_df = pd.DataFrame({'entropy':entropy_df})
    return entropy_df

def remove_domestic(count_df):
    '''Remove domestic counts for each source.'''
    # Get the column labels of the max for each source
    df = pd.DataFrame(count_df).dropna()
    max_df = df.transpose().idxmax()
    for url, label in max_df.iteritems():
        df.loc[url, label] = 0
    return df

def index_lower(df):
    df.index = map(str.lower, df.index)
    return df

def columns_lower(df):
    df.columns = map(str.lower, df.columns)
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

    # Load demographic data
    dhl_df = index_lower(pd.DataFrame.from_csv(dhl_file))
    gdp_df = index_lower(pd.DataFrame.from_csv(gdp_file))
    inet_df = index_lower(pd.DataFrame.from_csv(inet_file))
    migrant_df = index_lower(pd.DataFrame.from_csv(migrant_file))
    pop_df = index_lower(pd.DataFrame.from_csv(pop_file))
    demo_df = pd.DataFrame(index=count_df.columns)
    demo_df['dhl'] = dhl_df['Overall'].astype('float64')
    demo_df['total_gdp'] = gdp_df['GDP 2010'].astype('float64')
    demo_df['population'] = pop_df['Population'].astype('float64')
    demo_df['inet_users'] = inet_df['Internet Users'].astype('float64')
    demo_df['migrant_stock'] = migrant_df['Total Stock'].astype('float64')
    demo_df['inet_pen'] = np.divide(demo_df['inet_users'],demo_df['population'])
    demo_df['migrant_per'] = np.divide(demo_df['migrant_stock'],demo_df['population'])
    demo_df.to_csv('output/demographics.csv')

    # Calculate entropy of each source
    entropy_df = entropy(count_df)
    foreign_df = remove_domestic(count_df)
    foreign_entropy_df = entropy(foreign_df)
    # Add entropy to combined results
    combined_df = pd.DataFrame(source_df)
    combined_df['entropy'] = entropy_df['entropy']
    combined_df['foreign_entropy'] = foreign_entropy_df['entropy']
    combined_df.to_csv('output/combined.csv')

    # Construct observations for linear regression model
    foreign_fraction_df = np.divide(foreign_df, (foreign_df.sum(1))[:,None])
    fraction_df = np.divide(count_df, (count_df.sum(1))[:,None])
    results = {
        'type':[], 'population':[], 'total_gdp':[], 'dhl':[], 'migrant_per':[], 'inet_pen':[], 'attention':[]
    }
    foreign_results = {
        'type':[], 'population':[], 'total_gdp':[], 'dhl':[], 'migrant_per':[], 'inet_pen':[], 'attention':[]
    }    
    home_df = count_df.transpose().idxmax()
    for country, col in fraction_df.iteritems():
        for url, attention in col.iteritems():
            if attention > 0 and attention < 1:
                results['type'].append(source_df.loc[url,'type'])
                results['population'].append(demo_df.loc[country.lower(), 'population'])
                results['total_gdp'].append(demo_df.loc[country.lower(), 'total_gdp'])
                results['dhl'].append(demo_df.loc[country.lower(), 'dhl'])
                results['migrant_per'].append(demo_df.loc[country.lower(), 'migrant_per'])
                results['inet_pen'].append(demo_df.loc[country.lower(), 'inet_pen'])
                results['attention'].append(attention)
    for country, col in foreign_fraction_df.iteritems():
        for url, attention in col.iteritems():
            if attention > 0 and attention < 1:
                foreign_results['type'].append(source_df.loc[url,'type'])
                foreign_results['population'].append(demo_df.loc[country.lower(), 'population'])
                foreign_results['total_gdp'].append(demo_df.loc[country.lower(), 'total_gdp'])
                foreign_results['dhl'].append(demo_df.loc[country.lower(), 'dhl'])
                foreign_results['migrant_per'].append(demo_df.loc[country.lower(), 'migrant_per'])
                foreign_results['inet_pen'].append(demo_df.loc[country.lower(), 'inet_pen'])
                foreign_results['attention'].append(attention)
    result_df = pd.DataFrame(results).dropna()
    result_df.to_csv('output/attention.csv')
    foreign_result_df = pd.DataFrame(foreign_results).dropna()
    foreign_result_df.to_csv('output/foreign_attention.csv')

    # Calculate average entropy for media types
    average_df = combined_df.loc[:,['type','entropy','foreign_entropy']]
    average_df = average_df.groupby('type').mean()
    average_df.to_csv('output/media_types.csv')
    
if __name__ == '__main__':
    main()
