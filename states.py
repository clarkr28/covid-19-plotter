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
COUNTIES_FNAME = 'covid-19-data/us-counties.csv'
# columns: date, county, state, fips, cases, deaths


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--states', nargs='+', help='States to display', 
        required=True, dest='states')
    return parser



def process_state_input(state_args):
    """replace state abbreviations with their full name"""

    # load the state abbreviations
    f = open(STATES_MAPPING_FNAME, 'r')
    mapping = json.load(f)
    f.close()
    # replace state abbreviations with their full name if abbreviation found
    return [mapping[entry] if entry in mapping else entry for entry in state_args]


    
if __name__ == '__main__':
    # parse arguments
    parser = create_parser()
    args = parser.parse_args()
    selected_states = process_state_input(args.states)

    df = pd.read_csv(STATES_FNAME)
    fig, ax = plt.subplots()
    lines = [] # saves lines for use in legend

    # plot each state one at a time
    for state in selected_states:
        state_data = df.loc[df['state'] == state].sort_values(by=['date'])
        x = [date(int(d[:4]), int(d[5:7]), int(d[8:])) for d in state_data['date'].tolist()]
        y = state_data['cases'].tolist()
        line, = ax.plot(x, y, marker='.')
        lines.append(line)

    # formatting plot
    ax.legend(lines, selected_states)
    ax.xaxis.set_major_locator(MultipleLocator(7))
    ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.tick_params(which='major', length=8, width=2)
    ax.tick_params(which='minor', length=3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    ax.yaxis.tick_right()
    ax.grid(True)
    fig.autofmt_xdate()
    plt.title('Cumulative COVID-19 cases by state')
    plt.show()
