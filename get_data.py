# import statements
import numpy as np
import pandas as pd
import datetime
import re
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

#ncaa_history = pd.read_csv('ncaab_history.csv')
#fin_output = pd.read_csv('ncaab_results.csv')

def get_data_ncaam(date, attributes):
    '''
    Gets the attributes for each D-1 team on the supplied date, from TeamRankings.
    :param date: Target date. String.
    :param attributes: The factors to retrieve from TeamRankings. Must match the URL exactly. Passed as a dictionary. Dictionary.
    :return: Data frame of all speficied attributes for the given date, for all teams.
    '''

    # initiate data frame
    output = pd.DataFrame({'team': []})
    # index by team name
    output = output.set_index('team')

    # for each key in the factor dictionary, create a data frame
    for attribute in list(attributes.keys()):
        # if it's a proprietary ranking, the URL is a little different
        if 'by-other' in attribute:
            # create the URL to fetch
            url = 'https://www.teamrankings.com/ncaa-basketball/ranking/' + attribute + '?date=' + date
        else:
            url = 'https://www.teamrankings.com/ncaa-basketball/stat/' + attribute + '?date=' + date

        # read the data from the table on the supplied URL
        z = pd.read_html(url, flavor='html5lib')[0]

        # throw out the nonsense
        z = z.iloc[:, 0:3]

        # ranking, team name, attribute value
        z.columns = [attribute + '_rank', 'team', attribute]

        # these throw off the regex below, so they're replaced
        z = z.replace('Miami (OH)', 'Miami_OH')
        z = z.replace('Miami (FL)', 'Miami_FL')

        # fix; clean up the team names
        if 'by-other' in attribute:
            z['team'] = ['Miami_OH' if 'Miami (OH)' in x
                         else 'Miami_FL' if 'Miami (FL' in x
            else x.split(' (')[0] for x in z['team']]

        # set the index
        z = z.set_index('team')

        # merge the attribute data frames, one by one
        output = pd.merge(z, output, how='left', on=['team'])

    # fix format to be numeric
    for column in output.columns:
        if '--' in list(output[column].unique()):
            output[column] = output[column].replace(np.nan, '--')
            output[column] = [str(x).strip('%') for x in output[column]]
            output[column] = output[column].replace('--', np.nan)
            output[column] = pd.to_numeric(output[column])
        else:
            output[column] = [str(x).strip('%') for x in output[column]]
            output[column] = output[column].replace('nan', np.nan)
            output[column] = pd.to_numeric(output[column])

    # create rankings (the TeamRankings one are broken by special characters)
    for column in output.columns:
        if 'rank' in column:
            key = column.split('_rank')[0]
            if attributes[key] == 'desc':
                output[column] = output[key].rank(ascending=False)
            else:
                output[column] = output[key].rank(ascending=True)

    # output data frame
    return output


def adjust_sos(data, sos_column, magnitude, group_columns=[]):
    '''
    Adjust the data by strength of schedule.
    :param data: The data to adjust. Data frame.
    :param sos_column: The column to use to do the strength of schedule adjustments. String.
    :param magnitude: The maximum adjustment size. Number.
    :param group_columns: Specify a group (or groups) to adjust within. List.
    :return: All columns in the data adjusted by a strength-of-schedule column.
    '''

    # if there are columns to adjust within...
    if group_columns == []:
        # rank in descending (for when team has a poor s-o-s) and ascending
        data[sos_column + '_adj_neg'] = data[sos_column].rank(pct=True)
        data[sos_column + '_adj_pos'] = data[sos_column].rank(pct=True, ascending=False)
    else:
        data[sos_column + '_adj_neg'] = data.groupby(group_columns)[sos_column].rank(pct=True)
        data[sos_column + '_adj_pos'] = data.groupby(group_columns)[sos_column].rank(pct=True, ascending=False)

    # adjust positive when the team has a strong s-o-s, else adjust negative (penalize)
    data[sos_column + '_adj'] = np.asarray([data[sos_column + '_adj_pos'][x] if data[sos_column + '_adj_pos'][x] > 0.49
                                            else -1 * data[sos_column + '_adj_neg'][x] for x in
                                            range(len(data[sos_column]))])

    # adjust by the specified magnitude
    data[sos_column + '_adj'] = data[sos_column + '_adj'] * magnitude

    # drop bloat
    data = data.drop(columns=[sos_column + '_adj_neg', sos_column + '_adj_pos'])

    # adjust all columns by specified s-o-s magnitude
    for col in data.columns:
        if 'rank' in col and col not in [sos_column, sos_column + '_adj']:
            data[col] = data[col] - data[sos_column + '_adj']

    # output the adjusted data
    return (data)


def evaluate_v2(data, teamA, teamB, magnitude=12, factor_policy={}, store=False, verbose=False, spread_target=None,
                grouping='overall'):
    teamA_stats = data.loc[teamA]

    teamB_stats = data.loc[teamB]

    ht = 0
    ht_3s = 0
    ht_2s = 0
    ht_1s = 0
    ht_half = 0
    at = 0
    at_3s = 0
    at_2s = 0
    at_1s = 0
    at_half = 0

    for factor in factor_policy.keys():

        if factor_policy[factor]['multi_fac'] != None:
            factor_good_a = factor_policy[factor]['multi_fac'][0][0]
            factor_good_b = factor_policy[factor]['multi_fac'][1][0]
            factor_bad_a = factor_policy[factor]['multi_fac'][0][1]
            factor_bad_b = factor_policy[factor]['multi_fac'][1][1]

            teamA_good_fac_a = teamA_stats[factor_good_a]
            teamA_good_fac_b = teamA_stats[factor_good_b]
            teamB_good_fac_a = teamB_stats[factor_good_a]
            teamB_good_fac_b = teamB_stats[factor_good_b]

            teamA_bad_fac_a = teamA_stats[factor_bad_a]
            teamA_bad_fac_b = teamA_stats[factor_bad_b]
            teamB_bad_fac_a = teamB_stats[factor_bad_a]
            teamB_bad_fac_b = teamB_stats[factor_bad_b]

            teamA_status = (teamB_bad_fac_a - teamA_good_fac_a) - (teamA_bad_fac_b - teamB_good_fac_a)
            teamB_status = (teamA_bad_fac_b - teamB_good_fac_a) - (teamB_bad_fac_a - teamA_good_fac_a)

            if factor_policy[factor]["three_points"] != None:
                if teamA_status > factor_policy[factor]["three_points"][0]:
                    ht += 3
                    ht_3s += 1
                    if verbose == True:
                        print(teamA + " has a +3 advantage on " + factor)
                elif teamA_status > factor_policy[factor]["two_points"][0]:
                    ht += 2
                    ht_2s += 1
                    if verbose == True:
                        print(teamA + " has a +2 advantage on " + factor)
                elif teamA_status > factor_policy[factor]["one_point"][0]:
                    ht += 1
                    ht_1s += 1
                    if verbose == True:
                        print(teamA + " has a +1 advantage on " + factor)
                elif teamA_status > magnitude:
                    ht += 0.5
                    ht_half += 1
                    if verbose == True:
                        print(teamA + " has a +0.5 advantage on " + factor)
                else:
                    ht += 0

                if teamB_status > factor_policy[factor]["three_points"][0]:
                    at += 3
                    at_3s += 1
                    if verbose == True:
                        print(teamB + " has a +3 advantage on " + factor)
                elif teamB_status > factor_policy[factor]["two_points"][0]:
                    at += 2
                    at_2s += 1
                    if verbose == True:
                        print(teamB + " has a +2 advantage on " + factor)
                elif teamB_status > factor_policy[factor]["one_point"][0]:
                    at += 1
                    at_1s += 1
                    if verbose == True:
                        print(teamB + " has a +1 advantage on " + factor)
                elif teamB_status > magnitude:
                    at += 0.5
                    at_half += 1
                    if verbose == True:
                        print(teamB + " has a +0.5 advantage on " + factor)
                else:
                    at += 0


        elif factor_policy[factor]['two_fac'] != None:
            factor_good = factor_policy[factor]['two_fac'][0]
            factor_bad = factor_policy[factor]['two_fac'][1]

            teamA_good_fac = teamA_stats[factor_good]
            teamB_good_fac = teamB_stats[factor_good]
            teamA_bad_fac = teamA_stats[factor_bad]
            teamB_bad_fac = teamB_stats[factor_bad]

            teamA_status = teamB_bad_fac - teamA_good_fac
            teamB_status = teamA_bad_fac - teamB_good_fac

            if factor_policy[factor]["three_points"] != None:
                if teamA_status > factor_policy[factor]["three_points"][0]:
                    ht += 3
                    ht_3s += 1
                    if verbose == True:
                        print(teamA + " has a +3 advantage on " + factor)
                elif teamA_status > factor_policy[factor]["two_points"][0]:
                    ht += 2
                    ht_2s += 1
                    if verbose == True:
                        print(teamA + " has a +2 advantage on " + factor)
                elif teamA_status > factor_policy[factor]["one_point"][0]:
                    ht += 1
                    ht_1s += 1
                    if verbose == True:
                        print(teamA + " has a +1 advantage on " + factor)
                elif teamA_status > magnitude:
                    ht += 0.5
                    ht_half += 1
                    if verbose == True:
                        print(teamA + " has a +0.5 advantage on " + factor)
                else:
                    ht += 0

                if teamB_status > factor_policy[factor]["three_points"][0]:
                    at += 3
                    at_3s += 1
                    if verbose == True:
                        print(teamB + " has a +3 advantage on " + factor)
                elif teamB_status > factor_policy[factor]["two_points"][0]:
                    at += 2
                    at_2s += 1
                    if verbose == True:
                        print(teamB + " has a +2 advantage on " + factor)
                elif teamB_status > factor_policy[factor]["one_point"][0]:
                    at += 1
                    at_1s += 1
                    if verbose == True:
                        print(teamB + " has a +1 advantage on " + factor)
                elif teamB_status > magnitude:
                    at += 0.5
                    at_half += 1
                    if verbose == True:
                        print(teamB + " has a +0.5 advantage on " + factor)
                else:
                    at += 0

            else:
                if teamA_status > factor_policy[factor]["two_points"][0]:
                    ht += 2
                    ht_2s += 1
                    if verbose == True:
                        print(teamA + " has a +2 advantage on " + factor)
                elif teamA_status > factor_policy[factor]["one_point"][0]:
                    ht += 1
                    ht_1s += 1
                    if verbose == True:
                        print(teamA + " has a +1 advantage on " + factor)
                elif teamA_status > magnitude:
                    ht += 0.5
                    ht_half += 1
                    if verbose == True:
                        print(teamA + " has a +0.5 advantage on " + factor)
                else:
                    ht += 0

                if teamB_status > factor_policy[factor]["two_points"][0]:
                    at += 2
                    at_2s += 1
                    if verbose == True:
                        print(teamB + " has a +2 advantage on " + factor)
                elif teamB_status > factor_policy[factor]["one_point"][0]:
                    at += 1
                    at_1s += 1
                    if verbose == True:
                        print(teamB + " has a +1 advantage on " + factor)
                elif teamB_status > magnitude:
                    at += 0.5
                    at_half += 1
                    if verbose == True:
                        print(teamB + " has a +0.5 advantage on " + factor)
                else:
                    at += 0

        else:

            teamA_status = teamB_stats[factor] - teamA_stats[factor]
            teamB_status = teamA_stats[factor] - teamB_stats[factor]

            if factor_policy[factor]["three_points"] != None:
                if teamA_status > factor_policy[factor]["three_points"][0]:
                    ht += 3
                    ht_3s += 1
                    if verbose == True:
                        print(teamA + " has a +3 advantage on " + factor)
                elif teamA_status > factor_policy[factor]["two_points"][0]:
                    ht += 2
                    ht_2s += 1
                    if verbose == True:
                        print(teamA + " has a +2 advantage on " + factor)
                elif teamA_status > factor_policy[factor]["one_point"][0]:
                    ht += 1
                    ht_1s += 1
                    if verbose == True:
                        print(teamA + " has a +1 advantage on " + factor)
                elif teamA_status > magnitude:
                    ht += 0.5
                    ht_half += 1
                    if verbose == True:
                        print(teamA + " has a +0.5 advantage on " + factor)
                else:
                    ht += 0

                if teamB_status > factor_policy[factor]["three_points"][0]:
                    at += 3
                    at_3s += 1
                    if verbose == True:
                        print(teamB + " has a +3 advantage on " + factor)
                elif teamB_status > factor_policy[factor]["two_points"][0]:
                    at += 2
                    at_2s += 1
                    if verbose == True:
                        print(teamB + " has a +2 advantage on " + factor)
                elif teamB_status > factor_policy[factor]["one_point"][0]:
                    at += 1
                    at_1s += 1
                    if verbose == True:
                        print(teamB + " has a +1 advantage on " + factor)
                elif teamB_status > magnitude:
                    at += 0.5
                    at_half += 1
                    if verbose == True:
                        print(teamB + " has a +0.5 advantage on " + factor)
                else:
                    at += 0

            else:
                if teamA_status > factor_policy[factor]["two_points"][0]:
                    ht += 2
                    ht_2s += 1
                    if verbose == True:
                        print(teamA + " has a +2 advantage on " + factor)
                elif teamA_status > factor_policy[factor]["one_point"][0]:
                    ht += 1
                    ht_1s += 1
                    if verbose == True:
                        print(teamA + " has a +1 advantage on " + factor)
                elif teamA_status > magnitude:
                    ht += 0.5
                    ht_half += 1
                    if verbose == True:
                        print(teamA + " has a +0.5 advantage on " + factor)
                else:
                    ht += 0

                if teamB_status > factor_policy[factor]["two_points"][0]:
                    at += 2
                    at_2s += 1
                    if verbose == True:
                        print(teamB + " has a +2 advantage on " + factor)
                elif teamB_status > factor_policy[factor]["one_point"][0]:
                    at += 1
                    at_1s += 1
                    if verbose == True:
                        print(teamB + " has a +1 advantage on " + factor)
                elif teamB_status > magnitude:
                    at += 0.5
                    at_half += 1
                    if verbose == True:
                        print(teamB + " has a +0.5 advantage on " + factor)
                else:
                    at += 0

    if ht > at:
        print(teamA, " is likely to win, with a score of ", str(ht - at))

    elif ht < at:
        print(teamB, " is likely to win, with a score of ", str(at - ht))

    else:
        print("Neither team has a clear advantage.")

    if store == True:
        if grouping == 'overall':
            if ht > at:
                return ([ht, at, ht - at, teamA])
            elif at > ht:
                return ([at, ht, at - ht, teamB])
            else:
                return ([ht, at, ht - at, 'Neither'])

        elif grouping == 'threes':
            if ht_3s > at_3s:
                return ([ht - at, ht_3s - at_3s, ht_2s - at_2s, ht_1s - at_1s, ht_half - at_half, teamA])
            elif at_3s > ht_3s:
                return ([at - ht, at_3s - ht_3s, at_2s - ht_2s, at_1s - ht_1s, at_half - ht_half, teamB])
            else:
                return ([ht - at, ht_3s - at_3s, ht_2s - at_2s, ht_1s - at_1s, ht_half - at_half, 'Neither'])

        elif grouping == 'twos':
            if ht_2s > at_2s:
                return ([ht - at, ht_3s - at_3s, ht_2s - at_2s, ht_1s - at_1s, ht_half - at_half, teamA])
            elif at_2s > ht_2s:
                return ([at - ht, at_3s - ht_3s, at_2s - ht_2s, at_1s - ht_1s, at_half - ht_half, teamB])
            else:
                return ([ht - at, ht_3s - at_3s, ht_2s - at_2s, ht_1s - at_1s, ht_half - at_half, 'Neither'])

        elif grouping == 'ones':
            if ht_1s > at_1s:
                return ([ht - at, ht_3s - at_3s, ht_2s - at_2s, ht_1s - at_1s, ht_half - at_half, teamA])
            elif at_1s > ht_1s:
                return ([at - ht, at_3s - ht_3s, at_2s - ht_2s, at_1s - ht_1s, at_half - ht_half, teamB])
            else:
                return ([ht - at, ht_3s - at_3s, ht_2s - at_2s, ht_1s - at_1s, ht_half - at_half, 'Neither'])

        elif grouping == 'half':
            if ht_half > at_half:
                return ([ht - at, ht_3s - at_3s, ht_2s - at_2s, ht_1s - at_1s, ht_half - at_half, teamA])
            elif at_half > ht_half:
                return ([at - ht, at_3s - ht_3s, at_2s - ht_2s, at_1s - ht_1s, at_half - ht_half, teamB])
            else:
                return ([ht - at, ht_3s - at_3s, ht_2s - at_2s, ht_1s - at_1s, ht_half - at_half, 'Neither'])

    if spread_target != None:
        spread_df = spread_target[0]
        zz = 0
        if ht > at:
            diff = ht - at
        elif at > ht:
            diff = at - ht
        else:
            zz = 1
            diff = 0

        found = False
        row = 0
        while found == False:
            if zz == 1:
                found = True
            if (diff >= spread_df.loc[row, 'min']) and (diff <= spread_df.loc[row, 'max']):
                print("No-Brainer: " + str(-1 * spread_df.loc[row, '25%']),
                      ", Good Bet: " + str(-1 * spread_df.loc[row, '40%']),
                      ", Chance: " + str(-1 * spread_df.loc[row, '50%']))
                print("No-Brainer Fade: " + str(-1 * spread_df.loc[row, '90%']),
                      "Good Fade: " + str(-1 * spread_df.loc[row, '75%']))
                found = True
            else:
                row += 1


