
import ConfigParser, csv, math, os

import numpy as np
import pandas as pd

sources_file = 'external/source-metadata.csv'
count_file = '../story-fetcher/output/stories-by-source-and-country.csv'
alexa_file = '../alexa-scraper/data/alexa-top-all.csv'

dhl_file = 'external/dhl_gci_2011.csv'
gdp_file = 'external/gdp-2010.csv'
inet_file = 'external/internet_users.csv'
migrant_file = 'external/migrant-2010.csv'
pop_file = 'external/population-2010.csv'
common_file = '../data/common.csv'

# load shared config file
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
config = ConfigParser.ConfigParser()
config.read(parent_dir+'/mc-client.config')

def entropy(count_df):
    n = (count_df.sum(1))
    f = np.divide(count_df, n[:,None])
    entropy = -1 * (f * np.log2(f)).sum(1)
    nonzero = list()
    p80 = list()
    country = list()

    # Load alexa
    alexa_df = pd.DataFrame.from_csv(alexa_file,index_col=None)
    alexa_df.set_index('domain', inplace=True)

    for url in count_df.index:
        nonzero.append(np.count_nonzero(count_df.loc[url,:]))
        url_counts = sorted(count_df.loc[url,:], reverse=True)
        total = 0
        top = 0
        for idx, count in enumerate(url_counts):
            total += count
            if float(total) >= 0.8 * sum(url_counts):
                top = idx
                break
        p80.append(top)
        country.append(alexa_df.loc[url]['country'])
    entropy_df = pd.DataFrame({
        'entropy': list(entropy)
        , 'count': list(n)
        , 'unique_countries': nonzero
        , 'in_top_80': p80
        , 'country': country
    }, index=count_df.index)
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
        .reset_index()
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
    common_df = pd.DataFrame.from_csv(common_file)
    demo_df['dhl'] = dhl_df['Overall'].astype('float64')
    demo_df['total_gdp'] = gdp_df['GDP 2010'].astype('float64')
    demo_df['population'] = pop_df['Population'].astype('float64')
    demo_df['inet_users'] = inet_df['Internet Users'].astype('float64')
    demo_df['migrant_stock'] = migrant_df['Total Stock'].astype('float64')
    demo_df['inet_pen'] = np.divide(demo_df['inet_users'],demo_df['population'])
    demo_df['migrant_per'] = np.divide(demo_df['migrant_stock'],demo_df['population'])
    demo_df['troop'] = common_df['troop'].astype('float64')
    demo_df['import'] = common_df['import'].astype('float64')
    demo_df['export'] = common_df['export'].astype('float64')
    demo_df['trade'] = demo_df['import'] + demo_df['export']
    demo_df['dist_capital'] = common_df['dist_capital']
    demo_df.to_csv('output/demographics.csv')

    # Calculate entropy of each source
    entropy_df = entropy(count_df)
    
    entropy_df = entropy_df[entropy_df.country=='us']
    foreign_df = remove_domestic(count_df)
    # Remove sources with very few international stories
    foreign_df = foreign_df[foreign_df.sum(1) >= config.getint('analysis', 'min_articles')]
    foreign_df.to_csv('output/us_top_counts.csv')
    
    foreign_entropy_df = entropy(foreign_df)
    foreign_entropy_df.to_csv('output/foreign_entropy.csv')
    # Add entropy to combined results
    combined_df = pd.DataFrame(source_df)
    combined_df['alpha3'] = pd.Series()
    combined_df['foreign_entropy'] = pd.Series(foreign_entropy_df['entropy'])

    # Construct observations for linear regression model
    foreign_fraction_df = np.divide(foreign_df, (foreign_df.sum(1))[:,None])
    fraction_df = np.divide(count_df, (count_df.sum(1))[:,None])
    results = {
        'country':[], 'source':[], 'type':[], 'population':[], 'total_gdp':[], 'dhl':[], 'migrant_per':[], 'inet_pen':[], 'troop':[], 'import':[], 'export':[], 'trade':[], 'dist_capital':[], 'attention':[]
    }
    foreign_results = {
        'country':[], 'source':[], 'type':[], 'population':[], 'total_gdp':[], 'dhl':[], 'migrant_per':[], 'inet_pen':[], 'troop':[], 'import':[], 'export':[], 'trade':[], 'dist_capital':[], 'attention':[]
    }
    home_df = count_df.transpose().idxmax()
    for country, col in fraction_df.iteritems():
        for url, attention in col.iteritems():
            if attention > 0 and attention < 1:
                results['source'].append(url)
                results['country'].append(country)
                results['type'].append(source_df.loc[url,'type'])
                results['population'].append(demo_df.loc[country.lower(), 'population'])
                results['total_gdp'].append(demo_df.loc[country.lower(), 'total_gdp'])
                results['dhl'].append(demo_df.loc[country.lower(), 'dhl'])
                results['migrant_per'].append(demo_df.loc[country.lower(), 'migrant_per'])
                results['inet_pen'].append(demo_df.loc[country.lower(), 'inet_pen'])
                results['troop'].append(demo_df.loc[country.lower(), 'troop'])
                results['import'].append(demo_df.loc[country.lower(), 'import'])
                results['export'].append(demo_df.loc[country.lower(), 'export'])
                results['trade'].append(demo_df.loc[country.lower(), 'trade'])
                results['dist_capital'].append(demo_df.loc[country.lower(), 'dist_capital'])
                results['attention'].append(attention)
    for country, col in foreign_fraction_df.iteritems():
        for url, attention in col.iteritems():
            if attention > 0 and attention < 1:
                foreign_results['source'].append(url)
                foreign_results['country'].append(country)
                foreign_results['troop'].append(demo_df.loc[country.lower(), 'troop'])
                foreign_results['import'].append(demo_df.loc[country.lower(), 'import'])
                foreign_results['export'].append(demo_df.loc[country.lower(), 'export'])
                foreign_results['trade'].append(demo_df.loc[country.lower(), 'trade'])
                foreign_results['dist_capital'].append(demo_df.loc[country.lower(), 'dist_capital'])
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
