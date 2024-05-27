from AgentState import AgentState
from geo_utils import *
import random
from math import pi, floor
from constants import *
from scipy.stats import levy
import copy

class Agent:
	def __init__(self,agent_id, vertex, type, data=None, config=None, l=L, msg_ct=0, prop_ctr=0):
		self.location = vertex
		self.config = config
		self.state = AgentState(agent_id, vertex, type, data, l, msg_ct, prop_ctr)

	def find_nearby_task(self,local_vertex_mapping):
		ret = None
		min_dist = 10000000000
		for dx, dy in local_vertex_mapping.keys():
			vertex = local_vertex_mapping[(dx,dy)]
			if vertex.state.is_task and vertex.state.residual_demand > 0:
				if self.state.blocked_task is None or vertex.state.task_location != self.state.blocked_task.task_location:
					this_dist = l2_distance(self.location.x, self.location.y, self.location.x+dx, self.location.y+dy)
					if  this_dist < min_dist:
						min_dist = this_dist
						ret = vertex.state
		return ret

	def within_site(self, x, y, site):
		if site == None:
			x_range = (0, M-1)
			y_range = (0, N-1)

		if x >= x_range[0] and x <= x_range[1] and y >= y_range[0] and y <= y_range[1]:
			return True
		return False


	def get_travel_direction_prop(self, new_agent_state):
		if self.state.travel_distance == 0:
			new_agent_state.travel_distance = int(min(self.state.levy_cap, levy.rvs(loc=levy_loc))) #Twice the distance to the nest? maybe make this a variable
			new_agent_state.angle = random.uniform(0, 2*pi)
			new_agent_state.starting_point = (self.location.x, self.location.y)

		new_direction = get_direction_from_angle(new_agent_state.angle, new_agent_state.starting_point, (self.location.x, self.location.y))
		new_location = get_coords_from_movement(self.location.x, self.location.y, new_direction, True)

		bounding_site = None

		while not self.within_site(new_location[0], new_location[1], bounding_site):
			new_agent_state.angle = random.uniform(0, 2*pi)
			new_agent_state.starting_point = (self.location.x, self.location.y)
			new_direction = get_direction_from_angle(new_agent_state.angle, new_agent_state.starting_point, (self.location.x, self.location.y))
			new_location = get_coords_from_movement(self.location.x, self.location.y, new_direction, True)
		new_agent_state.travel_distance = new_agent_state.travel_distance-1
		return new_direction
	

	def get_travel_direction_rw(self, new_agent_state):
		if self.state.travel_distance == 0:
			new_agent_state.travel_distance = int(min(self.state.levy_cap, levy.rvs(loc=levy_loc))) #Twice the distance to the nest? maybe make this a variable
			new_agent_state.angle = random.uniform(0, 2*pi)
			new_agent_state.starting_point = (self.location.x, self.location.y)

		new_direction = get_direction_from_angle(new_agent_state.angle, new_agent_state.starting_point, (self.location.x, self.location.y))
		new_location = get_coords_from_movement(self.location.x, self.location.y, new_direction, True)

		bounding_site = None

		while not self.within_site(new_location[0], new_location[1], bounding_site):
			new_agent_state.angle = random.uniform(0, 2*pi)
			new_agent_state.starting_point = (self.location.x, self.location.y)
			new_direction = get_direction_from_angle(new_agent_state.angle, new_agent_state.starting_point, (self.location.x, self.location.y))
			new_location = get_coords_from_movement(self.location.x, self.location.y, new_direction, True)
		new_agent_state.travel_distance = new_agent_state.travel_distance-1
		return new_direction

	# Used by follower agents; looks at task_info of propagator agent at its vertex, chooses task to move towards with defined probabilities
	def choose_dir_from_propagator(self):
		for agent in self.location.agents:
			if agent.state.type == "Propagator" and sum([x[0] for x in agent.state.data.values()]) > 0:
				probs = []

				# print(self.state.blocked_task)
				for x in list(agent.state.data.keys()):
					dem = agent.state.data[x][0]
					#print(dem)
					dist = l2_distance(x[0], x[1], self.location.coords()[0], self.location.coords()[1])
					if dist == 0 and dem > 0:
							return get_direction_from_destination(x, self.location.coords())
					elif dist == 0 or (self.state.blocked_task is not None and x == self.state.blocked_task.task_location):
						probs.append(0)
					else:
						probs.append(dem / dist**2)
				#print(probs)
				if sum(probs) > 0:
					task = random.choices(list(agent.state.data.keys()), weights=probs, k=1)
					return get_direction_from_destination(task[0], self.location.coords())
		return None

	# Used by propagator agents; share task/demand information (if it is new) with propagator agents in influence radius (1)
	def propagate(self, local_vertex_mapping, comm_buff, max_dist):
		ct = 0

		# Truncate influence radius 2 ('follower' agent) local_vertex_mapping to influence radius 1 ('propagator' agent)
		local_vertex_mapping.pop((0,0))
		to_remove = []
		for i in local_vertex_mapping:
			if abs(i[0]) > 2 or abs(i[1]) > 2:
				to_remove.append(i)
		for j in to_remove:
			local_vertex_mapping.pop(j)

		for v in list(local_vertex_mapping.values()):
			for agent in v.agents:
				if agent.state.type == "Propagator":  # access the propagator agent at each vertex
					ct_tmp = 0
					for t in self.state.data:  # loop through this (self) agent's task/demand data
						if self.state.data[t][1] > 0 and l2_distance(t[0], t[1], agent.location.coords()[0], agent.location.coords()[1]) <= max_dist:
							ct_tmp = 1
							if t not in list(agent.state.data.keys()):
								agent.state.data[t] = (self.state.data[t][0], 0)
							elif agent.state.data[t][0] > self.state.data[t][0]:
								agent.state.data[t] = (self.state.data[t][0], 0)
					ct += ct_tmp  # increment message count each time task_info shared with another agent

		if ct > 0:
			ages = []
			for t in self.state.data:
				ages.append(self.state.data[t][1])
			if min(ages) > comm_buff + 1:  # if this (self) agent already propagated this same exact task_info, do not need to again (no messages sent)
				ct = 0

		return ct


	def generate_transition(self,local_vertex_mapping):
		new_agent_state = copy.copy(self.state)
		# We are not headed towards a task or doing a task

		if self.state.type == "Follower":
			# print(self.state.committed_task, self.state.destination_task, self.state.blocked_task)
			if self.state.committed_task is None and self.state.destination_task is None:
				nearby_task = self.find_nearby_task(local_vertex_mapping)
				# print("nearby", nearby_task)
				if nearby_task is not None:  # If found task nearby, head towards it/do it
					new_agent_state.destination_task = nearby_task
					return self.location.state, new_agent_state, "S"
				else:  # Otherwise, move w prob based on propagator info; if no info at vertex, random walk
					new_direction = self.choose_dir_from_propagator()
					if new_direction is None:
						new_direction = self.get_travel_direction_prop(new_agent_state)
					else:
						new_agent_state.msg_ct += 1  # Had to look at task_info of propagator agent, increment interagent message count
					return self.location.state, new_agent_state, new_direction


			# We are headed towards a task
			if self.state.destination_task is not None:
				if self.state.destination_task.residual_demand == 0:
					new_agent_state.destination_task = None
					return self.location.state, new_agent_state, "S"
				# If we have arrived
				if self.location.coords() == self.state.destination_task.task_location:
					new_agent_state.committed_task = self.state.destination_task
					new_agent_state.destination_task = None
					new_vertex_state = copy.copy(self.location.state)
					new_vertex_state.residual_demand -= 1
					#print(new_vertex_state.residual_demand)
					new_agent_state.committed_time -=1
					return new_vertex_state, new_agent_state, "S"
				# Still headed towards task
				else:
					new_direction = get_direction_from_destination(self.state.destination_task.task_location, self.location.coords())
					new_location = get_coords_from_movement(self.location.x, self.location.y, new_direction)
					return self.location.state, new_agent_state, new_direction
			# We are committed to doing a task, so stay still
			else:
				new_agent_state.blocked_task = None
				new_agent_state.committed_time -=1
				new_vertex_state = copy.copy(self.location.state)


				if self.state.committed_time <= 0:
					if self.state.committed_task.residual_demand == 0:
						new_agent_state.committed_task = None
						new_agent_state.destination_task = None
						new_agent_state.committed_time = TIME_PER_DEMAND
					else:
						# check how many agents in local mapping are assigned to this task
						# if at least as high as residual demand, then unassign task
						# otherwise, decrement residual demand
						assigned_agents = 0

						for dx, dy in local_vertex_mapping.keys():
							vertex = local_vertex_mapping[(dx,dy)]
							for agent in vertex.agents:
								if agent.state.committed_task == self.state.committed_task:
									assigned_agents += 1


						if assigned_agents > 0 and random.randint(1,assigned_agents) > self.state.committed_task.residual_demand:
							# print("cool case")
							new_agent_state.blocked_task = self.state.committed_task
							new_agent_state.committed_task = None
							new_agent_state.destination_task = None
							new_agent_state.committed_time = TIME_PER_DEMAND

						else:
							# new_agent_state.committed_task.residual_demand -= 1
							# new_vertex_state.residual_demand -= 1
							new_agent_state.committed_task = None
							new_agent_state.destination_task = None
							new_agent_state.committed_time = TIME_PER_DEMAND
							new_agent_state.blocked_task = None

				return new_vertex_state, new_agent_state, "S"
			
		elif self.state.type  == "RandomWalker":
			# We are not headed towards a task or doing a task
			if self.state.committed_task is None and self.state.destination_task is None:
				nearby_task = self.find_nearby_task(local_vertex_mapping)
				if nearby_task is not None:
					new_agent_state.destination_task = nearby_task
					return self.location.state, new_agent_state, "S"
				else:
					new_direction = self.get_travel_direction_rw(new_agent_state)
					return self.location.state, new_agent_state, new_direction
			# We are headed towards a task
			if self.state.destination_task is not None:
				if self.state.destination_task.residual_demand == 0:
					new_agent_state.destination_task = None
					return self.location.state, new_agent_state, "S"
				# If we have arrived
				if self.location.coords() == self.state.destination_task.task_location:
					new_agent_state.committed_task = self.state.destination_task
					new_agent_state.destination_task = None
					new_vertex_state = copy.copy(self.location.state)
					new_vertex_state.residual_demand = self.location.state.residual_demand-1
					self.state.committed_time -=1
					return new_vertex_state, new_agent_state, "S"
				# Still headed towards task
				else:
					new_direction = get_direction_from_destination(self.state.destination_task.task_location, self.location.coords())
					new_location = get_coords_from_movement(self.location.x, self.location.y, new_direction)
					return self.location.state, new_agent_state, new_direction
			# We are committed to doing a task, so stay still
			else:
				new_agent_state.committed_time -=1

				if new_agent_state.committed_time == 0:
					new_agent_state.committed_task = None
					new_agent_state.committed_time = TIME_PER_DEMAND
					
				return self.location.state, new_agent_state, "S"

		else: #lif type == 'Propagator':
			if self.location.state.is_task:  # if propagator agent on task, get the residual demand
				if self.location.coords() not in self.state.data:
					self.state.data[self.location.coords()] = (self.location.state.residual_demand, 0)
				elif self.state.data[self.location.coords()][0] > self.location.state.residual_demand:
					self.state.data[self.location.coords()] = (self.location.state.residual_demand, 0)

				new_agent_state.prop_ctr += 1
				if new_agent_state.prop_ctr >= self.config.prop_timeout:  # can propagate every prop_timeout rounds
					new_agent_state.msg_ct += self.propagate(local_vertex_mapping, self.config.prop_timeout, self.config.max_prop_rad)
					new_agent_state.prop_ctr = 0

				#print(self.state.data)

			else:  # otherwise pass your task/demand data to your influence radius
				new_agent_state.prop_ctr += 1
				if new_agent_state.prop_ctr >= self.config.prop_timeout:  # can propagate every prop_timeout rounds
					new_agent_state.msg_ct += self.propagate(local_vertex_mapping, self.config.prop_timeout, self.config.max_prop_rad)
					new_agent_state.prop_ctr = 0
			for t in self.state.data:
				self.state.data[t] = (self.state.data[t][0], self.state.data[t][1] + 1)  # all data points at self have now sat for at least one round
			return self.location.state, new_agent_state, "S"
		
			