def evaluate(data, teamA, teamB, size, store=False):
    teamA_stats = data.loc[teamA]

    teamB_stats = data.loc[teamB]

    ht = 0
    at = 0

    # Passing Offense - Home Team
    if teamA_stats['yards-per-pass-attempt_rank'] + size < teamB_stats['opponent-yards-per-pass-attempt_rank']:
        print(teamA, " has an advantage passing against the ", teamB, " defense. (YPP/Rank: ",
              str(teamA_stats['yards-per-pass-attempt']), '/', str(teamA_stats['yards-per-pass-attempt_rank']),
              " vs Defense's YPP/Rank: ", str(teamB_stats['opponent-yards-per-pass-attempt']),
              str(teamB_stats['opponent-yards-per-pass-attempt_rank']))

        ht += 1

    elif teamB_stats['opponent-yards-per-pass-attempt_rank'] + size < teamA_stats['yards-per-pass-attempt_rank']:
        print(teamB, " has an advantage DEFENDING the pass against the ", teamA, " offense. (Defense YPP/Rank: ",
              str(teamB_stats['opponent-yards-per-pass-attempt']), '/',
              str(teamB_stats['opponent-yards-per-pass-attempt_rank']), " vs Opponent YPP/Rank: ",
              str(teamA_stats['yards-per-pass-attempt']), str(teamA_stats['yards-per-pass-attempt_rank']))

        at += 1

    else:
        a = 0
        # print("Neither team has an advantage when", teamA, "passes.")

    # Passing Offense - Away Team
    if teamB_stats['yards-per-pass-attempt_rank'] + size < teamA_stats['opponent-yards-per-pass-attempt_rank']:
        print(teamB, " has an advantage passing against the ", teamA, " defense. (YPP/Rank: ",
              str(teamB_stats['yards-per-pass-attempt']), '/', str(teamB_stats['yards-per-pass-attempt_rank']),
              " vs Defense's YPP/Rank: ", str(teamA_stats['opponent-yards-per-pass-attempt']),
              str(teamA_stats['opponent-yards-per-pass-attempt_rank']))

        at += 1

    elif teamA_stats['opponent-yards-per-pass-attempt_rank'] + size < teamB_stats['yards-per-pass-attempt_rank']:
        print(teamA, " has an advantage DEFENDING the pass against the ", teamB, " offense. (Defense YPP/Rank: ",
              str(teamA_stats['opponent-yards-per-pass-attempt']), '/',
              str(teamA_stats['opponent-yards-per-pass-attempt_rank']), " vs Opponent YPP/Rank: ",
              str(teamB_stats['yards-per-pass-attempt']), str(teamB_stats['yards-per-pass-attempt_rank']))

        ht += 1

    else:
        a = 0
        # print("Neither team has an advantage when", teamB, "passes.")

    # Rushing Offense - Home Team
    if teamA_stats['yards-per-rush-attempt_rank'] + size < teamB_stats['opponent-yards-per-rush-attempt_rank']:
        print(teamA, " has an advantage rushing against the ", teamB, " defense. (YPP/Rank: ",
              str(teamA_stats['yards-per-rush-attempt']), '/', str(teamA_stats['yards-per-rush-attempt_rank']),
              " vs Defense's YPP/Rank: ", str(teamB_stats['opponent-yards-per-rush-attempt']),
              str(teamB_stats['opponent-yards-per-rush-attempt_rank']))

        ht += 1

    elif teamB_stats['opponent-yards-per-rush-attempt_rank'] + size < teamA_stats['yards-per-rush-attempt_rank']:
        print(teamB, " has an advantage DEFENDING the rush against the ", teamA, " offense. (Defense YPP/Rank: ",
              str(teamB_stats['opponent-yards-per-rush-attempt']), '/',
              str(teamB_stats['opponent-yards-per-rush-attempt_rank']), " vs Opponent YPP/Rank: ",
              str(teamA_stats['yards-per-rush-attempt']), str(teamA_stats['yards-per-rush-attempt_rank']))

        at += 1

    else:
        a = 0
        # print("Neither team has an advantage when", teamA, "rushes.")

    # Rushing Offense - Away Team
    if teamB_stats['yards-per-rush-attempt_rank'] + size < teamA_stats['opponent-yards-per-rush-attempt_rank']:
        print(teamB, " has an advantage rushing against the ", teamA, " defense. (YPP/Rank: ",
              str(teamB_stats['yards-per-rush-attempt']), '/', str(teamB_stats['yards-per-rush-attempt_rank']),
              " vs Defense's YPP/Rank: ", str(teamA_stats['opponent-yards-per-rush-attempt']),
              str(teamA_stats['opponent-yards-per-rush-attempt_rank']))

        at += 1

    elif teamA_stats['opponent-yards-per-rush-attempt_rank'] + size < teamB_stats['yards-per-rush-attempt_rank']:
        print(teamA, " has an advantage DEFENDING the rush against the ", teamB, " offense. (Defense YPP/Rank: ",
              str(teamA_stats['opponent-yards-per-rush-attempt']), '/',
              str(teamA_stats['opponent-yards-per-rush-attempt_rank']), " vs Opponent YPP/Rank: ",
              str(teamB_stats['yards-per-rush-attempt']), str(teamB_stats['yards-per-rush-attempt_rank']))

        ht += 1

    else:
        a = 0
        # print("Neither team has an advantage when", teamB, "rushes.")

    # Total Offense - Home Team
    if teamA_stats['offensive-points-per-game_rank'] + size < teamB_stats['opponent-offensive-points-per-game_rank']:
        print(teamA, " has an overall offensive advantage against the ", teamB, " defense. (OPPG/Rank: ",
              str(teamA_stats['offensive-points-per-game']), '/', str(teamA_stats['offensive-points-per-game_rank']),
              " vs Defense's OPPG/Rank: ", str(teamB_stats['opponent-offensive-points-per-game']),
              str(teamB_stats['opponent-offensive-points-per-game_rank']))

        ht += 1

    elif teamB_stats['opponent-offensive-points-per-game_rank'] + size < teamA_stats['offensive-points-per-game_rank']:
        print(teamB, " has an overall advantage DEFENDING against the ", teamA, " offense. (Defense OPPG/Rank: ",
              str(teamB_stats['opponent-offensive-points-per-game']), '/',
              str(teamB_stats['opponent-offensive-points-per-game_rank']), " vs Opponent OPPG/Rank: ",
              str(teamA_stats['offensive-points-per-game']), str(teamA_stats['offensive-points-per-game_rank']))

        at += 1

    else:
        a = 0
        # print("Neither team has an overall advantage when", teamA, "is on offense.")

    # Total Offense - Away Team
    if teamB_stats['offensive-points-per-game_rank'] + size < teamA_stats['opponent-offensive-points-per-game_rank']:
        print(teamB, " has an overall offensive advantage against the ", teamA, " defense. (OPPG/Rank: ",
              str(teamB_stats['offensive-points-per-game']), '/', str(teamB_stats['offensive-points-per-game_rank']),
              " vs Defense's OPPG/Rank: ", str(teamA_stats['opponent-offensive-points-per-game']),
              str(teamA_stats['opponent-offensive-points-per-game_rank']))

        at += 1

    elif teamA_stats['opponent-offensive-points-per-game_rank'] + size < teamB_stats['offensive-points-per-game_rank']:
        print(teamA, " has an overall advantage DEFENDING against the ", teamB, " offense. (Defense OPPG/Rank: ",
              str(teamA_stats['opponent-offensive-points-per-game']), '/',
              str(teamA_stats['opponent-offensive-points-per-game_rank']), " vs Opponent OPPG/Rank: ",
              str(teamB_stats['offensive-points-per-game']), str(teamB_stats['offensive-points-per-game_rank']))

        ht += 1

    else:
        a = 0
        # print("Neither team has an overall advantage when", teamB, "is on offense.")

    # Turnovers
    if teamA_stats['turnover-margin-per-game_rank'] + size < teamB_stats['turnover-margin-per-game_rank']:
        print(teamA, "has the turnover advantage against ", teamB, ". (TOMPG/Rank: ",
              str(teamA_stats['turnover-margin-per-game']), '/', str(teamA_stats['turnover-margin-per-game_rank']),
              " vs Opponent TOMPG/Rank: ", str(teamB_stats['turnover-margin-per-game']),
              str(teamB_stats['turnover-margin-per-game_rank']))

        ht += 1

    elif teamB_stats['turnover-margin-per-game_rank'] + size < teamA_stats['turnover-margin-per-game_rank']:
        print(teamB, "has the turnover advantage against ", teamA, ". (TOMPG/Rank: ",
              str(teamB_stats['turnover-margin-per-game']), '/',
              str(teamB_stats['turnover-margin-per-game_rank']), " vs Opponent TOMPG/Rank: ",
              str(teamA_stats['turnover-margin-per-game']), str(teamA_stats['turnover-margin-per-game_rank']))

        at += 1

    else:
        a = 0
        # print("Neither team has a turnover advantage.")

    # TeamRankings Rank
    if teamA_stats['predictive-by-other_rank'] < teamB_stats['predictive-by-other_rank']:
        print(teamA, " has a better TR rating than", teamB, ". (Rating/Rank: ",
              str(teamA_stats['predictive-by-other']), '/', str(teamA_stats['predictive-by-other_rank']),
              " vs Opponent Rating/Rank: ", str(teamB_stats['predictive-by-other']),
              str(teamB_stats['predictive-by-other_rank']))

        ht += 1

    else:
        print(teamB, " has a better TR rating than ", teamA, ". (Rating/Rank: ",
              str(teamB_stats['predictive-by-other']), '/',
              str(teamB_stats['predictive-by-other_rank']), " vs Opponent Rating/Rank: ",
              str(teamA_stats['predictive-by-other']), str(teamA_stats['predictive-by-other_rank']))

        at += 1

    if ht > at:
        print(teamA, " is likely to win, with a score of ", str(ht - at), " (on a scale of -8 to 8)")

    elif ht < at:
        print(teamB, " is likely to win, with a score of ", str(at - ht), " (on a scale of -8 to 8)")

    else:
        print("Neither team has a clear advantage.")

    if store == True:
        if ht > at:
            return ([ht, at, ht - at, teamA])
        elif at > ht:
            return ([at, ht, at - ht, teamB])
        else:
            return ([ht, at, ht - at, 'Neither'])


