graphics_on = False #True #True

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
    # for i in range(NUM_TASKS):
    #     task_location = (randint(0,M-1), randint(0,N-1))
    #     while task_location in task_locations or configuration.vertices[task_location].state.is_home:
    #         task_location = (randint(0, M-1), randint(0, N-1))

    #     tasks.append(VertexState(is_task=True, demand=1, task_location=task_location))
    #     task_locations.add(task_location)

    # for i in range(TOTAL_DEMAND-NUM_TASKS):
    #     task_num = randint(0, NUM_TASKS-1)
    #     tasks[task_num].demand += 1
    #     tasks[task_num].residual_demand += 1


    # for task_state in tasks:
    #     configuration.vertices[task_state.task_location].state = task_state


    # for x in range(M):
    #     for y in range(N):
    #         if not configuration.vertices[(x,y)].state.is_home:
    #             configuration.vertices[(x,y)].state = VertexState(is_task=True, demand=0, task_location=(x,y), next_task_time = randint(1,500))


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

    #configuration.vertices[(17,16)].state = VertexState(is_task=True, demand=3, task_location=(17,16))


    configuration.add_agents(agent_locations, types)
    if graphics_on:
        vc = ViewController(configuration)
    # ct = 0
    # tot_rd = NUM_TASKS
    # residual_demand_over_time = []
    # while tot_rd > 0:
    #     ct+=1
    #     configuration.transition()
    #     if graphics_on:
    #         vc.update()
    #     tot_rd = 0
    #     for task in tasks:
    #         tot_rd += task.residual_demand
    #     residual_demand_over_time.append(tot_rd)
    # print(len(residual_demand_over_time))

    # plt.plot(residual_demand_over_time)
    # plt.savefig("residual_demand_over_time.pdf")
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

        # if t % 100 == 0:
            # print("Average total demand: ", total_demand/t)
        #     if len(configuration.task_completion_times) > 0:
        #         print("Average task completion time", sum(configuration.task_completion_times)/len(configuration.task_completion_times))

        if t > 2000:
            break


    if graphics_on:
        vc.quit()

    # '''make plot look nice'''
    # plt.xlabel("Time")
    # plt.ylabel("Average Total Demand")
    # plt.plot(total_demand_over_time)
    # plt.savefig("total_demand_over_time.pdf")

    # '''save data'''
    # f = open("total_demand_over_time.txt", "w")
    # for i in total_demand_over_time:
    #     f.write(str(i)+"\n")
    
    # print(run_num, sum(configuration.task_completion_times)/len(configuration.task_completion_times))
    
    return total_demand_over_time, sum(configuration.task_completion_times)/len(configuration.task_completion_times)

def main_wrapper(n):
    return main([50,50,25,3, 6, 20000, 5, 0.2], n)

def get_main_wrapper(params, n):
    return main(params, n)
    

if __name__ == "__main__":


    # main([50,50,25,3,6,20000,5, 0.95],0)
    # main([50,50,25,3, 6, 10000,5], 0)
    # main([50,50,25,3, 6, 20000, 5],0)
    # for i in range(10):
    #     total_demand_over_time = main([20,20,25,3], 1)
    #     plt.plot(total_demand_over_time)
    #     plt.savefig("alg1/results/total_demand_over_time"+str(i)+".pdf")
    #     plt.clf()

    # main([12,12,25,2],1,0)

    # main([50,50,25,3,6,100000, 5], 0)

    
    trials = 50

    task_rates = [90000, 50000, 30000]
    prop_rates = [0.2, 0.4, 0.6, 0.8]


    for prop_rate in prop_rates:
        for task_rate in task_rates:
            file  = open("hybrid/results/prop_task_rate.txt", 'a')
            print(prop_rate, task_rate)
            results_prop = []
            results = []
            with Pool() as pool:
                params = [50,50,25,3,6,task_rate, 5, prop_rate]
                partial_function = partial(get_main_wrapper, params)

                results = pool.map(partial_function, range(trials))
                #results_prop.append(results[0])

            results_prop = [x[0] for x in results]
            times = [x[1] for x in results]
            print(len(times))
            avg_demand_prop = np.mean(results_prop, axis = 0)
            error_prop = np.std(results_prop, axis = 0)

            converged = False
            if abs(avg_demand_prop[-200] - avg_demand_prop[-1]) < 0.25:
                converged = True

            file.write(f"{prop_rate} {task_rate}: {avg_demand_prop[-1]} {error_prop[-1]} {np.mean(times)} {np.std(times)} {converged}, average of {len(times)} runs\n")
            file.close()
    

    # time_per_demand_vals = [20, 15, 10, 5, 4, 3, 2, 1]

    # for i in time_per_demand_vals:
    #     file  = open("alg1_nobleEdit_1126/results/vary_timeperdemand_llsub.txt", 'a')
    #     print(i)
    #     results_prop = []
    #     results = []
    #     with Pool() as pool:
    #         params = [50,50,25,3,6,50000, i]
    #         partial_function = partial(get_main_wrapper, params)

    #         results = pool.map(partial_function, range(trials))
    #         #results_prop.append(results[0])

    #     results_prop = [x[0] for x in results]
    #     times = [x[1] for x in results]
    #     print(len(times))
    #     avg_demand_prop = np.mean(results_prop, axis = 0)
    #     error_prop = np.std(results_prop, axis = 0)

    #     converged = False
    #     if abs(avg_demand_prop[-200] - avg_demand_prop[-1]) < 0.25:
    #          converged = True

    #     file.write(f"{i} {avg_demand_prop[-1]} {error_prop[-1]} {np.mean(times)} {np.std(times)} {converged}, average of {len(times)} runs\n")
    #     file.close()
        

    # with Pool() as pool:

    #     results = pool.map(main_wrapper, range(N))
    #     # results_rw.append(a[0])


    # results_prop = [x[0] for x in results]
    # times = [x[1] for x in results]

    # print(len(results_prop), len(results_prop[0]))
    # # Calculate average total demand and error bars for RW algorithm
    # avg_demand_prop = np.mean(results_prop, axis = 0)
    # error_prop = np.std(results_prop, axis = 0)

    # # Plot average total demand with error bars for both algorithms
    # x = np.arange(len(results_prop[0]))
    # plt.errorbar(x, avg_demand_prop, yerr=error_prop, label='PROP')
    # # plt.errorbar(range(len(results_rw[0])), avg_demand_rw, yerr=error_rw, label='RW')
    # plt.xlabel('Time')
    # plt.ylabel('Average Total Demand')
    # plt.legend()
    # plt.show()

    # print("Average time to complete task: ", np.mean(times))
    # print("Standard deviation of time to complete task: ", np.std(times))


    # # Save results_rw in a pickle file
    # with open("alg1_nobleEdit_1126/results/results_prop.pickle", "wb") as f:
    #     pickle.dump(results_prop, f)






