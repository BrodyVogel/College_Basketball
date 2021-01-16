from get_data import *

# get data for today
for_today = get_data_ncaam('2021-01-16', attributes = {'offensive-efficiency': 'desc',
                                                'floor-percentage': 'desc',
                                                'effective-field-goal-pct': 'desc',
                                                'two-point-pct': 'desc',
                                                'three-point-pct': 'desc',
                                                'true-shooting-percentage': 'desc',
                                                'ftm-per-100-possessions': 'desc',
                                                'predictive-by-other': 'desc',
                                                'schedule-strength-by-other': 'desc',
                                                'offensive-rebounding-pct': 'desc',
                                                'defensive-rebounding-pct': 'desc',
                                                'turnovers-per-possession': 'asc',
                                                'defensive-efficiency': 'asc',
                                                'opponent-floor-percentage': 'asc',
                                                'opponent-effective-field-goal-pct': 'asc',
                                                'opponent-two-point-pct': 'asc',
                                                'opponent-three-point-pct': 'asc',
                                                'opponent-true-shooting-percentage': 'asc',
                                                'opponent-ftm-per-100-possessions': 'asc',
                                                'opponent-turnovers-per-possession': 'desc',
                                                'effective-possession-ratio': 'desc',
                                                'opponent-effective-possession-ratio': 'asc'
                                               })

# names for indexing
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

# apply name fix
for_today = for_today.reset_index()
for x in range(len(for_today['team'])):
    try:
        for_today.loc[x, 'team'] = proper_names[for_today['team'][x]]
    except:
        for_today.loc[x, 'team'] = for_today.loc[x, 'team']

# reset index
for_today = for_today.set_index('team')

# get games for today
today = get_ncaa_schedule('2021-01-16')

# apply name fix
for x in range(len(today['Home Team'])):
    try:
        today.loc[x, 'Home Team'] = proper_names[today['Home Team'][x]]
    except:
        today.loc[x, 'Home Team'] = today['Home Team'][x]

    try:
        today.loc[x, 'Away Team'] = proper_names[today['Away Team'][x]]
    except:
        today.loc[x, 'Away Team'] = today['Away Team'][x]

# deprecated factor policy
factor_policy_dep = {
    "predictive-by-other_rank":
        {"one_point": [34, 48],
         "two_points": [82.5, 104.5],
         "three_points": [134, 177],
         "two_fac": None},

    "three-point-pct_rank":
        {"one_point": [183, 228],
         "two_points": [400, 500],
         "three_points": None,
         "two_fac": None},

    "opponent-three-point-pct_rank":
        {"one_point": [179.5, 222.5],
         "two_points": [400, 500],
         "three_points": None,
         "two_fac": None},

    "offensive-floor-percentage-advantage":
        {"one_point": [108, 134.5],
         "two_points": [167.5, 211.5],
         "three_points": [212, 345],
         "two_fac": ['floor-percentage_rank', 'opponent-floor-percentage_rank']},

    "defensive-floor-percentage-advantage":
        {"one_point": [80, 101.5],
         "two_points": [160, 204],
         "three_points": [204.5, 346],
         "two_fac": ['opponent-floor-percentage_rank', 'floor-percentage_rank']},

    "ftm_advantage":
        {"one_point": [232.5, 349],
         "two_points": [500, 600],
         "three_points": None,
         "two_fac": ['ftm-per-100-possessions_rank', 'opponent-ftm-per-100-possessions_rank']},

    "offensive_rebounding_advantage":
        {"one_point": [146, 179.5],
         "two_points": [400, 500],
         "three_points": None,
         "two_fac": ['offensive-rebounding-pct_rank', 'defensive-rebounding-pct_rank']},

    "defensive_rebounding_advantage":
        {"one_point": [195, 239.5],
         "two_points": [400, 500],
         "three_points": None,
         "two_fac": ['defensive-rebounding-pct_rank', 'offensive-rebounding-pct_rank']},

    "forced_turnover_advantage":
        {"one_point": [224, 352],
         "two_points": [400, 500],
         "three_points": None,
         "two_fac": ['opponent-turnovers-per-possession_rank', 'turnovers-per-possession_rank']
         },

    "committed_turnover_advantage":
        {"one_point": [250.5, 349],
         "two_points": [400, 500],
         "three_points": None,
         "two_fac": ['turnovers-per-possession_rank', 'opponent-turnovers-per-possession_rank']
         },

    "offensive_effective_possession_advantage":
        {"one_point": [201, 246.5],
         "two_points": [400, 500],
         "three_points": None,
         "two_fac": ['effective-possession-ratio_rank', 'opponent-effective-possession-ratio_rank']},

    "defensive_effective_possession_advantage":
        {"one_point": [178.5, 222.5],
         "two_points": [400, 500],
         "three_points": None,
         "two_fac": ['opponent-effective-possession-ratio_rank', 'effective-possession-ratio_rank']}

}

