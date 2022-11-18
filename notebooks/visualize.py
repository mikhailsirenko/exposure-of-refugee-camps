import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import glob
import datetime
import numpy as np
from mycolorpy import colorlist as mcp


def signaltonoise(a, axis=0, ddof=0):
    a = np.asanyarray(a)
    m = a.mean(axis)
    sd = a.std(axis=axis, ddof=ddof)
    return np.where(sd == 0, 0, m/sd)


def subplots_based_on_grid(indicator: str, abbreviation: str, units: str, plot_quintiles: bool = False) -> None:
    """Plot indicator for all countries in a grid

    Args:
        indicator (str): Indicator to plot: temperature, precipitation, etc.
        abbreviation (str): Abbreviation of the indicator: temp, precip, etc.
        units (str): Units of the indicator: C°, mm, etc.
    """

    descriptive_statistics = {}

    if indicator == 'temperature':
        weighted_average = pd.read_csv(
            '../data/processed/era5/t2m/weighted_average.csv', index_col=0)
        weighted_average.columns = pd.to_datetime(weighted_average.columns)
        ind = 't2m'
    elif indicator == 'precipitation':
        weighted_average = pd.read_csv(
            '../data/processed/era5/tp/weighted_average.csv', index_col=0)
        weighted_average.columns = pd.to_datetime(weighted_average.columns)
        weighted_average = weighted_average * 100 * 10
        ind = 'tp'
    elif indicator == 'heatwaves':
        weighted_average = pd.read_csv(
            '../data/processed/agroclimatic_indicators/wsdi/weighted_average.csv', index_col=0)
        weighted_average.columns = pd.to_datetime(weighted_average.columns)
        ind = 'wsdi'
    elif indicator == 'coldwaves':
        weighted_average = pd.read_csv(
            '../data/processed/agroclimatic_indicators/csdi/weighted_average.csv', index_col=0)
        weighted_average.columns = pd.to_datetime(weighted_average.columns)
        ind = 'csdi'
    elif indicator == 'floods':
        weighted_average = pd.read_csv(
            '../data/processed/agroclimatic_indicators/r10mm/weighted_average.csv', index_col=0)
        weighted_average.columns = pd.to_datetime(weighted_average.columns)
        ind = 'r10mm'

    # List down data files
    files = glob.glob(f"../data/processed/periodic/{indicator}/*")

    # Get country names from files
    countries = [f.split('_')[0].split('\\')[1] for f in files]

    # Get a list of colors from a specific colormap
    colors = mcp.gen_color(cmap="tab10", n=10)

    # Get a list of colors from a specific colormap
    colors = mcp.gen_color(cmap="tab10", n=10)

    # Define the attributes of the grid
    nrows = 2
    ncols = 5
    fig, ax = plt.subplots(nrows=nrows, ncols=ncols,
                           figsize=(20, 7), sharex=True, sharey=True)

    # Count country camps in data
    country_camps = {}
    n = -1

    # The number of a country to plot
    k = 0

    # Loop over rows
    for i in range(nrows):
        # Loop over columns
        for j in range(ncols):
            # Select country
            country = countries[k]

            ds = {}

            # Select file to load
            file = files[k]
            # Select color
            color = colors[k]
            # color = colors[k]
            # if k == 1:
            #     break
            # Correct country name
            if country == 'SouthSudan':
                country = 'South Sudan'

            # Load & format data
            df = pd.read_csv(file, infer_datetime_format=True)
            if indicator == 'heatwaves':
                df = df.iloc[:-3, :]
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
            national_average = df['National average']

            if plot_quintiles:
                grid = pd.read_csv(
                    f'../data/processed/era5/{ind}/{country}Grid.csv', index_col=0)
                grid.columns = pd.to_datetime(grid.columns)

            # Get camps
            n_camps = 0
            camps = []
            for column in df.columns:
                if 'Camp' in column or 'camp' in column:
                    camps.append(column)
                    n_camps += 1
            country_camps[country] = camps

            freq = 'Y'

            # Group data
            national_average = national_average.groupby(
                pd.Grouper(freq='Y')).mean()
            camp_average = df[camps].mean(axis=1)

            camp_average = camp_average.groupby(pd.Grouper(freq='Y')).mean()
            wa = weighted_average.loc[country].groupby(
                pd.Grouper(freq='Y')).mean()

            # Calculate quartiles
            if plot_quintiles:
                q1 = grid.quantile(0.25, axis=0)
                q1 = q1.groupby(pd.Grouper(freq='Y')).mean()

                q3 = grid.quantile(0.75, axis=0)
                q3 = q3.groupby(pd.Grouper(freq='Y')).mean()

            index = camp_average.index.values

            # Calculate the deviation from national average
            # delta = camp_average - national_average

            # Calculate the deviation from weighted average
            delta = camp_average - wa
            delta = delta.to_frame()
            delta.columns = ['diff']
            delta['date'] = delta.index

            # Prepare the data for plotting
            delta['date_ordinal'] = pd.to_datetime(
                delta['date']).apply(lambda date: date.toordinal())
            x = delta['date_ordinal']
            y = delta['diff']

            # Plot the deviation
            ax[i, j].plot(x, y, label=country, color=color)

            if plot_quintiles:
                # Fill between quantiles
                ax[i, j].fill_between(
                    x=x, y1=(camp_average - q1), y2=(camp_average - q3), alpha=0.25, color=color)

            # Plot regresion line
            sns.regplot(x=delta['date_ordinal'], y=delta['diff'], data=delta,
                        ax=ax[i, j],
                        scatter=False,
                        ci=None,
                        line_kws={'color': 'black', 'alpha': 1, 'lw': 0.5},
                        label='')

            # Format ticks and labels
            ax[i, j].set_xticks(x[::5])
            ax[i, j].set_xticklabels(x[::5])
            new_labels = [datetime.date.fromordinal(
                int(item)).year for item in ax[i, j].get_xticks()]
            ax[i, j].set_xticklabels(new_labels)

            # Add textbox with params of interest
            camp_mean = round(camp_average.mean(), 2)
            camp_std = round(camp_average.std(), 2)

            diff_mean = round(y.mean(), 2)
            diff_std = round(y.std(), 2)
            signal_to_noise = round(float(signaltonoise(y.fillna(0))), 2)

            for camp in camps:
                d = {}
                d['Pop. weight. average'] = wa.mean()
                d['Settl.'] = df[camp].mean()
                d['Diff.'] = df[camp].mean() - wa.mean()
                ds[camp] = d

            # textstr = f'Mean camp {abbreviation}={camp_mean} ({units}) \n\
            #             Std camp {abbreviation}={camp_std} ({units}) \n\
            #             Mean diff={diff_mean} ({units}) \n\
            #             Std diff={diff_std} ({units}) \n\
            #             SNR diff={signal_to_noise}'

            # props = dict(alpha=0.5, facecolor='white', edgecolor='black')
            # ax[i, j].annotate(text=textstr,
            #                   xy=(1.035, 1.05),
            #                   # xy=(0.885,0.45),
            #                   xytext=(-15, -15),
            #                   xycoords='axes fraction',
            #                   textcoords='offset points',
            #                   bbox=props,
            #                   fontsize=8,
            #                   verticalalignment='top',
            #                   horizontalalignment='right')

            # Fix other plot params
            ax[i, j].set_ylabel(f'Deviation from pop. weight. av. ({units})')
            ax[i, j].set_xlabel('Year')
            # ax[i, j].set_title(country)
            # ax[i, j].legend('')

            print('Number of camps in {}: {}'.format(country, n_camps))
            k += 1
            descriptive_statistics[country] = ds
    plt.savefig(f'C:/Users/Mikhail/My Drive/0 Code/exposure-refugee-camps/figures/{indicator}.pdf')

    return descriptive_statistics


