import pandas as pd

def load_population_projections_df():
    df = pd.read_excel(
        'http://www.dof.ca.gov/Forecasting/Demographics/Projections/documents/P_Components.xlsx',
        header=2,
    )
    df.drop(index=len(df) - 1, inplace=True)
    df = df[df['Start Year'] != df['End Year']].copy()
    df = df.astype({
        'Start Year': int,
        'Start Population': int,
        'Births': int,
        'Deaths': int,
        'Net migrants': int,
        'End Year': int,
        'End Population': int,
    })
    return df

def load_historical_estimates_df():
    df = pd.read_excel(
        'http://www.dof.ca.gov/Forecasting/Demographics/Estimates/E-6/documents/E-6_Report_July_2010-2019w.xlsx',
        sheet_name=1,
        header=2
    )
    df.drop(index=0, inplace=True)
    df.drop(index=df.index.max() - pd.Index([0, 1, 2, 3]), inplace=True)
    df.rename(
        columns={'Population \n(July 1)': 'Population (July 1)'}, inplace=True
    )

    def combine_fn(row):
        if pd.notnull(row['previous']):
            return None
        if pd.notnull(row['first']) and pd.notnull(row['second']):
            return row['first'].strip() + ' ' + row['second'].strip()
        return row['first']
    df['County'] = pd.DataFrame({
        'previous': df['County'].shift(1),
        'first': df['County'],
        'second': df['County'].shift(-1),
    }).apply(combine_fn, axis=1)

    df['County'] = df['County'].ffill()
    df.dropna(subset=df.columns.drop('County'), inplace=True)
    return df

def load_detailed_projections_df():
    df = pd.read_csv('PROJECTS/POPFC/B2019 - Copy - Copy/P3_Complete.csv')
    df['race7'] = df['race7'].map({
        1: 'White, Non-Hispanic',
        2: 'Black, Non-Hispanic',
        3: 'American Indian or Alaska Native, Non-Hispanic',
        4: 'Asian, Non-Hispanic',
        5: 'Native Hawaiian or Pacific Islander, Non-Hispanic',
        6: 'Multiracial (two or more of above races), Non-Hispanic',
        7: 'Hispanic (any race)',
    })

    fips_df = pd.read_excel(
        'https://www2.census.gov/programs-surveys/popest/geographies/2019/all-geocodes-v2019.xlsx',
        skiprows=[0,1,2],
        header=1,
    )
    fips_df.rename(columns={
        'Area Name (including legal/statistical area description)': 'Area Name',
        'Consolidtated City Code (FIPS)': 'Consolidated City Code (FIPS)',
    }, inplace=True)

    df['county'] = df.merge(
        fips_df,
        left_on='fips',
        right_on=1000 * fips_df['State Code (FIPS)'] + fips_df['County Code (FIPS)'],
        how='left',
    )['Area Name']

    return df
