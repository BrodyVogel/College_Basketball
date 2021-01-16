import numpy as np
import pandas as pd
import datetime

def win_breakdown(stats = None, results = None, factor = 'bs'):
    z = stats.copy()

    z = z.reset_index()

    y = results.copy()

    y = pd.merge(y, z[['team', 'Date', factor]], left_on = ['DATE', 'WINNER'], right_on = ['Date', 'team'], how = 'left')

    y = pd.merge(y, z[['team', 'Date', factor]], left_on = ['DATE', 'LOSER'], right_on = ['Date', 'team'], how = 'left')

    y = y[['DATE', 'WINNER', 'LOSER', 'PTS_WINNER', 'PTS_LOSER', 'MARGIN_OF_VICTORY', factor + '_x', factor + '_y']]

    y.columns = ['DATE', 'WINNER', 'LOSER', 'PTS_WINNER', 'PTS_LOSER', 'MARGIN_OF_VICTORY', factor + '_WINNER', factor + '_LOSER']

    y = y.dropna().reset_index(drop = True)

    y['ADV_WON'] = [1 if y[factor + '_WINNER'][x] < y[factor + '_LOSER'][x] else 0 for x in range(len(y['WINNER']))]

    y['ADV'] = y[factor + '_LOSER'] - y[factor + '_WINNER']

    y['ADV'] = y['ADV'].abs()

    y['ADV_BUCKET'] = y['ADV'].transform(
                     lambda x: pd.qcut(x, 10, duplicates='drop', labels = False))

    y['MARGIN_OF_VICTORY_ADV'] = [y['MARGIN_OF_VICTORY'][x] if y['ADV_WON'][x] == 1
                                  else -1 * y['MARGIN_OF_VICTORY'][x]
                                  for x in range(len(y['WINNER']))]

    print("Percentage of Games Won by Team with Advantage:", y['ADV_WON'].mean())
    print("Break Points for Baskets:", y.groupby('ADV_BUCKET')['ADV'].describe()[['min', 'max']])
    print("Percentage of Games Won by Team with Cascading Advantage Size:", y.groupby('ADV_BUCKET')['ADV_WON'].mean())
    print("Margin of Victory with Cascading Advantage Size: \n", y.groupby('ADV_BUCKET')['MARGIN_OF_VICTORY_ADV'].describe())

#win_breakdown(stats = ncaa_history, results = fin_output, factor = 'offensive-efficiency_rank') #65% win,, 1, 2, 3
#win_breakdown(stats = ncaa_history, results = fin_output, factor = 'floor-percentage_rank') #64%, 1, 2, 3
#win_breakdown(stats = ncaa_history, results = fin_output, factor = 'effective-field-goal-pct_rank') #61%, 1, 2
#win_breakdown(stats = ncaa_history, results = fin_output, factor = 'two-point-pct_rank') #61%, 1, 2
win_breakdown(stats = ncaa_history, results = fin_output, factor = 'three-point-pct_rank') #56%, 1
#win_breakdown(stats = ncaa_history, results = fin_output, factor = 'true-shooting-percentage_rank') #61%, 1, 2
#win_breakdown(stats = ncaa_history, results = fin_output, factor = 'ftm-per-100-possessions_rank') #56%, 1
win_breakdown(stats = ncaa_history, results = fin_output, factor = 'predictive-by-other_rank') #70%, 1, 2, 3
#win_breakdown(stats = ncaa_history, results = fin_output, factor = 'offensive-rebounding-pct_rank') #57%, 1
#win_breakdown(stats = ncaa_history, results = fin_output, factor = 'defensive-rebounding-pct_rank') #57%, 1
#win_breakdown(stats = ncaa_history, results = fin_output, factor = 'turnovers-per-possession_rank') #57%, 1, 2
#win_breakdown(stats = ncaa_history, results = fin_output, factor = 'defensive-efficiency_rank') #62%, 1, 2, 3
#win_breakdown(stats = ncaa_history, results = fin_output, factor = 'opponent-floor-percentage_rank') #62%, 1, 2
#win_breakdown(stats = ncaa_history, results = fin_output, factor = 'opponent-effective-field-goal-pct_rank') #60%, 1, 2
#win_breakdown(stats = ncaa_history, results = fin_output, factor = 'opponent-two-point-pct_rank') #60%, 1, 2
win_breakdown(stats = ncaa_history, results = fin_output, factor = 'opponent-three-point-pct_rank') #55%, 1, 2
#win_breakdown(stats = ncaa_history, results = fin_output, factor = 'opponent-true-shooting-percentage_rank') #60%, 1, 2
#win_breakdown(stats = ncaa_history, results = fin_output, factor = 'opponent-ftm-per-100-possessions_rank')  #56%, 1, 2
#win_breakdown(stats = ncaa_history, results = fin_output, factor = 'opponent-turnovers-per-possession_rank') #54%, 1
#win_breakdown(stats = ncaa_history, results = fin_output, factor = 'effective-possession-ratio_rank') #59%, 1, 2
#win_breakdown(stats = ncaa_history, results = fin_output, factor = 'opponent-effective-possession-ratio_rank') #56%, 1
win_breakdown(stats = ncaa_history, results = fin_output, factor = 'schedule-strength-by-other_rank') #64, 1, 2

