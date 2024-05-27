import random
from collections import namedtuple
import copy

AgentTransition = namedtuple("AgentTransition", "state direction")
LocalTransitory = namedtuple("LocalTransitory", "vertex_state, agent_updates")

def naive_resolution(proposed_vertex_states, proposed_agent_updates, vertex):
	return LocalTransitory(list(proposed_vertex_states.values())[0], proposed_agent_updates)

def winner_takes_all(proposed_vertex_states, proposed_agent_updates, vertex):
	agents = proposed_vertex_states.keys()
	winner = random.choice(agents)
	new_vertex_state = proposed_vertex_states[winner]
	new_agent_updates = {}
	for agent in proposed_agent_updates.keys():
		if agent == winner:
			new_agent_updates[agent] = proposed_agent_updates[agent]
		else:
			new_agent_updates[agent] = None

def task_claiming_resolution(proposed_vertex_states, proposed_agent_updates, vertex):
	if not vertex.state.is_task:
		return naive_resolution(proposed_vertex_states, proposed_agent_updates, vertex)
	agents = list(proposed_agent_updates.keys())
	contenders = []
	available_slots = vertex.state.residual_demand
	attempted_claims = 0
	for agent_id in proposed_vertex_states.keys():
		if proposed_vertex_states[agent_id].residual_demand == vertex.state.residual_demand-1:
			attempted_claims += (vertex.state.residual_demand-proposed_vertex_states[agent_id].residual_demand)
			contenders.append(agent_id)
	if attempted_claims <= available_slots:
		vertex.state.residual_demand = available_slots-attempted_claims
		return LocalTransitory(vertex.state, proposed_agent_updates)
	else:
		new_proposed_agent_updates = {}
		winners = set()
		while len(winners) < available_slots:
			winner = random.choice(contenders)
			if winner not in winners:
				winners.add(winner)
		for agent_id in agents:
			if agent_id in winners or agent_id not in contenders:
				new_proposed_agent_updates[agent_id] = proposed_agent_updates[agent_id]
			else:
				proposed_agent_updates[agent_id].state.committed_task = None
				new_proposed_agent_updates[agent_id] = proposed_agent_updates[agent_id]
		#Must modify vertex state here to keep the same task objects
		vertex.state.residual_demand = 0
		return LocalTransitory(vertex.state, new_proposed_agent_updates)
