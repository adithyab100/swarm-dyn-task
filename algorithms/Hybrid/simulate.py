graphics_on = False

if graphics_on:
    import pygame
    from ViewController import ViewController
from Configuration import Configuration
from constants import TORUS, N, M, NUM_AGENTS, NUM_TASKS, TOTAL_DEMAND, HOME_LOC, NUM_AGENTS
from random import randint
from VertexState import VertexState
import multiprocessing as mp
from matplotlib import pyplot as plt
import time
import numpy as np
from multiprocessing import Pool
import pickle
from functools import partial




def main(params, run_num):
    N, M, max_prop_rad, prop_timeout, expected_demand_per_task, expected_time_until_task, time_per_demand, prop_ratio = params
    NUM_PROP_AGENTS = int(NUM_AGENTS*prop_ratio)
    NUM_RANDOM_AGENTS = NUM_AGENTS - NUM_PROP_AGENTS

    configuration = Configuration(N, M, max_prop_rad, prop_timeout, expected_demand_per_task, expected_time_until_task, time_per_demand, TORUS)
    home = VertexState(is_home=True)

    for x in range(HOME_LOC[0][0], HOME_LOC[0][1]+1):
        for y in range(HOME_LOC[1][0], HOME_LOC[1][1]+1):
            configuration.vertices[(x,y)].state = VertexState(is_home=True)

    tasks = []
    task_locations = set()

    # Initialize agents
    agent_locations = []
    types = []
    for x in range(M):
        for y in range(N):
            agent_locations.append((x,y))
            types.append("Propagator")

    for i in range(NUM_PROP_AGENTS):
        agent_locations.append((randint(HOME_LOC[0][0], HOME_LOC[0][1]), randint(HOME_LOC[1][0], HOME_LOC[1][1])))
        types.append("Follower")

    for i in range(NUM_RANDOM_AGENTS):
        agent_locations.append((randint(HOME_LOC[0][0], HOME_LOC[0][1]), randint(HOME_LOC[1][0], HOME_LOC[1][1])))
        types.append("RandomWalker")



    configuration.add_agents(agent_locations, types)
    if graphics_on:
        vc = ViewController(configuration)
   
    t = int(N/2 + M/2)  # Time at start for propagator agents to get to assigned vertex

    def get_average_total_demand():
        total_demand = 0
        for x in range(M):
            for y in range(N):
                if configuration.vertices[(x,y)].state.is_task:
                    total_demand += configuration.vertices[(x,y)].state.residual_demand
        return total_demand


    total_demand = 0
    total_demand_over_time = []


    while True:
        # print(t)
        t+=1
        # time.sleep(0.1)
        configuration.transition()
        if graphics_on:
            vc.update()

        total_demand += get_average_total_demand()
        total_demand_over_time.append(total_demand/t)

        if t > 2000:
            break


    if graphics_on:
        vc.quit()
    
    return total_demand_over_time, sum(configuration.task_completion_times)/len(configuration.task_completion_times)

if __name__ == "__main__":
    main([50,50,25,3,6,20000,5, 0.95],0)