def win_breakdown_two_factors(stats, results, factors):
    factor_good = factors[0]
    factor_bad = factors[1]

    z = stats.copy()

    z = z.reset_index()

    y = results.copy()

    y = pd.merge(y, z[['team', 'Date', factor_good]], left_on=['DATE', 'WINNER'], right_on=['Date', 'team'], how='left')

    y = pd.merge(y, z[['team', 'Date', factor_bad]], left_on=['DATE', 'LOSER'], right_on=['Date', 'team'], how='left')

    y = y[['DATE', 'WINNER', 'LOSER', 'PTS_WINNER', 'PTS_LOSER', 'MARGIN_OF_VICTORY', factor_good, factor_bad]]

    y.columns = ['DATE', 'WINNER', 'LOSER', 'PTS_WINNER', 'PTS_LOSER', 'MARGIN_OF_VICTORY', factor_good + 'WINNER',
                 factor_bad + 'LOSER']

    y = pd.merge(y, z[['team', 'Date', factor_good]], left_on=['DATE', 'LOSER'], right_on=['Date', 'team'], how='left')

    y = pd.merge(y, z[['team', 'Date', factor_bad]], left_on=['DATE', 'WINNER'], right_on=['Date', 'team'], how='left')

    y = y[['DATE', 'WINNER', 'LOSER', 'PTS_WINNER', 'PTS_LOSER', 'MARGIN_OF_VICTORY', factor_good + 'WINNER',
                 factor_bad + 'LOSER', factor_good, factor_bad]]

    y.columns = ['DATE', 'WINNER', 'LOSER', 'PTS_WINNER', 'PTS_LOSER', 'MARGIN_OF_VICTORY', factor_good + 'WINNER',
                  factor_bad + 'LOSER', factor_good + 'LOSER', factor_bad + 'WINNER']

    y = y.dropna().reset_index(drop=True)

    winners = y[['DATE', 'WINNER', 'LOSER', 'MARGIN_OF_VICTORY', factor_good + 'WINNER', factor_bad + 'LOSER']]

    winners['ADV'] = winners[factor_bad + 'LOSER'] - winners[factor_good + 'WINNER']

    winners['WON'] = 1

    losers = y[['DATE', 'WINNER', 'LOSER', 'MARGIN_OF_VICTORY', factor_good + 'LOSER', factor_bad + 'WINNER']]

    losers['ADV'] = losers[factor_bad + 'WINNER'] - losers[factor_good + 'LOSER']

    losers['WON'] = 0

    y = pd.concat([winners[['DATE', 'WINNER', 'LOSER', 'MARGIN_OF_VICTORY', 'ADV', 'WON']],
                  losers[['DATE', 'WINNER', 'LOSER', 'MARGIN_OF_VICTORY', 'ADV', 'WON']]]).reset_index(drop = True)

    y['ADV_BUCKET'] = y['ADV'].transform(
        lambda x: pd.qcut(x, 20, duplicates='drop', labels=False))

    y['MARGIN_OF_VICTORY_ADV'] = [y['MARGIN_OF_VICTORY'][x] if y['WON'][x] == 1
                                  else -1 * y['MARGIN_OF_VICTORY'][x]
                                  for x in range(len(y['WINNER']))]

    #print("Percentage of Games Won by Team with Advantage:", y['WON'].mean())
    print("Break Points for Baskets:", y.groupby('ADV_BUCKET')['ADV'].describe()[['min', 'max']])
    print("Percentage of Games Won by Team with Cascading Advantage Size:", y.groupby('ADV_BUCKET')['WON'].mean())
    print("Margin of Victory with Cascading Advantage Size: \n",
          y.groupby('ADV_BUCKET')['MARGIN_OF_VICTORY_ADV'].describe())

