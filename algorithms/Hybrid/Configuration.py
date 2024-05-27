import multiprocessing as mp
from Agent import Agent
from Vertex import Vertex
from VertexState import VertexState
from geo_utils import generate_local_mapping, get_coords_from_movement
from res_utils import *
from constants import INFLUENCE_RADIUS
import numpy as np
import time

"""
Given a local vertex mapping, generate a proposed new vertex state and
new agent states and directions for each agent in that vertex

Parameters
local_vertex_mapping: dict
	mapping from local coordinates to the vertices at those coordiantes
"""
def delta(params):
	local_vertex_mapping, x, y = params
	print(x,y)
	vertex = local_vertex_mapping[(0,0)]

	if len(vertex.agents) == 0:
		return x, y, vertex.state, {}

	# Phase One: Each vertex uses their own transition function to propose a new
	# vertex state, agent state, and direction of motion
	proposed_vertex_states = {}
	proposed_agent_updates = {}

	for agent in vertex.agents:
		proposed_vertex_state, proposed_agent_state, direction = agent.generate_transition(local_vertex_mapping)

		proposed_vertex_states[agent.state.id] = proposed_vertex_state
		proposed_agent_updates[agent.state.id] = AgentTransition(proposed_agent_state, direction)


	# Phase Two: Use a resolution rule to handle conflicting proposed vertex states
	new_vertex_state, new_agent_updates = naive_resolution(proposed_vertex_states, proposed_agent_updates)

	# Need x and y for setting the global state for parallel processing
	return x, y, new_vertex_state, new_agent_updates

class Configuration:
	"""
	Initialize the configuration

	Parameters
	agent_locations: list
		list of integers specifying what vertex to initialize each agent in
	N: int
		the height of the configuration
	M: int
		the width of the configuration
	torus: bool
		True if the grid is a torus, False if we are considering
		edge effects
	"""
	def __init__(self, N, M, max_prop_rad, prop_timeout, expected_demand_per_task, expected_time_until_task, time_per_demand, torus=False):
		# Create all vertices
		self.vertices = {}
		for x in range(M):
			for y in range(N):
				self.vertices[(x, y)] = Vertex(x,y, VertexState(next_task_time=round(np.random.exponential(expected_time_until_task))))
		self.N = N
		self.M = M
		self.max_prop_rad = max_prop_rad
		self.prop_timeout = prop_timeout
		self.torus = torus
		self.influence_radius = INFLUENCE_RADIUS
		self.agents = {}  # map from id to agent itself
		self.task_completion_times = []
		self.expected_time_until_task = expected_time_until_task
		self.time_per_demand = time_per_demand
		self.expected_demand_per_task = expected_demand_per_task


	def add_agents(self, agent_locations,types):
		for agent_id in range(len(agent_locations)):
			location = self.vertices[agent_locations[agent_id]]
			agent = Agent(agent_id, location, types[agent_id], config=self)
			self.agents[agent_id] = agent
			location.agents.add(agent)

	def reset_agent_locations(self, agent_locations, home_nest):
		for x in range(self.M):
			for y in range(self.N):
				self.vertices[(x, y)].agents = set()
		for agent_id in range(len(agent_locations)):
			agent = self.agents[agent_id]
			vertex = self.vertices[agent_locations[agent_id]]
			vertex.agents.add(agent)
			agent.location = vertex
	"""
	Generates a global transitory state for the entire configuration
	"""
	def generate_global_transitory(self):
		# Break down into local configurations and generate local transitory configurations for each to create global one
		global_transitory = {}
		# print(self.M, self.N)
		for x in range(self.M):
			for y in range(self.N):
				# print(self.influence_radius)
				#Get mapping from local coordinates to each neighboring vertex
				local_vertex_mapping = generate_local_mapping(self.vertices[(x,y)], self.influence_radius, self.vertices)
				# print(x,y,local_vertex_mapping)
				global_transitory[(x,y)] = self.delta(local_vertex_mapping)

		return global_transitory

	"""
	Given a local vertex mapping, generate a proposed new vertex state and
	new agent states and directions for each agent in that vertex

	Parameters
	local_vertex_mapping: dict
		mapping from local coordinates to the vertices at those coordiantes
	"""
	def delta(self,local_vertex_mapping):
		vertex = local_vertex_mapping[(0,0)]

		if len(vertex.agents) == 0:
			return vertex.state, {}

		# Phase One: Each vertex uses their own transition function to propose a new
		# vertex state, agent state, and direction of motion
		proposed_vertex_states = {}
		proposed_agent_updates = {}

		for agent in vertex.agents:
			proposed_vertex_state, proposed_agent_state, direction = agent.generate_transition(local_vertex_mapping)

			proposed_vertex_states[agent.state.id] = proposed_vertex_state
			proposed_agent_updates[agent.state.id] = AgentTransition(proposed_agent_state, direction)


		# Phase Two: Use a resolution rule to handle conflicting proposed vertex states
		new_vertex_state, new_agent_updates = task_claiming_resolution(proposed_vertex_states, proposed_agent_updates, vertex)
		return new_vertex_state, new_agent_updates

	"""
	Given the global transitory configuration, update the configuration to the new
	global state
	"""
	def execute_transition(self,global_transitory):
		for x,y in global_transitory.keys():
			vertex = self.vertices[(x,y)]
			new_vertex_state, new_agent_updates = global_transitory[(x,y)]

			# Update vertex state
			vertex.state = new_vertex_state

			# Update agents
			for agent_id in new_agent_updates:
				agent = self.agents[agent_id]
				update = new_agent_updates[agent_id]
				if update != None:
					# Update agent state
					agent.state = update.state

					# Update agent location
					movement_dir = update.direction

					# Erase agent from current location
					vertex.agents.remove(agent)

					# Move agent according to direction
					new_coords = get_coords_from_movement(vertex.x, vertex.y, movement_dir)
					agent.location = self.vertices[new_coords]

					# Add agent to updated location
					agent.location.agents.add(agent)

		# dynamic task update
		for x in range(self.M):
			for y in range(self.N):
				if not self.vertices[(x,y)].state.is_home and not self.vertices[(x,y)].state.is_task:
					self.vertices[(x,y)].state.next_task_time -= 1

					#create new task here if the counter has reached 0
					if self.vertices[(x,y)].state.next_task_time == 0:
						task_demand = max(1,round(np.random.normal(self.expected_demand_per_task, 3)))
						self.vertices[(x,y)].state = VertexState(is_task = True, demand =task_demand, task_location = (x,y))

				# remove task when completed and release all agents here
				elif self.vertices[(x,y)].state.is_task:
					self.vertices[(x,y)].state.task_timer += 1
					if self.vertices[(x,y)].state.residual_demand == 0:
						for a in self.vertices[(x,y)].agents:
							if a.state.type == "Propagator":
								a.state.data[(x,y)] = (0, 0)
						self.task_completion_times.append((self.vertices[(x,y)].state.task_timer+self.time_per_demand)/self.vertices[(x,y)].state.demand)
						self.vertices[(x,y)].state = VertexState(next_task_time = round(np.random.exponential(self.expected_time_until_task)))

						# for agent in self.vertices[(x,y)].agents:
						# 	agent.state.committed_task = None
		#print(self.vertices[(17,16)].state.residual_demand)


	"""
	Transition from the current global state into the next one
	"""
	def transition(self):
		global_transitory = self.generate_global_transitory()
		self.execute_transition(global_transitory)

	def all_agents_terminated(self):
		for agent_id in self.agents:
			if not self.agents[agent_id].terminated:
				return False
		return True