# live factor policy
factor_policy = {
    "predictive-by-other_rank":
        {"one_point": [34, 48],
         "two_points": [82.5, 104.5],
         "three_points": [134, 177],
         "two_fac": None,
         "multi_fac": None},

    "three-point-pct_rank":
        {"one_point": [183, 228],
         "two_points": [4000, 5000],
         "three_points": None,
         "two_fac": None,
         "multi_fac": None},

    "opponent-three-point-pct_rank":
        {"one_point": [179.5, 222.5],
         "two_points": [4000, 5000],
         "three_points": None,
         "two_fac": None,
         "multi_fac": None},

    "floor-percentage-advantage":
        {"one_point": [100.5, 130.5],
         "two_points": [164.5, 202.5],
         "three_points": [255, 328],
         "two_fac": None,
         "multi_fac": [['floor-percentage_rank', 'opponent-floor-percentage_rank'], ['floor-percentage_rank', 'opponent-floor-percentage_rank']]},

    "ftm_advantage":
        {"one_point": [197, 244],
         "two_points": [5000, 6000],
         "three_points": None,
         "two_fac": None,
         "multi_fac": [['ftm-per-100-possessions_rank', 'opponent-ftm-per-100-possessions_rank'], ['ftm-per-100-possessions_rank', 'opponent-ftm-per-100-possessions_rank']]},

    "rebounding_advantage":
        {"one_point": [174, 213],
         "two_points": [333.5, 667],
         "three_points": None,
         "two_fac": None,
         "multi_fac": [['offensive-rebounding-pct_rank', 'defensive-rebounding-pct_rank'], ['offensive-rebounding-pct_rank', 'defensive-rebounding-pct_rank']]},

    "turnover_advantage":
        {"one_point": [207, 253],
         "two_points": [4000, 5000],
         "three_points": None,
         "two_fac": None,
         "multi_fac": [['opponent-turnovers-per-possession_rank', 'turnovers-per-possession_rank'], ['opponent-turnovers-per-possession_rank', 'turnovers-per-possession_rank']]
         },

    "effective_possession_advantage":
        {"one_point": [178.5, 225],
         "two_points": [4000, 5000],
         "three_points": None,
         "two_fac": None,
         "multi_fac": [['effective-possession-ratio_rank', 'opponent-effective-possession-ratio_rank'], ['effective-possession-ratio_rank', 'opponent-effective-possession-ratio_rank']]},

}

# evaluate with model
for row in range(len(today['Home Team'])):
    try:
        evaluate_with_model(for_today, today['Home Team'][row], today['Away Team'][row], factor_policy, scaler, model,
                            spread_target = [nopq3])
    except:
        print("One of", today['Home Team'][row], "or", today['Away Team'][row], "does not have data.")

    print('\n')

# evaluate with simple scoring
for row in range(len(today['Home Team'])):
    try:
        evaluate_v2(for_today, today['Home Team'][row], today['Away Team'][row], magnitude=100,
                    factor_policy=factor_policy, store=False, verbose=True, spread_target=[nopq3],
                grouping='overall')
    except:
        print("One of", today['Home Team'][row], "or", today['Away Team'][row], "does not have data.")
        
    print('\n')