#win_breakdown_two_factors(stats = ncaa_history, results = fin_output, factors = ['offensive-efficiency_rank', 'defensive-efficiency_rank']) #1, 2
#win_breakdown_two_factors(stats = ncaa_history, results = fin_output, factors = ['defensive-efficiency_rank', 'offensive-efficiency_rank']) #1, 2
win_breakdown_two_factors(stats = ncaa_history, results = fin_output, factors = ['floor-percentage_rank', 'opponent-floor-percentage_rank']) #1, 2, 3ish
win_breakdown_two_factors(stats = ncaa_history, results = fin_output, factors = ['opponent-floor-percentage_rank', 'floor-percentage_rank']) #1, 2, 3ish
#win_breakdown_two_factors(stats = ncaa_history, results = fin_output, factors = ['effective-field-goal-pct_rank', 'opponent-effective-field-goal-pct_rank']) #1, 2
#win_breakdown_two_factors(stats = ncaa_history, results = fin_output, factors = ['opponent-effective-field-goal-pct_rank', 'effective-field-goal-pct_rank']) #1, 2
#win_breakdown_two_factors(stats = ncaa_history, results = fin_output, factors = ['two-point-pct_rank', 'opponent-two-point-pct_rank']) #1, 2
#win_breakdown_two_factors(stats = ncaa_history, results = fin_output, factors = ['three-point-pct_rank', 'opponent-three-point-pct_rank']) #1
#win_breakdown_two_factors(stats = ncaa_history, results = fin_output, factors = ['true-shooting-percentage_rank', 'opponent-true-shooting-percentage_rank']) #1, 2
#win_breakdown_two_factors(stats = ncaa_history, results = fin_output, factors = ['opponent-true-shooting-percentage_rank', 'true-shooting-percentage_rank']) #1, 2
win_breakdown_two_factors(stats = ncaa_history, results = fin_output, factors = ['ftm-per-100-possessions_rank', 'opponent-ftm-per-100-possessions_rank']) #55%, 1
win_breakdown_two_factors(stats = ncaa_history, results = fin_output, factors = ['offensive-rebounding-pct_rank', 'defensive-rebounding-pct_rank']) #1
win_breakdown_two_factors(stats = ncaa_history, results = fin_output, factors = ['defensive-rebounding-pct_rank', 'offensive-rebounding-pct_rank']) #1
win_breakdown_two_factors(stats = ncaa_history, results = fin_output, factors = ['turnovers-per-possession_rank', 'opponent-turnovers-per-possession_rank']) #1
win_breakdown_two_factors(stats = ncaa_history, results = fin_output, factors = ['opponent-turnovers-per-possession_rank', 'turnovers-per-possession_rank']) #1
win_breakdown_two_factors(stats = ncaa_history, results = fin_output, factors = ['effective-possession-ratio_rank', 'opponent-effective-possession-ratio_rank']) #1
win_breakdown_two_factors(stats = ncaa_history, results = fin_output, factors = ['opponent-effective-possession-ratio_rank', 'effective-possession-ratio_rank']) #1