def get_ncaa_schedule(date):
    z = pd.read_html('https://www.teamrankings.com/ncb/schedules/' + '?date=' + date, flavor='html5lib')[
        0]

    z.columns = ['Drop', 'Drop_2', 'Teams', 'Drop_3', 'Drop_4']

    z = z[['Teams']]

    z[['Away Team', 'Home Team']] = z['Teams'].str.split(" vs.| at", n=1, expand=True)
    z['Away Team'] = [re.sub('[0-9]+', '', x.strip('#')).strip() for x in z['Away Team']]
    z['Home Team'] = [re.sub('[0-9]+', '', x.strip(' #')).strip() if x != None else None for x in z['Home Team']]

    z = z.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    z = z.replace('Miami (OH)', 'Miami_OH')
    z = z.replace('Miami (FL)', 'Miami_FL')

    z = z[['Away Team', 'Home Team']]

    return (z)


def get_historical_ncaa_data(start_dates, start_week, attributes):
    df_list = []

    for start_date in start_dates:
        date_list = []
        for x in range(22):
            original_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            next_date_to_add = original_date + datetime.timedelta(days=7 * x)
            next_date_to_add = next_date_to_add.strftime('%Y-%m-%d')
            date_list.append(next_date_to_add)

        start_week_go = start_week
        for date in date_list:
            print(date)
            try:
                to_concat = get_data_ncaam(date, attributes)
            except:
                new_date = datetime.datetime.strptime(date, '%Y-%m-%d')
                new_date = new_date + datetime.timedelta(days=1)
                new_date = new_date.strftime('%Y-%m-%d')
                print(new_date)
                to_concat = get_data_ncaam(new_date, attributes)

            to_concat['Week'] = start_week_go
            to_concat['Year'] = date[0:4]
            to_concat['Date'] = date

            df_list.append(to_concat)

            start_week_go += 1

    output = pd.concat(df_list)

    output['Week'] = output['Week'].astype('int32')
    output['Year'] = output['Year'].astype('int32')

    return (output)


