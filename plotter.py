import pandas as pd
import argparse
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MultipleLocator
from datetime import date
import json

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

STATES_MAPPING_FNAME = 'state-codes.json'
STATES_FNAME = 'data/us-states.csv'
# columns: date, state, fips, cases, deaths
COUNTIES_FNAME = 'data/us-counties.csv'
# columns: date, county, state, fips, cases, deaths


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', '--keys', nargs='+', help='list State or State:County', 
        default=list(), dest='keys')
    parser.add_argument('-d', '--deaths', help='plot cumulative deaths', 
        dest='plot_deaths', action='store_true')
    return parser



def process_state_input(keys):
    """replace state abbreviations with their full name"""

    if len(keys) == 0:
        # there's no need to spend time loading and processing the mapping file
        return keys
        
    # load the state abbreviations
    f = open(STATES_MAPPING_FNAME, 'r')
    mapping = json.load(f)
    f.close()

    # replace state abbreviations with their full name if abbreviation found
    output = []
    for entry in keys:
        if ':' in entry:
            state, county = entry.split(':')[0:2]
            if state in mapping:
                output.append('{}:{}'.format(mapping[state], county))
            else:
                output.append(entry)
        else:
            output.append(mapping[entry] if entry in mapping else entry)
    return output


    
if __name__ == '__main__':
    # parse arguments
    parser = create_parser()
    args = parser.parse_args()

    s_df = pd.read_csv(STATES_FNAME)
    c_df = pd.read_csv(COUNTIES_FNAME)
    keys = process_state_input(args.keys)
    print(keys)
    if len(keys) == 0:
        keys = sorted(list(s_df.state.unique()))
    fig, ax = plt.subplots()
    lines = [] # saves lines for use in legend
    mode = 'deaths' if args.plot_deaths else 'cases'

    # plot each state one at a time
    for key in keys:
        key_data = s_df[s_df['state'] == 'fake'].sort_values(by=['date']) # empty placeholder
        if ':' in key:
            s, c = key.split(':')[0:2]
            print('{}, {}, {}'.format(key, s, c))
            key_data = c_df[(c_df['state'] == s) & (c_df['county'] == c)].sort_values(by=['date'])
        else:
            key_data = s_df[s_df['state'] == key].sort_values(by=['date'])
        x = [date(int(d[:4]), int(d[5:7]), int(d[8:])) for d in key_data['date'].tolist()]
        y = key_data[mode].tolist()
        line, = ax.plot(x, y, marker='.')
        lines.append(line)

    # formatting plot
    ax.legend(lines, keys)
    ax.xaxis.set_major_locator(MultipleLocator(7))
    ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.tick_params(which='major', length=8, width=2)
    ax.tick_params(which='minor', length=3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    ax.yaxis.tick_right()
    ax.grid(True)
    fig.autofmt_xdate()
    plt.title('Cumulative COVID-19 {} by state'.format(mode))
    plt.show()