def win_breakdown_multifactors(stats, results, factors):
    stats = stats.copy()
    results = results.copy()

    stats = stats.reset_index()

    factors = [['floor-percentage_rank', 'opponent-floor-percentage_rank'], ['floor-percentage_rank', 'opponent-floor-percentage_rank']]

    if (type(factors[1]) is str) == False:
        factor_good_a = factors[0][0]
        factor_bad_a = factors[0][1]

        factor_good_b = factors[1][0]
        factor_bad_b = factors[1][1]

        winners = pd.merge(results, stats[['team', 'Date', factor_good_a]], left_on=['DATE', 'WINNER'],
                           right_on=['Date', 'team'], how='left')

        winners = pd.merge(winners, stats[['team', 'Date', factor_bad_a]], left_on=['DATE', 'LOSER'],
                           right_on=['Date', 'team'], how='left')

        winners['two-factor-adv-a'] = winners[factor_bad_a] - winners[factor_good_a]

        winners = winners.drop(columns = [factor_bad_a, factor_good_a])
        
        winners = pd.merge(winners, stats[['team', 'Date', factor_good_b]], left_on=['DATE', 'LOSER'],
                           right_on=['Date', 'team'], how='left')
        
        winners = pd.merge(winners, stats[['team', 'Date', factor_bad_b]], left_on=['DATE', 'WINNER'],
                           right_on=['Date', 'team'], how='left')

        winners['two-factor-adv-b'] = winners[factor_bad_b] - winners[factor_good_b]

        winners = winners.drop(columns=[factor_bad_b, factor_good_b])
        
        winners['multi-factor-adv'] = winners['two-factor-adv-a'] - winners['two-factor-adv-b']

        winners = winners.drop(columns=['two-factor-adv-a', 'two-factor-adv-b'])
        
        winners['WON'] = 1

        winners['MARGIN_OF_VICTORY_ADV'] = winners['MARGIN_OF_VICTORY']

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

        losers['MARGIN_OF_VICTORY_ADV'] = -1 * losers['MARGIN_OF_VICTORY']

        results = pd.concat([winners, losers]).reset_index(drop = True)

        results['ADV'] = results['multi-factor-adv']

        #results['ADV'] = results['ADV'].abs()

        results['ADV_BUCKET'] = results['ADV'].transform(
            lambda x: pd.qcut(x, 20, duplicates='drop', labels=False))

        #print("Percentage of Games Won by Team with Advantage:", results['WON'].mean())
        print("Break Points for Baskets:", results.groupby('ADV_BUCKET')['ADV'].describe()[['min', 'max']])
        print("Percentage of Games Won by Team with Cascading Advantage Size:",
              results.groupby('ADV_BUCKET')['WON'].mean())
        print("Margin of Victory with Cascading Advantage Size: \n",
              results.groupby('ADV_BUCKET')['MARGIN_OF_VICTORY_ADV'].describe())


win_breakdown_multifactors(ncaa_history, fin_output, [['floor-percentage_rank', 'opponent-floor-percentage_rank'], ['floor-percentage_rank', 'opponent-floor-percentage_rank']]) #1, 2, 3
win_breakdown_multifactors(ncaa_history, fin_output, [['ftm-per-100-possessions_rank', 'opponent-ftm-per-100-possessions_rank'], ['ftm-per-100-possessions_rank', 'opponent-ftm-per-100-possessions_rank']]) #1, 2ish
win_breakdown_multifactors(ncaa_history, fin_output, [['offensive-rebounding-pct_rank', 'defensive-rebounding-pct_rank'], ['offensive-rebounding-pct_rank', 'defensive-rebounding-pct_rank']]) #1, 2
win_breakdown_multifactors(ncaa_history, fin_output, [['turnovers-per-possession_rank', 'opponent-turnovers-per-possession_rank'], ['turnovers-per-possession_rank', 'opponent-turnovers-per-possession_rank']]) #1, 2ish
win_breakdown_multifactors(ncaa_history, fin_output, [['effective-possession-ratio_rank', 'opponent-effective-possession-ratio_rank'], ['effective-possession-ratio_rank', 'opponent-effective-possession-ratio_rank']]) #1, 2