def subplots_based_on_average(indicator: str, abbreviation: str, units: str) -> None:
    """Plot indicator for all countries in a grid

    Args:
        indicator (str): Indicator to plot: temperature, precipitation, etc.
        abbreviation (str): Abbreviation of the indicator: temp, precip, etc.
        units (str): Units of the indicator: C°, mm, etc.
    """

    # List down data files
    files = glob.glob(f"../data/processed/periodic/{indicator}/*")

    # Get country names from files
    countries = [f.split('_')[0].split('\\')[1] for f in files]

    # Get a list of colors from a specific colormap
    colors = mcp.gen_color(cmap="tab10", n=10)

    # Get a list of colors from a specific colormap
    colors = mcp.gen_color(cmap="tab10", n=10)

    # Define the attributes of the grid
    nrows = 2
    ncols = 5
    fig, ax = plt.subplots(nrows=nrows, ncols=ncols,
                           figsize=(18, 6), sharex=True, sharey=True)

    # Count country camps in data
    country_camps = {}
    n = -1

    # The number of a country to plot
    k = 0

    # Loop over rows
    for i in range(nrows):
        # Loop over columns
        for j in range(ncols):
            # Select country
            country = countries[k]
            # Select file to load
            file = files[k]
            # Select color
            color = colors[k]
            # color = colors[k]
            # if k == 1:
            #     break
            # Correct country name
            if country == 'SouthSudan':
                country = 'South Sudan'

            # Load & format data
            df = pd.read_csv(file, infer_datetime_format=True)
            if indicator == 'heatwaves':
                df = df.iloc[:-3, :]
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
            national_average = df['National average']

            # Get camps
            n_camps = 0
            camps = []
            for column in df.columns:
                if 'Camp' in column or 'camp' in column:
                    camps.append(column)
                    n_camps += 1
            country_camps[country] = camps

            freq = 'Y'

            # Group data
            national_average = national_average.groupby(
                pd.Grouper(freq='Y')).mean()
            camp_average = df[camps].mean(axis=1)
            camp_average = camp_average.groupby(pd.Grouper(freq='Y')).mean()

            # # Calculate quartiles
            q1 = df.drop('National average', axis=1).quantile(0.25, axis=1)
            q1 = q1.groupby(pd.Grouper(freq='Y')).mean()

            q3 = df.drop('National average', axis=1).quantile(0.75, axis=1)
            q3 = q3.groupby(pd.Grouper(freq='Y')).mean()

            index = camp_average.index.values

            # Calculate the deviation from national average
            delta = camp_average - national_average
            delta = delta.to_frame()
            delta.columns = ['diff']
            delta['date'] = delta.index

            # Prepare the data for plotting
            delta['date_ordinal'] = pd.to_datetime(
                delta['date']).apply(lambda date: date.toordinal())
            x = delta['date_ordinal']
            y = delta['diff']

            # Plot the deviation
            ax[i, j].plot(x, y, label=country, color=color)

            # Fill between quantiles
            ax[i, j].fill_between(
                x=x, y1=(camp_average - q1), y2=(camp_average - q3), alpha=0.25, color=color)

            # Plot regresion line
            sns.regplot(x=delta['date_ordinal'], y=delta['diff'], data=delta,
                        ax=ax[i, j],
                        scatter=False,
                        ci=None,
                        line_kws={'color': 'black', 'alpha': 1, 'lw': 0.5},
                        label='')

            # Format ticks and labels
            ax[i, j].set_xticks(x[::5])
            ax[i, j].set_xticklabels(x[::5])
            new_labels = [datetime.date.fromordinal(
                int(item)).year for item in ax[i, j].get_xticks()]
            ax[i, j].set_xticklabels(new_labels)

            # Add textbox with params of interest
            camp_mean = round(camp_average.mean(), 2)
            camp_std = round(camp_average.std(), 2)

            diff_mean = round(y.mean(), 2)
            diff_std = round(y.std(), 2)
            signal_to_noise = round(float(signaltonoise(y.fillna(0))), 2)

            textstr = f'Mean camp {abbreviation}={camp_mean} ({units}) \n\
                        Std camp {abbreviation}={camp_std} ({units}) \n\
                        Mean diff={diff_mean} ({units}) \n\
                        Std diff={diff_std} ({units}) \n\
                        SNR diff={signal_to_noise}'

            props = dict(alpha=0.5, facecolor='white', edgecolor='black')
            ax[i, j].annotate(text=textstr,
                              xy=(1.035, 1.05),
                              # xy=(0.885,0.45),
                              xytext=(-15, -15),
                              xycoords='axes fraction',
                              textcoords='offset points',
                              bbox=props,
                              fontsize=8,
                              verticalalignment='top',
                              horizontalalignment='right')

            # Fix other plot params
            ax[i, j].set_ylabel(f'Deviation from national average ({units})')
            ax[i, j].set_xlabel('Year')
            ax[i, j].set_title(country)
            # ax[i, j].legend('')

            print('Number of camps in {}: {}'.format(country, n_camps))
            k += 1