proper_names = {"APSU" : "Austian Peay",
                "AR Lit Rock" : "Arkansas Little Rock",
                "ARK" : "Arkansas",
                "AUB" : "Auburn",
                "Abl Christian" : "Abilene Christian",
                "Alab A&M" : "Alabama A&M",
                "Alabama Crimson" : "Alabama",
                "Alabama St" : "Alabama State",
                "Albany NY" : "Albany",
                "App State" : "Appalachian State",
                "Appalachian St" : "Appalachian State",
                "Arizona St" : "Arizona State",
                "Arizona U" : "Arizona",
                "Ark Pine Bl" : "Arkansas Pine Bluff",
                "Ark Pine Bluff" : "Arkansas Pine Bluff",
                "Arkansas LR" : "Arkansas Little Rock",
                "Arkansas St" : "Arkansas State",
                "Arkansas State Red" : "Arkansas State",
                "BC" : "Boston College",
                "BEL" : "Belmont",
                "BGSU" : "Bowling Green State",
                "BUT" : "Butler",
                "BYU" : "Brigham Young",
                "Beth-Cook" : "Bethune Cookman",
                "Boston Col" : "Boston College",
                "Boston U" : "Boston University",
                "Bowling Green" : "Bowling Green State",
                "Bowling Grn" : "Bowling Green State",
                "Buffalo U" : "Buffalo",
                "CONN" : "Connecticut",
                "CS Bakersfld" : "California State Bakersfield",
                "CS Fullerton" : "California State Fullerton",
                "CSBakerfield" : "California State Bakersfield",
                "CSFullerton" : "California State Fullerton",
                "CSNorthridge" : "California State Northridge",
                "CSSan Bernardino" : "California State San Bernardino",
                "CSU" : "Coppin State",
                "Cal Baptist" : "California Baptist",
                "Cal Irvine" : "California Irvine",
                "Cal Poly" : "California Polytechnic",
                "Cal Poly SLO" : "Califoria Polytechnic",
                "Cal Riverside" : "California Riverside",
                "Cal Santa Barb" : "California Santa Barbara",
                "Cal Santa Barbara" : "California Santa Barbara",
                "Cal St Nrdge" : "California State Northridge",
                "California Golden" : "California",
                "Central Ark" : "Central Arkansas",
                "Central Conn" : "Central Connecticut",
                "Central FL" : "Central Florida",
                "Central Mich" : "Central Michigan",
                "Central Missouri St" : "Central Missouri State",
                "Charl South" : "Charleston Southern",
                "Charlotte U" : "Charlotte",
                "Chiago St" : "Chicago State",
                "Cincinnati U" : "Cincinnati",
                "Citadel" : "The Citadel",
                "Cleveland St" : "Cleveland State",
                "Coastal Car" : "Coastal Carolina",
                "Col Charlestn" : "College of Charleston",
                "Coll Charleston" : "College of Charleston",
                "Colorado St" : "Colorado State",
                "Colorado St." : "Colorado State",
                "DAV" : "Davidson",
                "DAY" : "Dayton",
                "DEP" : "Depaul",
                "DSU" : "Delaware State",
                "DUQ" : "Duquesne",
                "Delaware St" : "Delaware State",
                "Denver U" : "Denver",
                "Detroit U" : "Detroit",
                "Duke Blue" : "Duke",
                "E Carolina" : "East Carolina",
                "E Illinois" : "Eastern Illinois",
                "E Kentucky" : "Eastern Kentucky",
                "E Michigan" : "Eastern Michigan",
                "E Tenn St" : "East Tennessee State",
                "E.Washington" : "Eastern Washington",
                "EIU" : "Eastern Illinois",
                "EKU" : "Eastern Kentucky",
                "ETSU" : "East Tennessee State",
                "ETennessee St" : "East Tennessee State",
                "East Tenn St" : "East Tennessee State",
                "Eastern Wash" : "Eastern Washington",
                "F Dickinson" : "Fairleigh Dickinson",
                "FLA" : "Florida",
                "FOR" : "Fordham",
                "FRES" : "Fresno State",
                "FUR" : "Furman",
                "Fair Dickinson" : "Fairleigh Dickinson",
                "Fla Atlantic" : "Florida Atlantic",
                "Fla Gulf Coast" : "Florida Gulf Coast",
                "Fla Gulf Cst" : "Florida Gulf Coast",
                "Florida AM" : "Florida A&M",
                "Florida Intl" : "Florida International",
                "Florida St" : "Florida State",
                "Fresno St" : "Fresno State",
                "GA Southern" : "Georgia Southern",
                "GA Tech" : "Georgia Tech",
                "GMU" : "George Mason",
                "GT" : "Georgia Tech",
                "GW" : "George Washington",
                "Gard-Webb" : "Gardner Webb",
                "Geo Mason" : "George Mason",
                "Geo Washington" : "George Washington",
                "Geo Wshgtn" : "George Washington",
                "Georgia St" : "Georgia State",
                "Georgia Tech Yellow" : "Georgia Tech",
                "Grambling St" : "Grambling",
                "Grd Canyon" : "Grand Canyon",
                "HALL" : "Seton Hall",
                "Hawai'i Rainbow" : "Hawaii",
                "Houston Bap" : "Houston Baptist",
                "Houston U" : "Houston",
                "IL-Chicago" : "Illinois Chicago",
                "IU" : "Indiana",
                "Idaho U" : "Idaho",
                "Illinois Fighting" : "Illinois",
                "Illinois St" : "Illinois State",
                "Incar Word" : "Incarnate Word",
                "Indiana St" : "Indiana State",
                "Indiana U" : "Indiana",
                "JOES" : "Saint Josephs",
                "JVST" : "Jacksonville State",
                "Jackson St" : "Jackson State",
                "Jackson St." : "Jackson State",
                "Jacksonville St." : "Jacksonville State",
                "James Mad" : "James Madison",
                "Jksnville St" : "Jacksonville State",
                "Kansas St" : "Kansas State",
                "Kennesaw St" : "Kennesaw State",
                "Kent St." : "Kent State",
                "Kent State Golden" : "Kent State",
                "LA Lafayette" : "Louisiana",
                "LA Monroe" : "Louisiana-Monroe",
                "LA Tech" : "Louisiana Tech",
                "LAS" : "La Salle",
                "LIU" : "Long Island",
                "LSU" : "Louisiana State",
                "Lafayette" : "Louisiana",
                "Lg Beach St" : "Long Beach State",
                "Louisiana Ragin'" : "Louisiana",
                "Loyola Mymt" : "Loyola Marymount",
                "Loyola-Chi" : "Loyola Chicago",
                "Loyola-MD" : "Loyola Maryland",
                "MAN" : "Manhattan",
                "MASS" : "Massachusetts",
                "MDEastern Shore" : "Maryland Eastern Shore",
                "MIZ" : "Missouri",
                "MSST" : "Mississippi State",
                "MUR" : "Murray State",
                "Maryland BC" : "UMBC",
                "Maryland ES" : "Maryland Eastern Shore",
                "Mc Neese State" : "McNeese State",
                "McNeese St" : "McNeese State",
                "Memphis U" : "Memphis",
                "Miami (OH)" : "Miami_OH",
                "Miami Florida" : "Miami_FL",
                "Miami Ohio" : "Miami_OH",
                "Michigan St" : "Michigan State",
                "Michigan St." : "Michigan State",
                "Mid Tennessee State" : "Middle Tennessee State",
                "Middle Tenn" : "Middle Tennessee State",
                "Middle Tenn St" : "Middle Tennessee State",
                "Middle Tennessee Blue" : "Middle Tennessee State",
                "Minnesota U" : "Minnesota",
                "Miss State" : "Mississippi State",
                "Miss Val St" : "Mississippi Valley State",
                "Miss Valley St" : "Mississippi Valley State",
                "Mississippi St" : "Mississippi State",
                "Missouri St" : "Missouri State",
                "Montana St" : "Montana State",
                "Morehead St" : "Morehead State",
                "Morgan St" : "Morgan State",
                "Mount St Marys" : "Mount Saint Marys",
                "Mt St Marys" : "Mount Saint Marys",
                "Mt.St.Mary's" : "Mount Saint Marys",
                "Murray St" : "Murray State",
                "N Alabama" : "North Alabama",
                "N Arizona" : "Northern Arizona",
                "N Carolina" : "North Carolina",
                "N Colorado" : "Northern Colorado",
                "N Dakota St" : "North Dakota State",
                "N Florida" : "North Florida",
                "N Hampshire" : "New Hampshire",
                "N Illinois" : "Northern Illinois",
                "N Iowa" : "Northern Iowa",
                "N Kentucky" : "Northern Kentucky",
                "N Mex State" : "New Mexico State",
                "N.Carolina A&T" : "North Carolina A&T",
                "NC A&T" : "North Carolina A&T",
                "NC Central" : "North Carolina Central",
                "NC ST" : "North Carolina State",
                "NCST" : "North Carolina State",
                "NC State" : "North Carolina State",
                "NC-Asheville" : "North Carolina Asheville",
                "NC-Grnsboro" : "North Carolina Greensboro",
                "NC-Wilmgton" : "North Carolina Wilmington",
                "NCAsheville" : "North Carolina Asheville",
                "NCCentral" : "North Carolina Central",
                "NCCharlotte" : "North Carolina Charlotte",
                "NCGreensboro" : "North Carolina Greensboro",
                "NCState" : "North Carolina State",
                "NCWilmington" : "North Carolina Wilmington",
                "ND" : "Notre Dame",
                "NDakota St" : "North Dakota State",
                "NEB" : "Nebraska",
                "NO Illinois" : "Northern Illinois",
                "NW State" : "Northwestern State",
                "Neb Omaha" : "Nebraska Omaha",
                "Nevada Wolf" : "Nevada",
                "New Orleans U" : "New Orleans",
                "Nicholls St" : "Nicholls State",
                "No.Colorado" : "Northern Colorado",
                "Norfolk St" : "Norfolk State",
                "North Carolina AT" : "North Carolina A&T",
                "North Carolina Tar" : "North Carolina",
                "North Dakota St" : "North Dakota State",
                "North Texas Mean" : "North Texas",
                "Northwestern St" : "Northwestern State",
                "Notre Dame Fighting" : "Notre Dame",
                "OHIO" : "Ohio",
                "OSU" : "Ohio State",
                "Ohio St." : "Ohio State",
                "Oklahoma St" : "Oklahoma State",
                "Ole Miss" : "Mississippi",
                "Oregon St" : "Oregon State",
                "Oregon St." : "Oregon State",
                "PORT" : "Portland",
                "PROV" : "Providence",
                "PSU" : "Penn State",
                "Penn" : "Pennsylvania",
                "Penn State Nittany" : "Penn State",
                "Pittsburgh U" : "Pittsburgh",
                "Portland St" : "Portland State",
                "Portland U" : "Portland",
                "Prairie View" : "Prairie View A&M",
                "Prairie View AM" : "Prairie View A&M",
                "RICH" : "Richmond",
                "Rob Morris" : "Robert Morris",
                "Rutgers Scarlet" : "Rutgers",
                "S Alabama" : "South Alabama",
                "S Car State" : "South Carolina State",
                "S Carolina" : "South Carolina",
                "S Dakota St" : "South Dakota State",
                "S Florida" : "South Florida",
                "S Illinois" : "Southern Illinois",
                "S Methodist" : "Southern Methodist",
                "S Mississippi" : "Southern Mississippi",
                "S Utah" : "Southern Utah",
                "SAC" : "Sacramento State",
                "SAM" : "Sam Houston State",
                "SBU" : "Saint Bonaventure",
                "SC Upstate" : "South Carolina Upstate",
                "SCUpstate" : "South Carolina Upstate",
                "SE Louisiana" : "Southeastern Louisiana",
                "SE Missouri" : "Southeastern Missouri",
                "SEA" : "Seattle",
                "SEMO" : "Southeast Missouri State",
                "SEMissouri St" : "Southeast Missouri State",
                "SEMissouri St." : "Southeast Missouri State",
                "SLU" : "Saint Louis",
                "SMC" : "Saint Marys",
                "SMU" : "Southern Methodist",
                "Sac State" : "Sacramento State",
                "Sacred Hrt" : "Sacred Heart",
                "Saint Marys CA" : "Saint Marys",
                "Saint Marys-CA" : "Saint Marys",
                "Sam Hous St" : "Sam Houston State",
                "Sam Houston" : "Sam Houston State",
                "Sam Houston St" : "Sam Houston State",
                "San Diego St" : "San Diego State",
                "San Fransco" : "San Francisco",
                "San Jose St" : "San Jose State",
                "San José State" : "San Jose State",
                "Seattle U" : "Seattle",
                "So Carolina St" : "South Carolina State",
                "So Illinois" : "Southern Illinois",
                "So Mississippi" : "Southern Mississippi",
                "South Dakota St" : "South Dakota State",
                "Southern Miss" : "Southern Mississippi",
                "St Bonavent" : "Saint Bonaventure",
                "St Fran (NY)" : "Saint Francis NY",
                "St Fran (PA)" : "Sain Francis PA",
                "St Johns" : "Saint Johns",
                "St Josephs" : "Saint Josephs",
                "St Marys" : "Saint Marys",
                "St Peters" : "Saint Peters",
                "St.Bonaventure" : "Saint Bonaventure",
                "St.Francis NY" : "Saint Francis NY",
                "St.Francis PA" : "Saint Francis PA",
                "St.Johns" : "Saint Johns",
                "St.Josephs" : "Saint Josephs",
                "St.Peter's" : "Saint Peters",
                "Ste F Austin" : "Stephen F Austin",
                "Stephen Austin" : "Stephen F Austin",
                "Stephen F.Austin" : "Stephen F Austin",
                "TCU" : "Texas Christian",
                "TCU Horned" : "Texas Christian",
                "TEM" : "Temple",
                "TENN" : "Tennessee",
                "TN Martin" : "Tennessee Martin",
                "TN State" : "Tennessee State",
                "TN Tech" : "Tennessee Tech",
                "TNST" : "Tennessee State",
                "TNTC" : "Tennessee Tech",
                "TULN" : "Tulane",
                "TX A&M-CC" : "Texas A&M Corpus Christi",
                "TX Christian" : "Texas Christian",
                "TX El Paso" : "Texas-El Paso",
                "TX Southern" : "Texas Southern",
                "TX-Arlington" : "Texas Arlington",
                "TX-Pan Am" : "Texas Pan American",
                "TX-San Ant" : "Texas-San Antonio",
                "TXPan American" : "Texas Pan American",
                "Tenn Martin" : "Tennessee Martin",
                "Tennessee Chat" : "Tennessee Chattanooga",
                "Tennessee U" : "Tennessee",
                "Tex San Antonio" : "Texas-San Antonio",
                "Texas A&MCorpus" : "Texas A&M Corpus Christi",
                "Texas AM" : "Texas A&M",
                "Texas AMCorpus" : "Texas A&M Corpus Christi",
                "Texas Tech Red" : "Texas Tech",
                "Texas-Pan American" : "Texas Pan American",
                "Towson State" : "Towson",
                "Tulsa Golden" : "Tulsa",
                "U Mass" : "Massachusetts",
                "U Penn" : "Pennsylvania",
                "UAB" : "Alabama-Birmingham",
                "UC Davis" : "California Davis",
                "UC Irvine" : "California Irvine",
                "UC Riverside" : "California Riverside",
                "UC San Diego" : "California San Diego",
                "UCDavis" : "California Davis",
                "UCF" : "Central Florida",
                "UCSB" : "California Santa Barbara",
                "UGA" : "Georgia",
                "UL Monroe" : "Louisiana-Monroe",
                "UL-Lafayette" : "Louisiana",
                "UL-Monroe" : "Louisiana-Monroe",
                "ULLafayette" : "Louisiana",
                "ULMonroe" : "Louisiana-Monroe",
                "UMass" : "Massachusetts",
                "UNC" : "North Carolina",
                "UNCWilmington" : "North Carolina Wilmington",
                "UNLV" : "Nevada-Las Vegas",
                "URI" : "Rhode Island",
                "USC" : "Southern California",
                "USCUpstate" : "South Carolina Upstate",
                "UTArlington" : "Texas Arlington",
                "UTC" : "Chattanooga",
                "UTEP" : "Texas-El Paso",
                "UTM" : "Tennessee Martin",
                "UTSA" : "Texas-San Antonio",
                "UVA" : "Virginia",
                "Utah St." : "Utah State",
                "Utah U" : "Utah",
                "Utah Val St" : "Utah Valley State",
                "Utah Valley" : "Utah Valley State",
                "Utah Valley St" : "Utah Valley State",
                "VA Military" : "VMI",
                "VA Tech" : "Virginia Tech",
                "VAN" : "Vanderbilt",
                "VCU" : "Virginia Commonwealth",
                "VMI" : "Virginia Military Institute",
                "Va Commonwealth" : "Virginia Commonwealth",
                "W Carolina" : "Western Carolina",
                "W Illinois" : "Western Illinois",
                "W Kentucky" : "Western Kentucky",
                "W Michigan" : "Western Michigan",
                "W Virginia" : "West Virginia",
                "WCU" : "Western Carolina",
                "WI-Grn Bay" : "Wisconsin Green Bay",
                "WI-Milwkee" : "Wisconsin Milwaukee",
                "Wash State" : "Washington State",
                "Washington U" : "Washington",
                "Western Ky" : "Western Kentucky",
                "Wichita St" : "Wichita State",
                "William Mary" : "William & Mary",
                "William&Mary" : "William & Mary",
                "Wisc Green Bay" : "Wisconsin Green Bay",
                "Wisc Milwaukee" : "Wisconsin Milwaukee",
                "Wisc-Green Bay" : "Wisconsin Green Bay",
                "Wm & Mary" : "William & Mary",
                "XAV" : "Xavier",
                "Youngs St" : "Youngstown State",
                "Youngstown St." : "Youngstown State"}