def factor_overlap(stats_data, results_data, factors, output = False):
    stats = stats_data.copy()
    results = results_data.copy()

    stats = stats.reset_index()

    if (type(factors[1]) is str) == False:
        factor_good_a = factors[0][0]
        factor_bad_a = factors[0][1]

        factor_good_b = factors[1][0]
        factor_bad_b = factors[1][1]

        results = pd.merge(results, stats[['team', 'Date', factor_good_a]], left_on=['DATE', 'WINNER'],
                           right_on=['Date', 'team'], how='left')

        results = pd.merge(results, stats[['team', 'Date', factor_bad_a]], left_on=['DATE', 'LOSER'],
                           right_on=['Date', 'team'], how='left')

        results['two-factor-adv-a'] = results[factor_bad_a] - results[factor_good_a]

        results = results.drop(columns = [factor_bad_a, factor_good_a])

        results = pd.merge(results, stats[['team', 'Date', factor_good_b]], left_on=['DATE', 'WINNER'],
                           right_on=['Date', 'team'], how='left')

        results = pd.merge(results, stats[['team', 'Date', factor_bad_b]], left_on=['DATE', 'LOSER'],
                           right_on=['Date', 'team'], how='left')

        results['two-factor-adv-b'] = results[factor_bad_b] - results[factor_good_b]

        results = results.drop(columns=[factor_bad_b, factor_good_b])

        results = results[['DATE', 'WINNER', 'LOSER', 'PTS_WINNER', 'PTS_LOSER', 'MARGIN_OF_VICTORY', 'two-factor-adv-a',
                           'two-factor-adv-b']]

        results = results.dropna().reset_index(drop=True)

        results['ADV_A_WON'] = [1 if results['two-factor-adv-a'][x] > 0 else 0 for x in range(len(results['WINNER']))]

        results['ADV_A'] = results['two-factor-adv-a']

        #results['ADV_A'] = results['ADV_A'].abs()

        results['ADV_A_BUCKET'] = results['ADV_A'].transform(
            lambda x: pd.qcut(x, 5, duplicates='drop', labels=False))

        results['MARGIN_OF_VICTORY_ADV_A'] = [results['MARGIN_OF_VICTORY'][x] if results['ADV_A_WON'][x] == 1
                                              else -1 * results['MARGIN_OF_VICTORY'][x]
                                              for x in range(len(results['WINNER']))]

        results['ADV_B_WON'] = [1 if results['two-factor-adv-b'][x] > 0 else 0 for x in range(len(results['WINNER']))]

        results['ADV_B'] = results['two-factor-adv-b']

        #results['ADV_B'] = results['ADV_B'].abs()

        results['ADV_B_BUCKET'] = results['ADV_B'].transform(
            lambda x: pd.qcut(x, 5, duplicates='drop', labels=False))

        results['MARGIN_OF_VICTORY_ADV_B'] = [results['MARGIN_OF_VICTORY'][x] if results['ADV_B_WON'][x] == 1
                                              else -1 * results['MARGIN_OF_VICTORY'][x]
                                              for x in range(len(results['WINNER']))]


    elif (type(factors[0]) is str) == False:

        print('YES')
        factor_good = factors[0][0]
        factor_bad = factors[0][1]

        results = pd.merge(results, stats[['team', 'Date', factor_good]], left_on=['DATE', 'WINNER'],
                           right_on=['Date', 'team'], how='left')

        results = pd.merge(results, stats[['team', 'Date', factor_bad]], left_on=['DATE', 'LOSER'],
                           right_on=['Date', 'team'], how='left')

        results['two-factor-adv'] = results[factor_bad] - results[factor_good]

        results = results.drop(columns = [factor_good, factor_bad])

        results = pd.merge(results, stats[['team', 'Date', factors[1]]], left_on=['DATE', 'WINNER'],
                           right_on=['Date', 'team'], how='left')

        results = pd.merge(results, stats[['team', 'Date', factors[1]]], left_on=['DATE', 'LOSER'],
                           right_on=['Date', 'team'], how='left')

        results = results[['DATE', 'WINNER', 'LOSER', 'PTS_WINNER', 'PTS_LOSER', 'MARGIN_OF_VICTORY', 'two-factor-adv',
                           factors[1] + '_x', factors[1] + '_y']]

        results.columns = ['DATE', 'WINNER', 'LOSER', 'PTS_WINNER', 'PTS_LOSER', 'MARGIN_OF_VICTORY', 'two-factor-adv',
                           factors[1] + '_WINNER', factors[1] + '_LOSER']

        results = results.dropna().reset_index(drop=True)

        results['ADV_A_WON'] = [1 if results['two-factor-adv'][x] > 0 else 0 for x in range(len(results['WINNER']))]

        results['ADV_A'] = results['two-factor-adv']

        #results['ADV_A'] = results['ADV_A'].abs()

        results['ADV_A_BUCKET'] = results['ADV_A'].transform(
            lambda x: pd.qcut(x, 5, duplicates='drop', labels=False))

        results['MARGIN_OF_VICTORY_ADV_A'] = [results['MARGIN_OF_VICTORY'][x] if results['ADV_A_WON'][x] == 1
                                              else -1 * results['MARGIN_OF_VICTORY'][x]
                                              for x in range(len(results['WINNER']))]

        results['ADV_B_WON'] = [1 if results[factors[1] + '_WINNER'][x] < results[factors[1] + '_LOSER'][x] else 0
                                for x in range(len(results['WINNER']))]

        results['ADV_B'] = results[factors[1] + '_LOSER'] - results[factors[1] + '_WINNER']

        results['ADV_B'] = results['ADV_B'].abs()

        results['ADV_B_BUCKET'] = results['ADV_B'].transform(
            lambda x: pd.qcut(x, 5, duplicates='drop', labels=False))

        results['MARGIN_OF_VICTORY_ADV_B'] = [results['MARGIN_OF_VICTORY'][x] if results['ADV_B_WON'][x] == 1
                                              else -1 * results['MARGIN_OF_VICTORY'][x]
                                              for x in range(len(results['WINNER']))]


    else:

        results = pd.merge(results, stats[['team', 'Date', factors[0]]], left_on=['DATE', 'WINNER'],
                           right_on=['Date', 'team'], how='left')

        results = pd.merge(results, stats[['team', 'Date', factors[0]]], left_on=['DATE', 'LOSER'],
                           right_on=['Date', 'team'], how='left')

        results = pd.merge(results, stats[['team', 'Date', factors[1]]], left_on=['DATE', 'WINNER'],
                           right_on=['Date', 'team'], how='left')

        results = pd.merge(results, stats[['team', 'Date', factors[1]]], left_on=['DATE', 'LOSER'],
                           right_on=['Date', 'team'], how='left')

        results = results[['DATE', 'WINNER', 'LOSER', 'PTS_WINNER', 'PTS_LOSER', 'MARGIN_OF_VICTORY',
                           factors[0] + '_x', factors[0] + '_y', factors[1] + '_x', factors[1] + '_y']]

        results.columns = ['DATE', 'WINNER', 'LOSER', 'PTS_WINNER', 'PTS_LOSER', 'MARGIN_OF_VICTORY',
                           factors[0] + '_WINNER', factors[0] + '_LOSER', factors[1] + '_WINNER', factors[1] + '_LOSER']

        results = results.dropna().reset_index(drop=True)

        results['ADV_A_WON'] = [1 if results[factors[0] + '_WINNER'][x] < results[factors[0] + '_LOSER'][x] else 0
                                for x in range(len(results['WINNER']))]

        results['ADV_A'] = results[factors[0] + '_LOSER'] - results[factors[0] + '_WINNER']

        results['ADV_A'] = results['ADV_A'].abs()

        results['ADV_A_BUCKET'] = results['ADV_A'].transform(
            lambda x: pd.qcut(x, 5, duplicates='drop', labels=False))

        results['MARGIN_OF_VICTORY_ADV_A'] = [results['MARGIN_OF_VICTORY'][x] if results['ADV_A_WON'][x] == 1
                                              else -1 * results['MARGIN_OF_VICTORY'][x]
                                              for x in range(len(results['WINNER']))]

        results['ADV_B_WON'] = [1 if results[factors[1] + '_WINNER'][x] < results[factors[1] + '_LOSER'][x] else 0
                                for x in range(len(results['WINNER']))]

        results['ADV_B'] = results[factors[1] + '_LOSER'] - results[factors[1] + '_WINNER']

        results['ADV_B'] = results['ADV_B'].abs()

        results['ADV_B_BUCKET'] = results['ADV_B'].transform(
            lambda x: pd.qcut(x, 5, duplicates='drop', labels=False))

        results['MARGIN_OF_VICTORY_ADV_B'] = [results['MARGIN_OF_VICTORY'][x] if results['ADV_B_WON'][x] == 1
                                              else -1 * results['MARGIN_OF_VICTORY'][x]
                                              for x in range(len(results['WINNER']))]

    results['ADV_OVERLAP'] = results['ADV_A_WON'] == results['ADV_B_WON']

    print("Percentage of Games Won by Team with Advantage A:", results['ADV_A_WON'].mean())
    print("Percentage of Games Won by Team with Advantage B:", results['ADV_B_WON'].mean())
    print("Correlation Between MOV by Factor:", results[['MARGIN_OF_VICTORY_ADV_A', 'MARGIN_OF_VICTORY_ADV_B']].corr())
    print("Percentage of Games with Same Outcome by Factor:", results['ADV_OVERLAP'].sum() / len(results['ADV_OVERLAP']))
    print("Correlation Between Factors:", results[['ADV_A', 'ADV_B']].corr())

    adv_a = results.groupby(['ADV_A_BUCKET', 'ADV_B_BUCKET'])['ADV_A_WON'].mean()
    adv_a_mov = results.groupby(['ADV_A_BUCKET', 'ADV_B_BUCKET'])['MARGIN_OF_VICTORY_ADV_A'].describe()
    adv_b = results.groupby(['ADV_B_BUCKET', 'ADV_A_BUCKET'])['ADV_B_WON'].mean()
    adv_b_mov = results.groupby(['ADV_B_BUCKET', 'ADV_A_BUCKET'])['MARGIN_OF_VICTORY_ADV_B'].describe()


    if output == True:
        return([adv_a, adv_a_mov, adv_b, adv_b_mov])

