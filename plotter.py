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
    parser.add_argument('-pd', '--per-day', help='plot new cases per day',
        dest='per_day', action='store_true')
    parser.add_argument('-s', '--start', help='start plotting at this day',
        default='', dest='start_date_input')
    parser.add_argument('-a', '--average', type=int, help='number of days to average',
        default=1, dest='days_to_avg')
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

    # scale default figure size
    scale = 1.5
    plt.rcParams['figure.figsize'] = [i * scale for i in plt.rcParams['figure.figsize']]

    s_df = pd.read_csv(STATES_FNAME)
    c_df = pd.read_csv(COUNTIES_FNAME)
    keys = process_state_input(args.keys)
    if len(keys) == 0:
        keys = sorted(list(s_df.state.unique()))
    fig, ax = plt.subplots()
    lines = [] # saves lines for use in legend
    labels = [] # list of labels that actually get used
    cases_or_deaths = 'deaths' if args.plot_deaths else 'cases'

    # setup starting date
    use_start_date = False
    start_date = date.today() # placeholder
    if args.start_date_input != '' and '-' in args.start_date_input:
        use_start_date = True
        m, d = args.start_date_input.split('-')[0:2]
        try:
            start_date = date(2020, int(m), int(d))
        except Exception as e:
            print('invalid start date')
            use_start_date = False

    # plot each state one at a time
    for key in keys:
        key_data = s_df[s_df['state'] == 'fake'].sort_values(by=['date']) # empty placeholder
        if ':' in key:
            s, c = key.split(':')[0:2]
            key_data = c_df[(c_df['state'] == s) & (c_df['county'] == c)].sort_values(by=['date'])
        else:
            key_data = s_df[s_df['state'] == key].sort_values(by=['date'])
        x = [date(int(d[:4]), int(d[5:7]), int(d[8:])) for d in key_data['date'].tolist()]
        y = key_data[cases_or_deaths].tolist()
        
        # skip malformed data
        if len(x) == 0 or len(y) == 0 or len(x) != len(y):
            continue

        # plot new cases per day instead of cumulative data
        if args.per_day:
            if len(y) >= 2:
                y = [y[i] - y[i-1] for i in range(1,len(y))]
                del x[0]
            else:
                continue

        # apply start date filter
        if use_start_date and start_date in x:
            i = x.index(start_date)
            x = x[i:]
            y = y[i:]

        # apply averaging and do special averaging plotting
        if args.days_to_avg > 1:
            if args.days_to_avg % 2 == 0:
                args.days_to_avg += 1
            avg_y = list()
            half = args.days_to_avg//2
            total = 0
            for i in range(half,len(y)-half):
                total = sum(y[i-half:i+half+1])
                avg_y.append(total / (half+half+1))
            # plot raw data and averaged data
            labels.append(key)
            ax.scatter(x, y, marker='.')
            line, = ax.plot(x[half:-half], avg_y)
            lines.append(line)
            # trim the dates that were not averaged because the window was not complete
            #for i in range(half):
                #del x[0]
                #del x[-1]
        else:
            # no avaraing, so apply plotting normally
            labels.append(key)
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
    totals_mode = 'New Daily' if args.per_day else 'Cumulative'
    title_str = '{} COVID-19 {}'.format(totals_mode, cases_or_deaths.capitalize())
    if args.days_to_avg > 1:
        title_str += ' ({} day avg)'.format(args.days_to_avg)
    plt.title(title_str)
    plt.show()