def cap_helper(x):
    x = re.sub("[a-z][A-Z]", lambda ele: ele[0][0] + " " + ele[0][1], x)

    return (x)

def date_helper(x, year1, year2):
    try:
        x = str(int(x))
        if len(x) > 3:
            first = x[0:2]
        else:
            first = x[0]
        if int(first) < 8:
            x = x + year2
        else:
            x = x + year1

        if int(first) < 10:
            x = '0' + x

        x = datetime.datetime.strptime(x, '%m%d%Y').strftime('%Y-%m-%d')
        return (x)
    except:
        return(np.nan)

def process_historical_ncaa_data():
    fin_output = pd.DataFrame({'DATE': [], 'HOME_TEAM': [], 'WINNER': [], 'LOSER': [], 'PTS_WINNER': [],
                               'PTS_LOSER': [], 'OPEN_SPREAD_WINNER': [], 'OPEN_SPREAD_LOSER': [],
                               'CLOSE_SPREAD_WINNER': [], 'CLOSE_SPREAD_LOSER': [], 'MONEY_LINE_WINNER': [],
                               'MONEY_LINE_LOSER': [], 'MARGIN_OF_VICTORY': []})

    years = ['2007-08', '2008-09', '2009-10', '2010-11', '2011-12', '2012-13', '2013-14', '2014-15', '2015-16',
             '2016-17', '2017-18', '2018-19',
             '2019-20']

    years_dict = {'2007-08': ['2007', '2008'], '2008-09': ['2008', '2009'], '2009-10': ['2009', '2010'],
                  '2010-11': ['2010', '2011'], '2011-12': ['2011', '2012'], '2012-13': ['2012', '2013'],
                  '2013-14': ['2013', '2014'], '2014-15': ['2014', '2015'], '2015-16': ['2015', '2016'],
                  '2016-17': ['2016', '2017'], '2017-18': ['2017', '2018'], '2018-19': ['2018', '2019'],
                  '2019-20': ['2019', '2020']}

    for file in years:
        z = pd.read_excel('/Users/brodyvogel/Downloads/ncaa basketball ' + file + '.xlsx')

        for x in range(len(z['Date']) - 1):
            if z['Date'][x] > z['Date'][x + 1]:
                z.loc[x, 'Date'] = z['Date'][x + 1]

        years = years_dict[file]
        z['Team'] = z['Team'].apply(cap_helper)
        z['Date'] = z['Date'].apply(date_helper, args=(years[0], years[1]))

        z['Open'] = np.asarray([100 if x == 'NL' else 0 if x == 'pk' else x for x in z['Open']])
        z['Close'] = np.asarray([100 if x == 'NL' else 0 if x == 'pk' else x for x in z['Close']])

        z['Open'] = z['Open'].astype('str')
        z['Close'] = z['Close'].astype('str')

        z.loc[["," in x for x in z['Open']], 'Open'] = 'adfadad'
        z.loc[["p" in x for x in z['Open']], 'Open'] = 'adfadad'
        z.loc[["PK" in x for x in z['Open']], 'Open'] = 'adfadad'
        z.loc[[len(x) > 4 for x in z['Open']], 'Open'] = np.nan

        z.loc[["," in x for x in z['Close']], 'Close'] = 'sdfadf'
        z.loc[["p" in x for x in z['Close']], 'Close'] = 'sdfadf'
        z.loc[["PK" in x for x in z['Close']], 'Close'] = 'sdfadf'
        z.loc[[len(x) > 4 for x in z['Close']], 'Close'] = np.nan

        z['Open'] = z['Open'].astype('float')
        z['Close'] = z['Close'].astype('float')

        output = pd.DataFrame({'DATE': [], 'HOME_TEAM': [], 'WINNER': [], 'LOSER': [], 'PTS_WINNER': [],
                               'PTS_LOSER': [], 'OPEN_SPREAD_WINNER': [], 'OPEN_SPREAD_LOSER': [],
                               'CLOSE_SPREAD_WINNER': [], 'CLOSE_SPREAD_LOSER': [], 'MONEY_LINE_WINNER': [],
                               'MONEY_LINE_LOSER': [], 'MARGIN_OF_VICTORY': []})

        for x in range(0, len(z['Team']), 2):
            date = z['Date'][x]

            if z['VH'][x] == 'V':
                home_team = z['Team'][x + 1]
            else:
                home_team = 'Neutral'

            if z['Final'][x] > z['Final'][x + 1]:
                winner = z['Team'][x]
                loser = z['Team'][x + 1]
                pts_winner = z['Final'][x]
                pts_loser = z['Final'][x + 1]
            else:
                winner = z['Team'][x + 1]
                loser = z['Team'][x]
                pts_winner = z['Final'][x + 1]
                pts_loser = z['Final'][x]

            spreads = z.iloc[x:(x + 2), :][['Open', 'Close']]
            if spreads['Open'][x] > spreads['Open'][x + 1]:
                z.loc[x, 'Open'] = z.loc[x + 1, 'Open']
                z.loc[x + 1, 'Open'] = -1 * z.loc[x + 1, 'Open']
            else:
                z.loc[x + 1, 'Open'] = z.loc[x, 'Open']
                z.loc[x, 'Open'] = -1 * z.loc[x, 'Open']
            if spreads['Close'][x] > spreads['Close'][x + 1]:
                z.loc[x, 'Close'] = z.loc[x + 1, 'Close']
                z.loc[x + 1, 'Close'] = -1 * z.loc[x + 1, 'Close']
            else:
                z.loc[x + 1, 'Close'] = spreads.loc[x, 'Close']
                z.loc[x, 'Close'] = -1 * spreads.loc[x, 'Close']

            if z['Final'][x] > z['Final'][x + 1]:
                open_spread_winner = z['Open'][x]
                close_spread_winner = z['Close'][x]

                open_spread_loser = z['Open'][x + 1]
                close_spread_loser = z['Close'][x + 1]

                ml_winner = z['ML'][x]
                ml_loser = z['ML'][x + 1]

            else:
                open_spread_winner = z['Open'][x + 1]
                close_spread_winner = z['Close'][x + 1]

                open_spread_loser = z['Open'][x]
                close_spread_loser = z['Close'][x]

                ml_winner = z['ML'][x + 1]
                ml_loser = z['ML'][x]

            margin_of_victory = pts_winner - pts_loser

            new_row = {'DATE': date, 'HOME_TEAM': home_team, 'WINNER': winner, 'LOSER': loser, 'PTS_WINNER': pts_winner,
                       'PTS_LOSER': pts_loser, 'OPEN_SPREAD_WINNER': open_spread_winner,
                       'OPEN_SPREAD_LOSER': open_spread_loser,
                       'CLOSE_SPREAD_WINNER': close_spread_winner, 'CLOSE_SPREAD_LOSER': close_spread_loser,
                       'MONEY_LINE_WINNER': ml_winner, 'MONEY_LINE_LOSER': ml_loser,
                       'MARGIN_OF_VICTORY': margin_of_victory}

            output = output.append(new_row, ignore_index=True)

        print(file)

        fin_output = pd.concat([fin_output, output])

    fin_output = fin_output.reset_index(drop=True)

    fin_output['COVERED_OPEN'] = np.asarray([
        np.nan if np.isnan(fin_output['OPEN_SPREAD_WINNER'][x]) == True
        else 0 if fin_output['OPEN_SPREAD_WINNER'][x] > 0
        else 0 if fin_output['MARGIN_OF_VICTORY'][x] < (-1 * fin_output['OPEN_SPREAD_WINNER'][x])
        else 1 for x in range(len(fin_output['DATE']))])

    fin_output['COVERED_CLOSE'] = np.asarray([
        np.nan if np.isnan(fin_output['CLOSE_SPREAD_WINNER'][x]) == True
        else 0 if fin_output['CLOSE_SPREAD_WINNER'][x] > 0
        else 0 if fin_output['MARGIN_OF_VICTORY'][x] < (-1 * fin_output['CLOSE_SPREAD_WINNER'][x])
        else 1 for x in range(len(fin_output['DATE']))])

    fin_output = fin_output.dropna(subset = ['DATE']).reset_index(drop = True)

    for day in range(len(fin_output['DATE'])):
        cur_date = datetime.datetime.strptime(fin_output['DATE'][day], '%Y-%m-%d')

        if cur_date.weekday() == 0:
            cur_date = cur_date
        elif cur_date.weekday() == 1:
            cur_date = cur_date - datetime.timedelta(days=1)
        elif cur_date.weekday() == 2:
            cur_date = cur_date - datetime.timedelta(days=2)
        elif cur_date.weekday() == 3:
            cur_date = cur_date - datetime.timedelta(days=3)
        elif cur_date.weekday() == 4:
            cur_date = cur_date - datetime.timedelta(days=4)
        elif cur_date.weekday() == 5:
            cur_date = cur_date - datetime.timedelta(days=5)
        elif cur_date.weekday() == 6:
            cur_date = cur_date - datetime.timedelta(days=6)

        cur_date = cur_date.strftime('%Y-%m-%d')

        fin_output.loc[day, 'DATE'] = cur_date

    for x in range(len(fin_output['HOME_TEAM'])):
        try:
            fin_output.loc[x, 'HOME_TEAM'] = proper_names[fin_output['HOME_TEAM'][x]]
        except:
            fin_output.loc[x, 'HOME_TEAM'] = fin_output.loc[x, 'HOME_TEAM']

        try:
            fin_output.loc[x, 'WINNER'] = proper_names[fin_output['WINNER'][x]]
        except:
            fin_output.loc[x, 'WINNER'] = fin_output.loc[x, 'WINNER']

        try:
            fin_output.loc[x, 'LOSER'] = proper_names[fin_output['LOSER'][x]]
        except:
            fin_output.loc[x, 'LOSER'] = fin_output.loc[x, 'LOSER']

    return (fin_output)

