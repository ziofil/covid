import pandas as pd
import numpy as np
import altair as alt
import world_bank_data as wb
import webbrowser
import argparse
from typing import List


def download_data(url:str, name:str) -> pd.DataFrame:
    data = pd.read_csv(url)
    data.index.name = name + ' as of ' + pd.to_datetime(data.columns[-1]).strftime('%d-%m-%Y')
    world = data.drop(['Lat','Long','Province/State','Country/Region'], axis=1)
    world['Lat'] = None
    world['Long'] = None
    world['Province/State'] = None
    world['Country/Region'] = 'World'
    data = data.append(world)
    return data

def cleanup_data(df:pd.DataFrame, countries:List[str], new_cases:bool, relative_to_pop:bool) -> pd.DataFrame:
    df = df[(df['Country/Region'].isin(countries)) & (confirmed['Province/State'].isna())]
    raw = df.T
    raw.columns = df['Country/Region']
    df = raw.drop(['Province/State','Country/Region','Lat','Long'])
    df = df.shift(-1) - df if new_cases else df
    df[df < 1] = 1
    df = df/pop[pop.index.isin(countries)] if relative_to_pop else df
    return df

def select_countries(countries:list, new_cases:bool=False, relative_to_pop:bool=False, moving_avg_days:int=1) -> pd.DataFrame:
    conf = cleanup_data(confirmed, countries, new_cases, relative_to_pop)
    dead = cleanup_data(deaths, countries, new_cases, relative_to_pop)
    col = pd.MultiIndex.from_arrays([['Confirmed']*len(conf.columns) + ['Deaths']*len(conf.columns), list(conf.columns)*2])
    both = pd.concat([conf, dead], axis=1)
    both.columns = col
    both.index.name = 'Dates'
    both = both.rolling(moving_avg_days).mean()
    both = both.reset_index().melt('Dates', var_name=['Mode','Country'], value_name='cases').dropna()
    return both.dropna()


def line(df, log_scale:bool=False, relative_to_pop:bool=False):
    if log_scale:
        scale = alt.Scale(type='log', base=10, domain=[1, df['cases'].max()])
    else:
        scale = alt.Scale(type='linear')
    
    if relative_to_pop:
        axis = alt.Axis(format="%", title="% of population", orient='right')
    else:
        axis = alt.Axis(title="Cases", orient='right')
    
    country = alt.selection_multi(fields=['Country'], bind='legend')
    mode = alt.selection_single(fields=['Mode'], bind='legend')
    chart = alt.Chart(df).mark_line(interpolate='basis').encode(
    x='Dates:T',
    y = alt.Y('cases:Q', scale=scale, axis=axis),
    color=alt.Color('Country:N', scale=alt.Scale(domain=list(df.Country.unique()))),
    strokeDash=alt.Opacity('Mode:N', scale=alt.Scale(domain=list(df.Mode.unique())))
    ).add_selection(country, mode).transform_filter(country).transform_filter(mode)
    return chart


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Make covid charts.')
    parser.add_argument('--browser', '-b', type=str, required=False, default=None, help='the path to a browser for chart visualization')
    args = parser.parse_args()

    print("🦠 downloading data...")
    confirmed = download_data('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv', 'Confirmed cases')
    deaths = download_data('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv', 'Deaths')

    pop = wb.get_series('SP.POP.TOTL', mrv=1, simplify_index=True)
    pop.rename(index={'United States':'US'},inplace=True)
    pop.rename(index={'Russian Federation':'Russia'},inplace=True)

    print("📈 generating graphs...")
    countries = ['US', 'Brazil', 'Spain', 'Italy', 'France', 'Russia', 'United Kingdom', 'India', 'Germany', 'Cyprus']
    df_new_absolute = select_countries(countries, new_cases=True, relative_to_pop=False, moving_avg_days=7)
    df_new_relative = select_countries(countries, new_cases=True, relative_to_pop=True, moving_avg_days=7)
    df_total_absolute = select_countries(countries, new_cases=False, moving_avg_days=1, relative_to_pop=False)
    df_total_relative = select_countries(countries, new_cases=False, moving_avg_days=1, relative_to_pop=True)

    line_new_absolute = line(df_new_absolute, log_scale = True, relative_to_pop=False).properties(width=900, height=500, title='Absolute new Cases/deaths')
    line_new_relative = line(df_new_relative, log_scale = False, relative_to_pop=True).properties(width=900, height=500, title='Relative new Cases/deaths')
    line_total_absolute = line(df_total_absolute, log_scale = False, relative_to_pop=False).properties(width=900, height=500, title='Absolute total Cases/deaths')
    line_total_relative = line(df_total_relative, log_scale = False, relative_to_pop=True).properties(width=900, height=500, title='Relative total Cases/deaths')

    print("📥 saving graphs to html...")
    line_new_absolute.save('new_cases_absolute.html')
    line_new_relative.save('new_cases_relative.html')
    line_total_absolute.save('total_cases_absolute.html')
    line_total_relative.save('total_cases_relative.html')

    if args.browser is not None:
        webbrowser.get(f"open -a {args.browser} %s").open('new_cases_absolute.html',1)
        webbrowser.get(f"open -a {args.browser} %s").open('new_cases_relative.html',2)
        webbrowser.get(f"open -a {args.browser} %s").open('total_cases_absolute.html',3)
        webbrowser.get(f"open -a {args.browser} %s").open('total_cases_relative.html',4)