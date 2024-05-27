import time

graphics_on = False

if graphics_on:
    import pygame
    from ViewController import ViewController
from Configuration import Configuration
from constants import TORUS, N, M, NUM_AGENTS, NUM_TASKS, TOTAL_DEMAND, HOME_LOC
from random import randint
from VertexState import VertexState
import multiprocessing as mp
import numpy as np
from matplotlib import pyplot as plt
from multiprocessing import Pool
import pickle
from functools import partial




def main(params, run_num):
    expected_demand_per_task, expected_time_until_task, time_per_demand = params
    configuration  = Configuration(N, M, expected_demand_per_task, expected_time_until_task, time_per_demand, TORUS)
    home = VertexState(is_home=True)

    for x in range(HOME_LOC[0][0], HOME_LOC[0][1]+1):
        for y in range(HOME_LOC[1][0], HOME_LOC[1][1]+1):
            configuration.vertices[(x,y)].state = VertexState(is_home=True)

    tasks = []
    task_locations = set()

    # Initialize agents
    agent_locations = []
    for i in range(NUM_AGENTS):
        agent_locations.append((randint(HOME_LOC[0][0], HOME_LOC[0][1]), randint(HOME_LOC[1][0], HOME_LOC[1][1])))

    configuration.add_agents(agent_locations)
    if graphics_on:
        vc = ViewController(configuration)

    t = 0

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
        t+=1
        configuration.transition()
        if graphics_on:
            vc.update()
        
        total_demand += get_average_total_demand()
        total_demand_over_time.append(total_demand/t)
        
        if t % 100 == 0:
            print("Average total demand: ", total_demand/t)
            if len(configuration.task_completion_times) > 0:
                print("Average task completion time: ", sum(configuration.task_completion_times)/len(configuration.task_completion_times))
        
        if t > 2000:
            break

        # time.sleep(0.1)

    if graphics_on:
        vc.quit()

    
    return total_demand_over_time, sum(configuration.task_completion_times)/len(configuration.task_completion_times)