factor_overlap(ncaa_history, fin_output, [['offensive-efficiency_rank', 'defensive-efficiency_rank'], 'offensive-efficiency_rank']) # -0.11, 0.24, 0.63
factor_overlap(ncaa_history, fin_output, [['defensive-efficiency_rank', 'offensive-efficiency_rank'], ['opponent-floor-percentage_rank', 'floor-percentage_rank']]) # 0.83, 0.79, 0.88
factor_overlap(ncaa_history, fin_output, [['offensive-efficiency_rank', 'defensive-efficiency_rank'], ['defensive-efficiency_rank', 'offensive-efficiency_rank']]) # 0.09, 0.24, 0.55
factor_overlap(ncaa_history, fin_output, [['floor-percentage_rank', 'opponent-floor-percentage_rank'], 'floor-percentage_rank']) # 0.36, 0.52, 0.73
factor_overlap(ncaa_history, fin_output, [['effective-field-goal-pct_rank', 'opponent-effective-field-goal-pct_rank'], 'effective-field-goal-pct_rank']) # 0.22, 0.42, 0.69
factor_overlap(ncaa_history, fin_output, [['two-point-pct_rank', 'opponent-two-point-pct_rank'], 'two-point-pct_rank']) # 0.25, 0.45, 0.70
factor_overlap(ncaa_history, fin_output, [['three-point-pct_rank', 'opponent-three-point-pct_rank'], 'three-point-pct_rank']) # 0.1, 0.33, 0.66
factor_overlap(ncaa_history, fin_output, [['true-shooting-percentage_rank', 'opponent-true-shooting-percentage_rank'], 'true-shooting-percentage_rank']) # 0.24, 0.42, 0.69
factor_overlap(ncaa_history, fin_output, [['ftm-per-100-possessions_rank', 'opponent-ftm-per-100-possessions_rank'], 'ftm-per-100-possessions_rank']) # 0.11, 0.33, 0.66
factor_overlap(ncaa_history, fin_output, [['defensive-rebounding-pct_rank', 'offensive-rebounding-pct_rank'], 'defensive-rebounding-pct_rank']) # 0.19, 0.40, 0.68
factor_overlap(ncaa_history, fin_output, [['effective-possession-ratio_rank', 'opponent-effective-possession-ratio_rank'], 'effective-possession-ratio_rank']) # 0.13, 0.39, 0.68