def prepare_data_for_model(results, stats, target_column = 'WON', factor_policy = {}):
    #stats = ncaa_history.copy()
    #results = fin_output.copy()

    stats = stats.reset_index()

    output = []

    for factor in factor_policy.keys():
        if factor_policy[factor]['multi_fac'] != None:
            factor_good_a = factor_policy[factor]['multi_fac'][0][0]
            factor_bad_a = factor_policy[factor]['multi_fac'][0][1]

            factor_good_b = factor_policy[factor]['multi_fac'][1][0]
            factor_bad_b = factor_policy[factor]['multi_fac'][1][1]

            winners = pd.merge(results, stats[['team', 'Date', factor_good_a]], left_on=['DATE', 'WINNER'],
                               right_on=['Date', 'team'], how='left')

            winners = pd.merge(winners, stats[['team', 'Date', factor_bad_a]], left_on=['DATE', 'LOSER'],
                               right_on=['Date', 'team'], how='left')

            winners['two-factor-adv-a'] = winners[factor_bad_a] - winners[factor_good_a]

            winners = winners.drop(columns=[factor_bad_a, factor_good_a])

            winners = pd.merge(winners, stats[['team', 'Date', factor_good_b]], left_on=['DATE', 'LOSER'],
                               right_on=['Date', 'team'], how='left')

            winners = pd.merge(winners, stats[['team', 'Date', factor_bad_b]], left_on=['DATE', 'WINNER'],
                               right_on=['Date', 'team'], how='left')

            winners['two-factor-adv-b'] = winners[factor_bad_b] - winners[factor_good_b]

            winners = winners.drop(columns=[factor_bad_b, factor_good_b])

            winners['multi-factor-adv'] = winners['two-factor-adv-a'] - winners['two-factor-adv-b']

            winners = winners.drop(columns=['two-factor-adv-a', 'two-factor-adv-b'])

            winners['WON'] = 1

            losers = pd.merge(results, stats[['team', 'Date', factor_good_a]], left_on=['DATE', 'LOSER'],
                              right_on=['Date', 'team'], how='left')

            losers = pd.merge(losers, stats[['team', 'Date', factor_bad_a]], left_on=['DATE', 'WINNER'],
                              right_on=['Date', 'team'], how='left')

            losers['two-factor-adv-a'] = losers[factor_bad_a] - losers[factor_good_a]

            losers = losers.drop(columns=[factor_bad_a, factor_good_a])

            losers = pd.merge(losers, stats[['team', 'Date', factor_good_b]], left_on=['DATE', 'WINNER'],
                              right_on=['Date', 'team'], how='left')

            losers = pd.merge(losers, stats[['team', 'Date', factor_bad_b]], left_on=['DATE', 'LOSER'],
                              right_on=['Date', 'team'], how='left')

            losers['two-factor-adv-b'] = losers[factor_bad_b] - losers[factor_good_b]

            losers = losers.drop(columns=[factor_bad_b, factor_good_b])

            losers['multi-factor-adv'] = losers['two-factor-adv-a'] - losers['two-factor-adv-b']

            losers = losers.drop(columns=['two-factor-adv-a', 'two-factor-adv-b'])

            losers['WON'] = 0

            losers['MARGIN_OF_VICTORY'] = -1 * losers['MARGIN_OF_VICTORY']

            losers['COVERED_CLOSE'] = -1 * losers['COVERED_CLOSE'] + 1

            losers['CLOSE_SPREAD_WINNER'] = -1 * losers['CLOSE_SPREAD_WINNER']

            out_hold = pd.concat([winners, losers]).reset_index(drop=True)[['multi-factor-adv', 'DATE', 'HOME_TEAM', 'WINNER', 'LOSER',
                                                                            'MARGIN_OF_VICTORY', 'COVERED_CLOSE',
                                                                            'CLOSE_SPREAD_WINNER', target_column]]

            out_hold = out_hold.rename(columns = {'multi-factor-adv': factor})

            output.append(out_hold)

        elif factor_policy[factor]['two_fac'] != None:
            factor_good = factor_policy[factor]['two_fac'][0]
            factor_bad = factor_policy[factor]['two_fac'][1]

            y = pd.merge(results, stats[['team', 'Date', factor_good]], left_on=['DATE', 'WINNER'], right_on=['Date', 'team'],
                         how='left')

            y = pd.merge(y, stats[['team', 'Date', factor_bad]], left_on=['DATE', 'LOSER'], right_on=['Date', 'team'],
                         how='left')

            y = y[['DATE', 'HOME_TEAM', 'WINNER', 'LOSER', 'PTS_WINNER', 'PTS_LOSER', 'MARGIN_OF_VICTORY',
                   'COVERED_CLOSE', 'CLOSE_SPREAD_WINNER', factor_good, factor_bad]]

            y.columns = ['DATE', 'WINNER', 'LOSER', 'PTS_WINNER', 'PTS_LOSER', 'MARGIN_OF_VICTORY', 'COVERED_CLOSE', 'CLOSE_SPREAD_WINNER',
                         factor_good + 'WINNER',
                         factor_bad + 'LOSER']

            y = pd.merge(y, stats[['team', 'Date', factor_good]], left_on=['DATE', 'LOSER'], right_on=['Date', 'team'],
                         how='left')

            y = pd.merge(y, stats[['team', 'Date', factor_bad]], left_on=['DATE', 'WINNER'], right_on=['Date', 'team'],
                         how='left')

            y = y[['DATE', 'HOME_TEAM', 'WINNER', 'LOSER', 'PTS_WINNER', 'PTS_LOSER', 'MARGIN_OF_VICTORY',
                   'COVERED_CLOSE', 'CLOSE_SPREAD_WINNER', factor_good + 'WINNER',
                   factor_bad + 'LOSER', factor_good, factor_bad]]

            y.columns = ['DATE', 'HOME_TEAM', 'WINNER', 'LOSER', 'PTS_WINNER', 'PTS_LOSER', 'MARGIN_OF_VICTORY', 'COVERED_CLOSE',
                         'CLOSE_SPREAD_WINNER', factor_good + 'WINNER',
                         factor_bad + 'LOSER', factor_good + 'LOSER', factor_bad + 'WINNER']

            y = y.dropna().reset_index(drop=True)

            winners = y[['DATE', 'HOME_TEAM', 'WINNER', 'LOSER', 'MARGIN_OF_VICTORY',
                         'COVERED_CLOSE', 'CLOSE_SPREAD_WINNER', factor_good + 'WINNER', factor_bad + 'LOSER']]

            winners['ADV'] = winners[factor_bad + 'LOSER'] - winners[factor_good + 'WINNER']

            winners['WON'] = 1

            losers = y[['DATE', 'HOME_TEAM', 'WINNER', 'LOSER', 'MARGIN_OF_VICTORY',
                        'COVERED_CLOSE', 'CLOSE_SPREAD_WINNER', factor_good + 'LOSER', factor_bad + 'WINNER']]

            losers['ADV'] = losers[factor_bad + 'WINNER'] - losers[factor_good + 'LOSER']

            losers['WON'] = 0

            losers['MARGIN_OF_VICTORY'] = -1 * losers['MARGIN_OF_VICTORY']

            losers['COVERED_CLOSE'] = -1 * losers['COVERED_CLOSE'] + 1

            losers['CLOSE_SPREAD_WINNER'] = -1 * losers['CLOSE_SPREAD_WINNER']

            out_hold = pd.concat([winners, losers]).reset_index(drop=True)[['ADV', 'DATE', 'HOME_TEAM', 'WINNER', 'LOSER',
                                                                            'MARGIN_OF_VICTORY', 'COVERED_CLOSE',
                                                                            'CLOSE_SPREAD_WINNER', target_column]]

            out_hold = out_hold.rename(columns = {'ADV': factor})

            output.append(out_hold)

        else:
            y = pd.merge(results, stats[['team', 'Date', factor]], left_on=['DATE', 'WINNER'], right_on=['Date', 'team'],
                         how='left')

            y = pd.merge(y, stats[['team', 'Date', factor]], left_on=['DATE', 'LOSER'], right_on=['Date', 'team'],
                         how='left')

            y = y[['DATE', 'HOME_TEAM', 'WINNER', 'LOSER', 'PTS_WINNER', 'PTS_LOSER', 'MARGIN_OF_VICTORY', 'COVERED_CLOSE',
                   'CLOSE_SPREAD_WINNER', factor + '_x',
                   factor + '_y']]

            y.columns = ['DATE', 'HOME_TEAM', 'WINNER', 'LOSER', 'PTS_WINNER', 'PTS_LOSER', 'MARGIN_OF_VICTORY', 'COVERED_CLOSE',
                         'CLOSE_SPREAD_WINNER', factor + '_WINNER',
                         factor + '_LOSER']

            y = y.dropna().reset_index(drop=True)

            winners = y[['DATE', 'HOME_TEAM', 'WINNER', 'LOSER', 'PTS_WINNER', 'PTS_LOSER', 'MARGIN_OF_VICTORY', 'COVERED_CLOSE',
                         'CLOSE_SPREAD_WINNER', factor + '_WINNER',
                         factor + '_LOSER']]

            winners['ADV'] = winners[factor + '_LOSER'] - winners[factor + '_WINNER']

            winners = winners.rename(columns={factor + '_LOSER': factor})

            winners['WON'] = 1

            losers = y[['DATE', 'HOME_TEAM', 'WINNER', 'LOSER', 'PTS_WINNER', 'PTS_LOSER', 'MARGIN_OF_VICTORY', 'COVERED_CLOSE',
                        'CLOSE_SPREAD_WINNER', factor + '_WINNER',
                         factor + '_LOSER']]

            losers['ADV'] = losers[factor + '_WINNER'] - losers[factor + '_LOSER']

            losers = losers.rename(columns={factor + '_LOSER': factor})

            losers['WON'] = 0

            losers['MARGIN_OF_VICTORY'] = -1 * losers['MARGIN_OF_VICTORY']
            losers['COVERED_CLOSE'] = -1 * losers['COVERED_CLOSE'] + 1
            losers['CLOSE_SPREAD_WINNER'] = -1 * losers['CLOSE_SPREAD_WINNER']

            out_hold = pd.concat([winners, losers]).reset_index(drop=True)[['ADV', 'DATE', 'HOME_TEAM', 'WINNER', 'LOSER',
                                                                            'MARGIN_OF_VICTORY', 'COVERED_CLOSE',
                                                                            'CLOSE_SPREAD_WINNER', target_column]]

            out_hold = out_hold.rename(columns = {'ADV': factor})

            output.append(out_hold)

    fin_out = output[0]
    fin_out = fin_out.drop_duplicates(subset = ['DATE', 'WINNER', 'LOSER', 'MARGIN_OF_VICTORY', 'COVERED_CLOSE', 'CLOSE_SPREAD_WINNER'])
    for x in range(1, len(output)):
        new = output[x][['DATE', 'WINNER', 'LOSER', 'MARGIN_OF_VICTORY', 'COVERED_CLOSE', 'CLOSE_SPREAD_WINNER', list(factor_policy.keys())[x]]]
        new = new.drop_duplicates(subset = ['DATE', 'WINNER', 'LOSER', 'MARGIN_OF_VICTORY', 'COVERED_CLOSE', 'CLOSE_SPREAD_WINNER'])
        fin_out = pd.merge(fin_out, new,
                            left_on = ['DATE', 'WINNER', 'LOSER', 'MARGIN_OF_VICTORY', 'COVERED_CLOSE', 'CLOSE_SPREAD_WINNER'],
                            right_on = ['DATE', 'WINNER', 'LOSER', 'MARGIN_OF_VICTORY', 'COVERED_CLOSE', 'CLOSE_SPREAD_WINNER'],
                           how = 'left')

    # home_team

    fin_out['HOME'] = [1 if (fin_out['HOME_TEAM'][x] == fin_out['WINNER'][x]) and fin_out['WON'][x] == 1
                       else 1 if (fin_out['HOME_TEAM'][x] == fin_out['LOSER'][x]) and fin_out['WON'][x] == 0
                       else 0 for x in range(len(fin_out['HOME_TEAM']))]

    fin_out_no_nas = fin_out.dropna()

    return({'raw_data': fin_out, 'no_nas': fin_out_no_nas})