def single_plot(indicator: str, units: str) -> None:
    """Plot a single graph for a given indicator.

    Args:
        indicator (str): Indicator to plot.
        units (str): Units of the indicator.
    """
    # List down data files
    files = glob.glob(f"../data/processed/periodic/{indicator}/*")

    # Get country names from files
    countries = [f.split('_')[0].split('\\')[1] for f in files]
    fig, ax = plt.subplots(figsize=(8, 6))

    # Count country camps in data
    country_camps = {}
    n = -1

    colors = ['CC6677', '332288', 'DDCC77', '117733', '88CCEE',
              '882255', '44AA99', '999933', 'AA4499', 'DDDDDD']

    for country, file, color in zip(countries[:n], files[:n], colors[:n]):
        # Correct country name
        if country == 'SouthSudan':
            country = 'South Sudan'

        # Load & format data
        df = pd.read_csv(file, infer_datetime_format=True)
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)

        if indicator == 'heatwaves':
            df = df.iloc[:-3, :]

        national_average = df['National average']

        # Get camps
        n_camps = 0
        camps = []
        for column in df.columns:
            if 'Camp' in column or 'camp' in column:
                camps.append(column)
                n_camps += 1
        country_camps[country] = camps

        freq = 'Y'

        # Plot national average
        national_average = national_average.groupby(
            pd.Grouper(freq=freq)).mean()
        camp_average = df[camps].mean(axis=1)
        camp_average = camp_average.groupby(pd.Grouper(freq=freq)).mean()

        q1 = df.drop('National average', axis=1).quantile(0.25, axis=1)
        q1 = q1.groupby(pd.Grouper(freq=freq)).mean()

        q3 = df.drop('National average', axis=1).quantile(0.75, axis=1)
        q3 = q3.groupby(pd.Grouper(freq=freq)).mean()

        index = camp_average.index.values

        delta = camp_average - national_average

        # ax = camp_average.plot(label='Camp average')
        delta.plot(ax=ax, label=country, color='#' + color)
        ax.set_ylabel(f'Deviation from national average ({units})')
        ax.set_xlabel('Year')

        # national_average.plot(ax=ax, label='National average')
        # (camp_average - q1).plot(ax=ax,
        #         # label='Q1'
        #         )
        # (camp_average - q3).plot(ax=ax,
        #         # label='Q3'
        #         )
        # ax.fill_between(xmin=index[0], xmax=index[-1], ymin=q1, ymax=q3, alpha=0.5, color='red')
        # ax.fill_between(x=index, y1=(camp_average - q1), y2=(camp_average - q3), alpha=0.25, color='#' + color)
        ax.legend(frameon=True)

        print('Number of camps in {}: {}'.format(country, n_camps))