factor_overlap(ncaa_history, fin_output, [['offensive-efficiency_rank', 'defensive-efficiency_rank'], ['floor-percentage_rank', 'opponent-floor-percentage_rank']]) # 0.83, 0.80, 0.88
factor_overlap(ncaa_history, fin_output, [['floor-percentage_rank', 'opponent-floor-percentage_rank'], 'offensive-efficiency_rank']) # 0.28, 0.47, 0.70
factor_overlap(ncaa_history, fin_output, [['floor-percentage_rank', 'opponent-floor-percentage_rank'], ['effective-field-goal-pct_rank', 'opponent-effective-field-goal-pct_rank']]) # 0.49, 0.56, 0.76
factor_overlap(ncaa_history, fin_output, [['floor-percentage_rank', 'opponent-floor-percentage_rank'], ['two-point-pct_rank', 'opponent-two-point-pct_rank']]) # 0.46, 0.53, 0.75
factor_overlap(ncaa_history, fin_output, [['floor-percentage_rank', 'opponent-floor-percentage_rank'], ['three-point-pct_rank', 'opponent-three-point-pct_rank']]) # 0.19, 0.32, 0.65
factor_overlap(ncaa_history, fin_output, [['floor-percentage_rank', 'opponent-floor-percentage_rank'], ['true-shooting-percentage_rank', 'opponent-true-shooting-percentage_rank']]) # 0.54, 0.58, 0.78
factor_overlap(ncaa_history, fin_output, [['floor-percentage_rank', 'opponent-floor-percentage_rank'], ['ftm-per-100-possessions_rank', 'opponent-ftm-per-100-possessions_rank']]) # 0.18, 0.29, 0.65
factor_overlap(ncaa_history, fin_output, [['floor-percentage_rank', 'opponent-floor-percentage_rank'], ['defensive-rebounding-pct_rank', 'offensive-rebounding-pct_rank']]) # 0.09, 0.23, 0.59
factor_overlap(ncaa_history, fin_output, [['floor-percentage_rank', 'opponent-floor-percentage_rank'], ['effective-possession-ratio_rank', 'opponent-effective-possession-ratio_rank']]) # 0.16, 0.36, 0.65
factor_overlap(ncaa_history, fin_output, [['effective-possession-ratio_rank', 'opponent-effective-possession-ratio_rank'], ['three-point-pct_rank', 'opponent-three-point-pct_rank']]) # 0.01, 0.01, 0.49
factor_overlap(ncaa_history, fin_output, [['defensive-rebounding-pct_rank', 'offensive-rebounding-pct_rank'], 'offensive-rebounding-pct_rank']) # 0.23, 0.40, 0.69
factor_overlap(ncaa_history, fin_output, [['opponent-floor-percentage_rank', 'floor-percentage_rank'], ['opponent-effective-field-goal-pct_rank', 'effective-field-goal-pct_rank']]) # 0.48, 0.56, 0.76
factor_overlap(ncaa_history, fin_output, [['opponent-floor-percentage_rank', 'floor-percentage_rank'], ['opponent-effective-field-goal-pct_rank', 'effective-field-goal-pct_rank']]) # 0.48, 0.56, 0.76
factor_overlap(ncaa_history, fin_output, [['opponent-floor-percentage_rank', 'floor-percentage_rank'], ['opponent-true-shooting-percentage_rank', 'true-shooting-percentage_rank']]) # 0.54, 0.59, 0.78
factor_overlap(ncaa_history, fin_output, [['opponent-floor-percentage_rank', 'floor-percentage_rank'], ['floor-percentage_rank', 'opponent-floor-percentage_rank']]) # 0.13, 0.29, 0.59
factor_overlap(ncaa_history, fin_output, [['opponent-floor-percentage_rank', 'floor-percentage_rank'], 'opponent-three-point-pct_rank']) # 0.07, 0.21, 0.55
factor_overlap(ncaa_history, fin_output, [['opponent-floor-percentage_rank', 'floor-percentage_rank'], ['defensive-efficiency_rank', 'offensive-efficiency_rank']]) # 0.83, 0.78, 0.88
factor_overlap(ncaa_history, fin_output, [['opponent-floor-percentage_rank', 'floor-percentage_rank'], ['turnovers-per-possession_rank', 'opponent-turnovers-per-possession_rank']]) # 0.00, 0.11, 0.53
factor_overlap(ncaa_history, fin_output, [['opponent-floor-percentage_rank', 'floor-percentage_rank'], ['opponent-effective-possession-ratio_rank', 'effective-possession-ratio_rank']]) # 0.00, 0.11, 0.53
factor_overlap(ncaa_history, fin_output, [['opponent-turnovers-per-possession_rank', 'turnovers-per-possession_rank'], ['turnovers-per-possession_rank', 'opponent-turnovers-per-possession_rank']]) # 0.15, 0.30, 0.63
factor_overlap(ncaa_history, fin_output, [['opponent-effective-possession-ratio_rank', 'effective-possession-ratio_rank'], ['effective-possession-ratio_rank', 'opponent-effective-possession-ratio_rank']]) # 0.02, 0.09, 0.51

