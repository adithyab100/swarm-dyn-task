import random 
from constants import L, TIME_PER_DEMAND

class AgentState:

	def __init__(self, agent_id, vertex, type, data=None, l=L, msg_ct=0, prop_ctr=0):
		self.reset(agent_id, vertex, type, data, l, msg_ct, prop_ctr)

	def reset(self, agent_id, vertex, type, data, l, msg_ct, prop_ctr):
		# Initial Parameters
		self.id = agent_id
		self.type = type  # 'follower' or 'propagator'
		self.data = {}  # task_info: mapping from (x,y) task to (residual-demand, age), where 'age' num rounds this piece of data has been with this agent (unchanged)
		self.L = l
		self.msg_ct = msg_ct  # total(cumulative) num interagent messages sent during current system run
		self.prop_ctr = prop_ctr  # counter to track when propagator agents can propagate according to the propagation timeout

		#Random Walk Parameters
		self.angle = 0
		self.starting_point = (vertex.x, vertex.y)
		self.travel_distance = 0
		self.levy_cap = 1/l

		#Destination Travel Parameters
		self.destination_task = None

		#Commitment
		self.committed_task = None
		self.committed_time = TIME_PER_DEMAND

		self.blocked_task = None
		





	
