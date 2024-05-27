class VertexState:

	def __init__(self, is_task=False, demand=None, task_location=None, is_home = False, next_task_time = None, task_timer = 0):
		self.is_task = is_task
		self.is_home = is_home
		self.demand = demand
		self.residual_demand = demand
		self.task_location = task_location
		self.next_task_time = next_task_time
		self.task_timer = task_timer
