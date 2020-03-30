import pandas as pd
import matplotlib.pyplot as plt
import argparse

STATES_FNAME = 'data/us-states.csv'
# columns: date, state, fips, cases, deaths
COUNTIES_FNAME = 'covid-19-data/us-counties.csv'
# columns: date, county, state, fips, cases, deaths


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--states', nargs='+', help='States to display', 
        required=True, dest='states')
    return parser

    

if __name__ == '__main__':
    # parse arguments
    parser = create_parser()
    args = parser.parse_args()

    df = pd.read_csv(STATES_FNAME)
    fig, ax = plt.subplots()
    lines = []
    for state in args.states:
        state_data = df.loc[df['state'] == state].sort_values(by=['date'])
        x = [date[6:] for date in state_data['date'].tolist()]
        y = state_data['cases'].tolist()
        line, = ax.plot(x, y)
        lines.append(line)
    ax.legend(lines, args.states)
    plt.xticks(rotation=75)
    plt.title('Cumulative COVID-19 cases by state')
    plt.show()