############## JUNK ###############
# reset_fin_output = fin_output.copy()
#
# reset_fin_output['pred_winner'] = 'Neither'
# reset_fin_output['confidence'] = np.nan
# #reset_fin_output['home_team_advantages'] = np.nan
# #reset_fin_output['away_team_advantages'] = np.nan
#
# reset_fin_output['three_advantages'] = np.nan
# reset_fin_output['two_advantages'] = np.nan
# reset_fin_output['one_advantages'] = np.nan
# reset_fin_output['half_advantages'] = np.nan
#
# to_test = reset_fin_output.copy().reset_index(drop = True)
#
# reset_ncaa_history = ncaa_history.copy()
#
# for row in range(len(to_test['WINNER'])):
#     date_to_locate = to_test['DATE'][row]
#     try:
#         to_test.loc[row, 'one_advantages'], to_test.loc[row, 'three_advantages'], to_test.loc[row, 'confidence'],\
#         to_test.loc[row, 'pred_winner'] = evaluate_v2(reset_ncaa_history.loc[(reset_ncaa_history['Date'] == date_to_locate)],
#                  to_test['WINNER'][row], to_test['LOSER'][row], factor_policy=factor_policy, magnitude=100, store=True, grouping = 'overall')
#
#     except:
#         to_test.loc[row, 'three_advantages'] = np.nan
#         to_test.loc[row, 'two_advantages'] = np.nan
#         to_test.loc[row, 'one_advantages'] = np.nan
#         to_test.loc[row, 'half_advantages'] = np.nan
#         to_test.loc[row, 'pred_winner'] = np.nan
#         to_test.loc[row, 'confidence'] = np.nan
#
# to_test_evaluate = to_test.loc[np.isnan(to_test.confidence) == False].reset_index(drop = True)
# to_test_evaluate = to_test_evaluate.loc[to_test_evaluate.pred_winner != 'Neither'].reset_index(drop = True)
#
# to_test_evaluate['MARGIN_OF_VICTORY_pred_winner'] = np.nan
# for x in range(len(to_test_evaluate['WINNER'])):
#     if to_test_evaluate['pred_winner'][x] == to_test_evaluate['WINNER'][x] or to_test_evaluate['pred_winner'][x] == 'Neither':
#         to_test_evaluate.loc[x, 'MARGIN_OF_VICTORY_pred_winner'] = to_test_evaluate['MARGIN_OF_VICTORY'][x]
#     elif type(to_test_evaluate['pred_winner'][x]) == float and np.isnan(to_test_evaluate['pred_winner'][x]) == True:
#         to_test_evaluate.loc[x, 'MARGIN_OF_VICTORY_pred_winner'] = to_test_evaluate['MARGIN_OF_VICTORY'][x]
#     else:
#         to_test_evaluate.loc[x, 'MARGIN_OF_VICTORY_pred_winner'] = -1 * to_test_evaluate['MARGIN_OF_VICTORY'][x]
#
# to_test_evaluate['OPEN_SPREAD_pred_winner'] = [
#     to_test_evaluate['OPEN_SPREAD_WINNER'][x] if to_test_evaluate['pred_winner'][x] == to_test_evaluate['WINNER'][x]
#     else to_test_evaluate['OPEN_SPREAD_LOSER'][x] if to_test_evaluate['pred_winner'][x] == to_test_evaluate['LOSER'][x]
#     else np.nan for x in range(len(to_test_evaluate['DATE']))]
#
# to_test_evaluate['CLOSE_SPREAD_pred_winner'] = [
#     to_test_evaluate['CLOSE_SPREAD_WINNER'][x] if to_test_evaluate['pred_winner'][x] == to_test_evaluate['WINNER'][x]
#     else to_test_evaluate['CLOSE_SPREAD_LOSER'][x] if to_test_evaluate['pred_winner'][x] == to_test_evaluate['LOSER'][x]
#     else np.nan for x in range(len(to_test_evaluate['DATE']))]
#
# to_test_evaluate['COVERED_OPEN_pred_winner'] = np.asarray([
#     np.nan if np.isnan(to_test_evaluate['OPEN_SPREAD_pred_winner'][x]) == True
#     else 1 if (to_test_evaluate['OPEN_SPREAD_pred_winner'][x] > 0) & (to_test_evaluate['pred_winner'][x] == to_test_evaluate['WINNER'][x])
#     else 1 if (to_test_evaluate['MARGIN_OF_VICTORY'][x] > (-1 * to_test_evaluate['OPEN_SPREAD_pred_winner'][x])) & (to_test_evaluate['pred_winner'][x] == to_test_evaluate['WINNER'][x])
#     else 1 if (to_test_evaluate['MARGIN_OF_VICTORY'][x] < (-1 * to_test_evaluate['OPEN_SPREAD_pred_winner'][x])) & (to_test_evaluate['pred_winner'][x] == to_test_evaluate['LOSER'][x])
#     else 0 for x in range(len(to_test_evaluate['DATE']))])
#
# to_test_evaluate['COVERED_CLOSE_pred_winner'] = np.asarray([
#     np.nan if np.isnan(to_test_evaluate['CLOSE_SPREAD_pred_winner'][x]) == True
#     else 1 if (to_test_evaluate['CLOSE_SPREAD_pred_winner'][x] > 0) & (to_test_evaluate['pred_winner'][x] == to_test_evaluate['WINNER'][x])
#     else 1 if (to_test_evaluate['MARGIN_OF_VICTORY'][x] > (-1 * to_test_evaluate['CLOSE_SPREAD_pred_winner'][x])) & (to_test_evaluate['pred_winner'][x] == to_test_evaluate['WINNER'][x])
#     else 1 if (to_test_evaluate['MARGIN_OF_VICTORY'][x] < (-1 * to_test_evaluate['CLOSE_SPREAD_pred_winner'][x])) & (to_test_evaluate['pred_winner'][x] == to_test_evaluate['LOSER'][x])
#     else 0 for x in range(len(to_test_evaluate['DATE']))])
#
# to_test_evaluate.groupby(['grouped_confidence'])['COVERED_OPEN_pred_winner'].mean()
#
# to_test_evaluate['FAVORITE_pred_winner'] = np.asarray([
#     np.nan if np.isnan(to_test_evaluate['CLOSE_SPREAD_pred_winner'][x]) == True
#     else 1 if to_test_evaluate['CLOSE_SPREAD_pred_winner'][x] < 0
#     else 0 for x in range(len(to_test_evaluate['DATE']))])
#
#
# zippy = to_test_evaluate.loc[to_test_evaluate.CLOSE_SPREAD_pred_winner < 0]
# #zippy['CLOSE_SPREAD_pred_winner_DECILE'] = pd.qcut(zippy['CLOSE_SPREAD_pred_winner'], 5, labels = False, duplicates='drop')
# zippy['CLOSE_SPREAD_pred_winner_DECILE'] = zippy.groupby(['grouped_confidence'])['CLOSE_SPREAD_pred_winner'].transform(
#                      lambda x: pd.qcut(x, 5, labels=False))
#
# zippy = zippy.dropna(subset = ['FAVORITE_pred_winner'])
#
# tt = zippy.groupby(['grouped_confidence', 'CLOSE_SPREAD_pred_winner_DECILE'])['COVERED_CLOSE_pred_winner'].describe()
# zt = zippy.groupby(['grouped_confidence', 'CLOSE_SPREAD_pred_winner_DECILE'])['CLOSE_SPREAD_pred_winner'].describe()
# zt = zt.reset_index()[['grouped_confidence', 'CLOSE_SPREAD_pred_winner_DECILE', 'min', 'max']]
# tt = tt.reset_index()[['grouped_confidence', 'CLOSE_SPREAD_pred_winner_DECILE', 'mean']]
#
# at = pd.merge(zt, tt)
#
#
#
# to_test_evaluate['grouped_confidence'] = to_test_evaluate['confidence'].transform(
#                      lambda x: pd.qcut(x, 20, labels = False, duplicates='drop'))
#
# n = to_test_evaluate.groupby(['grouped_confidence'])['MARGIN_OF_VICTORY_pred_winner'].describe(percentiles = [0.05, 0.1, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.75, 0.90, 0.95])
# p = n[['25%', '40%', '50%', '75%', '90%']]
# q = to_test_evaluate.groupby(['grouped_confidence'])['confidence'].describe()[['min', 'max']]
# #o = to_test_evaluate.groupby(['confidence', 'pred_winner_advantages'])['Margin_of_Victory_pred_winner'].describe(percentiles = [0.05, 0.1, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.75, 0.90, 0.95])
#
# q = q.reset_index()
# p = p.reset_index()
#
# nopq3 = pd.merge(q, p)
#
# # Minn, Drake, MO St, SIU,
#
# spreads = pd.read_html('http://m.espn.com/ncb/dailyline', flavor = 'html5lib')[0]
#
# for x in range(len(spreads['FAV'])):
#     try:
#         spreads.loc[x, 'FAV'] = proper_names[spreads['FAV'][x].upper()]
#     except:
#         spreads.loc[x, 'FAV'] = spreads.loc[x, 'FAV']
#
#     try:
#         spreads.loc[x, 'DOG'] = proper_names[spreads['DOG'][x].upper()]
#     except:
#         spreads.loc[x, 'DOG'] = spreads.loc[x, 'DOG']
#
# spreads = spreads.replace('--', np.nan)
#spreads = spreads.replace('', np.nan)