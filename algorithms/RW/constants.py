INFLUENCE_RADIUS = 2
TORUS = False

#Location Parameters
N = 50
M = 50

#Home Location
HOME_LOC = ((23, 26), (23, 26)) # ((23, 26), (23, 26))

#Tasks and Agents
NUM_AGENTS = 50
K = 0.5
TOTAL_DEMAND = int(NUM_AGENTS*K)
NUM_TASKS = 4
TIME_PER_DEMAND = 5
EXPECTED_TIME_UNTIL_TASK = 20000



EXPECTED_DEMAND_PER_TASK = TOTAL_DEMAND/NUM_TASKS
assert(NUM_TASKS >= 1)
assert(EXPECTED_DEMAND_PER_TASK >= 1)

#General Constants
INF = 1000000000

#TAHH 
L = 1/100

#Levy Flight Constants
levy_loc = 10
levy_cap = 1/L



'''
FOR VISUALS
'''
# INFLUENCE_RADIUS = 2
# TORUS = False

# #Location Parameters
# N = 8
# M = 16

# #Home Location
# HOME_LOC = ((4,5), (4,5)) #((23,26), (23,26)) # ((23, 26), (23, 26))

# #Tasks and Agents
# NUM_AGENTS = 10
# K = 1
# TOTAL_DEMAND = int(NUM_AGENTS*K)
# NUM_TASKS = 4
# TIME_PER_DEMAND = 5
# EXPECTED_TIME_UNTIL_TASK = 1000

# EXPECTED_DEMAND_PER_TASK = TOTAL_DEMAND/NUM_TASKS
# assert(NUM_TASKS >= 1)
# assert(EXPECTED_DEMAND_PER_TASK >= 1)

# #General Constants
# INF = 1000000000

# #TAHH
# L = 1/10

# #Levy Flight Constants
# levy_loc = 5
# levy_cap = 1/L
