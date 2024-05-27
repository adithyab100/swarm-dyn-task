import time

graphics_on = True

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
    for i in range(NUM_AGENTS):
        agent_locations.append((randint(HOME_LOC[0][0], HOME_LOC[0][1]), randint(HOME_LOC[1][0], HOME_LOC[1][1])))

    configuration.add_agents(agent_locations)
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

    # '''make plot look nice'''
    # plt.xlabel("Time")
    # plt.ylabel("Average Total Demand")
    # plt.plot(total_demand_over_time)
    # plt.savefig("total_demand_over_time.pdf")

    # '''save data'''
    # f = open("total_demand_over_time.txt", "w")
    # for i in total_demand_over_time:
    #     f.write(str(i)+"\n")
    # print(run_num)
    return total_demand_over_time, sum(configuration.task_completion_times)/len(configuration.task_completion_times)

def get_main_wrapper(params, n):
    return main(params, n)

if __name__ == "__main__":
    # simulate 10 times and put all the plots in a pdf

    # '''simulate 10 times and show all 10 plots on different graphs in one pdf'''
    # for i in range(10): 
    #     plt.xlabel("Time")
    #     plt.ylabel("Average Total Demand")
    #     total_demand_over_time = main()
    #     plt.plot(total_demand_over_time)
    #     plt.savefig("RW/results/total_demand_over_time"+str(i)+".pdf")
    #     plt.clf()

    # run many times and plot total demand over time with error bars
    # total_demand_over_time = []
    # for i in range(3):
    #     total_demand_over_time.append(main())
    #     print(i)
    # plt.xlabel("Time")
    # plt.ylabel("Average Total Demand")
    # plt.errorbar(range(len(total_demand_over_time[0])), np.mean(total_demand_over_time, axis=0), yerr=np.std(total_demand_over_time, axis=0))
    # plt.savefig("RW/results/total_demand_over_time_error.pdf")
    # plt.clf()
    # plt.show()
    # main(0)

    # main(0)
    # main([6, 20000, 5],0)

    params  = [6,1000, 5]
    get_main_wrapper(params, 0)
    # trials = 50


    # for i in range(9,-1,-1):
    #     file  = open("RW/results/vary_task_rate_llsub.txt", 'a')
    #     print(i)
    #     results_rw = []
    #     results = []
    #     with Pool() as pool:
    #         params = [6,10000*(i+1), 5]
    #         partial_function = partial(get_main_wrapper, params)

    #         results = pool.map(partial_function, range(trials))
    #         # results_rw.append(results[0])

    #     results_rw = [x[0] for x in results]
    #     times = [x[1] for x in results]
    #     print(len(times))
    #     avg_demand_rw = np.mean(results_rw, axis = 0)
    #     error_rw = np.std(results_rw, axis = 0)

    #     converged = False
    #     if abs(avg_demand_rw[-200] - avg_demand_rw[-1]) < 0.25:
    #         converged = True

    #     file.write(f"{i} {avg_demand_rw[-1]} {error_rw[-1]} {np.mean(times)} {np.std(times)} {converged}, average over {len(times)} runs\n")
    #     file.close()

    
    # time_per_demand_vals = [20, 15, 10, 5, 4, 3, 2, 1]

    # for i in time_per_demand_vals:
    #     file  = open("RW/results/vary_timeperdemand_llsub.txt", 'a')
    #     print(i)
    #     results_rw = []
    #     results = []
    #     with Pool() as pool:
    #         params = [6,50000, i]
    #         partial_function = partial(get_main_wrapper, params)

    #         results = pool.map(partial_function, range(trials))
    #         # results_rw.append(results[0])

    #     results_rw = [x[0] for x in results]
    #     times = [x[1] for x in results]
    #     print(len(times))
    #     avg_demand_rw = np.mean(results_rw, axis = 0)
    #     error_rw = np.std(results_rw, axis = 0)

    #     converged = False
    #     if abs(avg_demand_rw[-200] - avg_demand_rw[-1]) < 0.25:
    #         converged = True

    #     file.write(f"{i} {avg_demand_rw[-1]} {error_rw[-1]} {np.mean(times)} {np.std(times)} {converged}, average over {len(times)} runs\n")
    #     file.close()
    




# OLD

    # def main_wrapper(n):
    #     results_rw.append(main(n))

    # with Pool() as pool:
    #     results = pool.map(main, range(N))
    #     # results_rw.append(a[0])

    # results_rw = [x[0] for x in results]
    # times = [x[1] for x in results]

    # print(len(results_rw), len(results_rw[0]))

    # # Calculate average total demand and error bars for RW algorithm
    # avg_demand_rw = np.mean(results_rw, axis = 0)
    # error_rw = np.std(results_rw, axis = 0)

    # # Plot average total demand with error bars for both algorithms
    # x = np.arange(len(results_rw[0]))
    # plt.errorbar(x, avg_demand_rw, yerr=error_rw, label='RW')
    # # plt.errorbar(range(len(results_rw[0])), avg_demand_rw, yerr=error_rw, label='RW')
    # plt.xlabel('Time')
    # plt.ylabel('Average Total Demand')
    # plt.legend()
    # plt.show()

    # print("Average task completion time", sum(times)/len(times))
    # print("Standard deviation of task completion time", np.std(times))

    # # Save results_rw in a pickle file
    # with open("RW/results/results_rw.pickle", "wb") as f:
    #     pickle.dump(results_rw, f)