def fit_model(data, factors, target_response):
    #data = fin_out_no_nas.copy()
    factors = list(factors.keys()) + ['HOME']
    target_response = 'WON'

    #X_train, X_test, y_train, y_test = train_test_split(data[factors], data[target_response], random_state=42)
    pipe = make_pipeline(StandardScaler(), LogisticRegression())
    pipe.fit(data[factors], data[target_response])  # apply scaling on training data
    #pipe.fit(X_train, y_train)

    #scaled_data = StandardScaler().fit_transform(data[factors])
    #knn = KNeighborsClassifier(n_neighbors = 9).fit(scaled_data, data[target_response]).predict_proba(scaled_data)
    #log = LogisticRegression().fit(scaled_data, data[target_response]).predict_proba(scaled_data)
    #rf = RandomForestClassifier(max_depth = 5).fit(scaled_data, data[target_response]).predict_proba(scaled_data)

    #pred_probs = pd.DataFrame({'knn': knn[:, 1], 'log': log[:, 1], 'rf': rf[:, 1], 'truth': data[target_response]})

    #pred_probs['mean_prob'] = pred_probs[['knn', 'log', 'rf']].mean(axis = 1)

    #pred_probs = pred_probs.reset_index(drop = True)

    #pred_probs['pred'] = [1 if pred_probs['mean_prob'][x] > 0.49 else 0 for x in range(len(pred_probs['mean_prob']))]
    #pred_probs['pred_correct'] = pred_probs['pred'] == pred_probs['truth']

    #pipe.score(X_train, y_train)
    #pipe.score(data[factors], data[target_response])
    model = pipe.named_steps['logisticregression']
    #polynomials = pipe.named_steps['polynomialfeatures']
    scaler = pipe.named_steps['standardscaler']

    prac_data = StandardScaler().fit_transform(data[factors])
    #prac_data = pd.DataFrame(prac_data, columns=data[factors].columns)
    #polynomials = PolynomialFeatures(interaction_only = True).fit(prac_data)
    #prac_data = polynomials.transform(prac_data)
    #prac_data = pd.DataFrame(prac_data, polynomials.get_feature_names())
    #model = LogisticRegression().fit(prac_data)

    t = model.predict_proba(prac_data)[:, 1]
    z = model.predict(prac_data)

    preds = pd.DataFrame({'pred_prob': t, 'pred': z, 'truth': data[target_response], 'MARGIN_OF_VICTORY': data['MARGIN_OF_VICTORY']})

    preds['confidence_bucket'] = preds['pred_prob'].transform(
        lambda x: pd.qcut(x, 20, duplicates='drop', labels=False))

    n = preds.groupby(['confidence_bucket'])['MARGIN_OF_VICTORY'].describe(
        percentiles=[0.05, 0.1, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.75, 0.90, 0.95])
    p = n[['25%', '40%', '50%', '75%', '90%']]
    q = preds.groupby(['confidence_bucket'])['pred_prob'].describe()[['min', 'max']]
    # o = to_test_evaluate.groupby(['confidence', 'pred_winner_advantages'])['Margin_of_Victory_pred_winner'].describe(percentiles = [0.05, 0.1, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.75, 0.90, 0.95])

    q = q.reset_index()
    p = p.reset_index()

    nopq3 = pd.merge(q, p)

    #to = data.reset_index(drop=False)

    #z = pd.merge(to[['index', 'MARGIN_OF_VICTORY']], preds, left_on='index', right_on='number')

    l = preds.groupby('confidence_bucket')['MARGIN_OF_VICTORY'].describe(percentiles = [0.05, 0.1, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.75, 0.90, 0.95])

    return({'model': model, 'spread_target': nopq3, 'scaler': scaler})

# PROBLEMS: biased data; not confirmed correct
def validate_model(data, date_to_start, factors, target_response):
    #date_to_start = '2018-01-01'
    data = fin_out_no_nas.copy()
    data_train = data.loc[data['DATE'] <= date_to_start]
    data_test = data.loc[data['DATE'] > date_to_start]
    factors = list(factor_policy.keys()) + ['HOME']
    target_response = 'WON'

    #X_train, X_test, y_train, y_test = train_test_split(data[factors], data[target_response], random_state=42)
    pipe = make_pipeline(StandardScaler(), LogisticRegression())
    pipe.fit(data_train[factors], data_train[target_response])  # apply scaling on training data

    model = pipe.named_steps['logisticregression']
    scaler = pipe.named_steps['standardscaler']

    pred_train_data = StandardScaler().fit_transform(data_train[factors])

    t = model.predict_proba(pred_train_data)[:, 1]
    z = model.predict(pred_train_data)

    pred_thresh = pd.DataFrame({'pred_prob': t, 'pred': z, 'MARGIN_OF_VICTORY': data_train['MARGIN_OF_VICTORY']})

    pred_thresh['confidence_bucket'] = pred_thresh['pred_prob'].transform(
        lambda x: pd.qcut(x, 20, duplicates='drop', labels=False))

    n = pred_thresh.groupby(['confidence_bucket'])['MARGIN_OF_VICTORY'].describe(
        percentiles=[0.05, 0.1, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.75, 0.90, 0.95])
    p = n[['25%', '40%', '50%', '75%', '90%']]
    q = pred_thresh.groupby(['confidence_bucket'])['pred_prob'].describe()[['min', 'max']]
    q = q.reset_index()
    p = p.reset_index()

    nopq3 = pd.merge(q, p)
    nopq3.loc[19, 'max'] = 1
    nopq3.loc[0, 'min'] = 0


    pred_test_data = StandardScaler().fit_transform(data_test[factors])
    test_t = model.predict_proba(pred_test_data)[:, 1]
    test_z = model.predict(pred_test_data)
    pred_eval = pd.DataFrame({'pred_prob': test_t, 'pred': test_z, 'truth': data_test['WON'], 'MARGIN_OF_VICTORY': data_test['MARGIN_OF_VICTORY'],
                              'COVERED_CLOSE': data_test['COVERED_CLOSE'], 'CLOSE_SPREAD': data_test['CLOSE_SPREAD_WINNER']})

    pred_eval = pred_eval.reset_index(drop = True)
    pred_eval['NO_BRAINER'] = np.nan
    pred_eval['GOOD_BET'] = np.nan
    pred_eval['CHANCE'] = np.nan

    for x in range(len(pred_eval['truth'])):
        found = False
        row = 0
        diff = round(pred_eval['pred_prob'][x], 3)
        while found == False:
            if (diff >= nopq3.loc[row, 'min']) and (diff <= round(nopq3.loc[row, 'max'], 3)):
                pred_eval.loc[x, 'NO_BRAINER'] = -1 * round(nopq3.loc[row, '25%'], 3)
                pred_eval.loc[x, 'GOOD_BET'] = -1 * round(nopq3.loc[row, '40%'], 3)
                pred_eval.loc[x, 'CHANCE'] = -1 * round(nopq3.loc[row, '50%'], 3)
                found = True
            else:
                row += 1

    pred_eval['NO_BRAINER_BET'] = np.nan
    pred_eval['GOOD_BET_BET'] = np.nan
    pred_eval['CHANCE_BET'] = np.nan

    for x in range(len(pred_eval['truth'])):
        # favorite
        if (pred_eval['NO_BRAINER'][x] < 0) and (pred_eval['NO_BRAINER'][x] <= pred_eval['CLOSE_SPREAD'][x]):
            if pred_eval['MARGIN_OF_VICTORY'][x] > (-1 * pred_eval['CLOSE_SPREAD'][x]):
                pred_eval.loc[x, 'NO_BRAINER_BET'] = 1
            else:
                pred_eval.loc[x, 'NO_BRAINER_BET'] = 0
        # dog
        elif (pred_eval['NO_BRAINER'][x] >= 0) and (pred_eval['NO_BRAINER'][x] <= pred_eval['CLOSE_SPREAD'][x]):
            if pred_eval['MARGIN_OF_VICTORY'][x] < pred_eval['CLOSE_SPREAD'][x]:
                pred_eval.loc[x, 'NO_BRAINER_BET'] = 1
            else:
                pred_eval.loc[x, 'NO_BRAINER_BET'] = 0
        # favorite
        elif (pred_eval['GOOD_BET'][x] < 0) and (pred_eval['GOOD_BET'][x] <= pred_eval['CLOSE_SPREAD'][x]):
            if pred_eval['MARGIN_OF_VICTORY'][x] > (-1 * pred_eval['CLOSE_SPREAD'][x]):
                pred_eval.loc[x, 'GOOD_BET_BET'] = 1
            else:
                pred_eval.loc[x, 'GOOD_BET_BET'] = 0
        # dog
        elif (pred_eval['GOOD_BET'][x] >= 0) and (pred_eval['GOOD_BET'][x] <= pred_eval['CLOSE_SPREAD'][x]):
            if pred_eval['MARGIN_OF_VICTORY'][x] < pred_eval['CLOSE_SPREAD'][x]:
                pred_eval.loc[x, 'GOOD_BET_BET'] = 1
            else:
                pred_eval.loc[x, 'GOOD_BET_BET'] = 0
        # favorite
        elif (pred_eval['CHANCE'][x] < 0) and (pred_eval['CHANCE'][x] <= pred_eval['CLOSE_SPREAD'][x]):
            if pred_eval['MARGIN_OF_VICTORY'][x] > (-1 * pred_eval['CLOSE_SPREAD'][x]):
                pred_eval.loc[x, 'CHANCE_BET'] = 1
            else:
                pred_eval.loc[x, 'CHANCE_BET'] = 0
        # dog
        elif (pred_eval['CHANCE'][x] >= 0) and (pred_eval['CHANCE'][x] <= pred_eval['CLOSE_SPREAD'][x]):
            if pred_eval['MARGIN_OF_VICTORY'][x] < pred_eval['CLOSE_SPREAD'][x]:
                pred_eval.loc[x, 'CHANCE_BET'] = 1
            else:
                pred_eval.loc[x, 'CHANCE_BET'] = 0

    print("Effectiveness of Chance Bets: ", pred_eval['CHANCE_BET'].mean())
    print("Effectiveness of Good Bets: ", pred_eval['GOOD_BET_BET'].mean())
    print("Effectiveness of No Brainer Bets: ", pred_eval['NO_BRAINER_BET'].mean())

    print("Percentage of Games that fall in each basket: ", pred_eval[['CHANCE_BET', 'GOOD_BET_BET', 'NO_BRAINER_BET']].apply(
        lambda x: 1 - x.isnull().sum() / len(x))
    )