factor_overlap(ncaa_history, fin_output, [['turnovers-per-possession_rank', 'opponent-turnovers-per-possession_rank'], 'turnovers-per-possession_rank']) # 0.09, 0.35, 0.66
factor_overlap(ncaa_history, fin_output, [['turnovers-per-possession_rank', 'opponent-turnovers-per-possession_rank'], 'opponent-turnovers-per-possession_rank']) # 0.12, 0.33, 0.66

factor_overlap(ncaa_history, fin_output, [['turnovers-per-possession_rank', 'opponent-turnovers-per-possession_rank'], 'schedule-strength-by-other_rank']) # 0.00, 0.15, 0.56
factor_overlap(ncaa_history, fin_output, ['predictive-by-other_rank', 'schedule-strength-by-other_rank']) # 0.48, 0.53, 0.76

factor_overlap(ncaa_history, fin_output, [['floor-percentage_rank', 'opponent-floor-percentage_rank'], ['opponent-floor-percentage_rank', 'floor-percentage_rank']]) # 0.13, 0.29, 0.59
factor_overlap(ncaa_history, fin_output, [['defensive-rebounding-pct_rank', 'offensive-rebounding-pct_rank'], ['offensive-rebounding-pct_rank', 'defensive-rebounding-pct_rank']]) # 0.01, 0.09, 0.52