def fit_model_continuous(data, factors, target_response):
    data = fin_out_no_nas.copy()
    factors = list(factor_policy.keys()) + ['HOME']
    target_response = 'MARGIN_OF_VICTORY'

    #X_train, X_test, y_train, y_test = train_test_split(data[factors], data[target_response], random_state=42)
    pipe = make_pipeline(StandardScaler(), LinearRegression())
    pipe.fit(data[factors], data[target_response])  # apply scaling on training data
    #pipe.fit(X_train, y_train)

    #pipe.score(X_train, y_train)
    pipe.score(data[factors], data[target_response])
    model = pipe.named_steps['linearregression']
    scaler = pipe.named_steps['standardscaler']

    prac_data = StandardScaler().fit_transform(data[factors])
    #prac_data = pd.DataFrame(prac_data, columns=data[factors].columns)
    #polynomials = PolynomialFeatures(interaction_only = True).fit(prac_data)
    #prac_data = polynomials.transform(prac_data)
    #prac_data = pd.DataFrame(prac_data, polynomials.get_feature_names())
    #model = LogisticRegression().fit(prac_data)

    t = model.predict(prac_data)
    z = model.predict(prac_data)

    preds = pd.DataFrame({'pred_prob': t, 'pred': z, 'truth': data[target_response], 'MARGIN_OF_VICTORY': data['MARGIN_OF_VICTORY']})

    preds['confidence_bucket'] = preds['pred_prob'].transform(
        lambda x: pd.qcut(x, 20, duplicates='drop', labels=False))

    n = preds.groupby(['confidence_bucket'])['MARGIN_OF_VICTORY'].describe(
        percentiles=[0.05, 0.1, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.75, 0.90, 0.95])
    p = n[['25%', '40%', '50%', '75%', '90%']]
    q = preds.groupby(['confidence_bucket'])['pred_prob'].describe()[['min', 'max']]
    # o = to_test_evaluate.groupby(['confidence', 'pred_winner_advantages'])['Margin_of_Victory_pred_winner'].describe(percentiles = [0.05, 0.1, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.75, 0.90, 0.95])

    q = q.reset_index()
    p = p.reset_index()

    nopq3 = pd.merge(q, p)

    #to = data.reset_index(drop=False)

    #z = pd.merge(to[['index', 'MARGIN_OF_VICTORY']], preds, left_on='index', right_on='number')

    l = preds.groupby('confidence_bucket')['MARGIN_OF_VICTORY'].describe(percentiles = [0.05, 0.1, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.75, 0.90, 0.95])

    
def evaluate_with_model(data, home_team, away_team, factor_policy, scaler, model, spread_target):
    #data = for_today.copy()
    #home_team = 'Clemson'
    #away_team = 'Notre Dame'
    #pipe = StandardScaler()
    #spread_target = [nopq3]
    
    home_team_stats = data.loc[home_team]

    away_team_stats = data.loc[away_team]

    eval_df = pd.DataFrame({})
    
    for factor in factor_policy.keys():

        eval_df[factor] = np.nan

        if factor_policy[factor]['multi_fac'] != None:
            factor_good_a = factor_policy[factor]['multi_fac'][0][0]
            factor_good_b = factor_policy[factor]['multi_fac'][1][0]
            factor_bad_a = factor_policy[factor]['multi_fac'][0][1]
            factor_bad_b = factor_policy[factor]['multi_fac'][1][1]

            home_team_good_fac_a = home_team_stats[factor_good_a]
            home_team_good_fac_b = home_team_stats[factor_good_b]
            away_team_good_fac_a = away_team_stats[factor_good_a]
            away_team_good_fac_b = away_team_stats[factor_good_b]

            home_team_bad_fac_a = home_team_stats[factor_bad_a]
            home_team_bad_fac_b = home_team_stats[factor_bad_b]
            away_team_bad_fac_a = away_team_stats[factor_bad_a]
            away_team_bad_fac_b = away_team_stats[factor_bad_b]

            home_team_status = (away_team_bad_fac_a - home_team_good_fac_a) - (home_team_bad_fac_b - away_team_good_fac_a)
            away_team_status = (home_team_bad_fac_b - away_team_good_fac_a) - (away_team_bad_fac_a - home_team_good_fac_a)

            eval_df.loc[0, factor] = home_team_status
            eval_df.loc[1, factor] = away_team_status

        elif factor_policy[factor]['two_fac'] != None:
            factor_good = factor_policy[factor]['two_fac'][0]
            factor_bad = factor_policy[factor]['two_fac'][1]

            home_team_good_fac = home_team_stats[factor_good]
            away_team_good_fac = away_team_stats[factor_good]
            home_team_bad_fac = home_team_stats[factor_bad]
            away_team_bad_fac = away_team_stats[factor_bad]

            home_team_status = away_team_bad_fac - home_team_good_fac
            away_team_status = home_team_bad_fac - away_team_good_fac

            eval_df.loc[0, factor] = home_team_status
            eval_df.loc[1, factor] = away_team_status

        else:

            home_team_status = away_team_stats[factor] - home_team_stats[factor]
            away_team_status = home_team_stats[factor] - away_team_stats[factor]

            eval_df.loc[0, factor] = home_team_status
            eval_df.loc[1, factor] = away_team_status

    eval_df['HOME'] = np.nan

    eval_df.loc[0, 'HOME'] = 1
    eval_df.loc[1, 'HOME'] = 0

    to_pred = scaler.transform(eval_df)

    z = model.predict_proba(to_pred)

    home_team_prob = round(z[0, 1], 2)
    away_team_prob = round(z[1, 1], 2)

    found = False
    row = 0
    if spread_target != None:
        spread_df = spread_target[0]
        zz = 0
        while found == False:
            if zz == 1:
                found = True
            if (home_team_prob >= spread_df.loc[row, 'min']) and (home_team_prob <= spread_df.loc[row, 'max']):
                    print(home_team, 'has a', str(round(z[0, 1], 2)), 'percent chance of winning.')
                    print("No-Brainer: " + str(-1 * spread_df.loc[row, '25%']),
                          ", Good Bet: " + str(-1 * spread_df.loc[row, '40%']),
                          ", Chance: " + str(-1 * spread_df.loc[row, '50%']))
                    print("No-Brainer Fade: " + str(-1 * spread_df.loc[row, '90%']),
                          "Good Fade: " + str(-1 * spread_df.loc[row, '75%']))
                    found = True
            else:
                row += 1

    found = False
    row = 0
    if spread_target != None:
        spread_df = spread_target[0]
        zz = 0
        while found == False:
            if zz == 1:
                found = True
            if (away_team_prob >= spread_df.loc[row, 'min']) and (away_team_prob <= spread_df.loc[row, 'max']):
                    print(away_team, 'has a', str(round(z[1, 1], 2)), 'percent chance of winning.')
                    print("No-Brainer: " + str(-1 * spread_df.loc[row, '25%']),
                          ", Good Bet: " + str(-1 * spread_df.loc[row, '40%']),
                          ", Chance: " + str(-1 * spread_df.loc[row, '50%']))
                    print("No-Brainer Fade: " + str(-1 * spread_df.loc[row, '90%']),
                          "Good Fade: " + str(-1 * spread_df.loc[row, '75%']))
                    found = True
            else:
                row += 1

#ncaa_history = get_historical_ncaa_data(
#    ['2007-11-12', '2008-11-17', '2009-11-16', '2010-11-15', '2011-11-14', '2012-11-12', '2013-11-11', '2014-11-17',
#     '2015-11-16',
#     '2016-11-14', '2017-11-13', '2018-11-12', '2019-11-11'],
#    attributes = {'offensive-efficiency': 'desc',
#                  'floor-percentage': 'desc',
#                  'effective-field-goal-pct': 'desc',
#                  'two-point-pct': 'desc',
#                  'three-point-pct': 'desc',
#                  'true-shooting-percentage': 'desc',
#                  'ftm-per-100-possessions': 'desc',
#                  'predictive-by-other': 'desc',
#                  'schedule-strength-by-other': 'desc',
#                  'offensive-rebounding-pct': 'desc',
#                  'defensive-rebounding-pct': 'desc',
#                  'turnovers-per-possession': 'desc',
#                  'defensive-efficiency': 'desc',
#                  'opponent-floor-percentage': 'asc',
#                  'opponent-effective-field-goal-pct': 'asc',
#                  'opponent-two-point-pct': 'asc',
#                 'opponent-three-point-pct': 'asc',
#                  'opponent-true-shooting-percentage': 'asc',
#                  'opponent-ftm-per-100-possessions': 'asc',
#                  'opponent-turnovers-per-possession': 'asc',
#                  'effective-possession-ratio': 'desc',
#                  'opponent-effective-possession-ratio': 'asc'}, start_week=2)

#ncaa_history = ncaa_history.reset_index()
#for x in range(len(ncaa_history['team'])):
#    try:
#        ncaa_history.loc[x, 'team'] = proper_names[ncaa_history['team'][x]]
#    except:
#        ncaa_history.loc[x, 'team'] = ncaa_history.loc[x, 'team']

#ncaa_history = ncaa_history.set_index('team')

#ncaa_history['defensive-efficiency_rank'] = ncaa_history.groupby('Date')['defensive-efficiency'].rank(ascending=True)
#ncaa_history['turnovers-per-possession_rank'] = ncaa_history.groupby('Date')['turnovers-per-possession'].rank(ascending=True)
#ncaa_history['opponent-turnovers-per-possession_rank'] = ncaa_history.groupby('Date')['opponent-turnovers-per-possession'].rank(ascending=False)

#for x in sorted(proper_names.keys()):
#    print('"' + x + '" : ' + '"' + proper_names[x] + '",')