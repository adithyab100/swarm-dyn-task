from VertexState import VertexState
class Vertex:
	def __init__(self,x,y, vertex_state=None):
		self.x = x
		self.y = y 
		self.agents = set()
		if vertex_state is None:
			self.state = VertexState()
		else:
			self.state = vertex_state

	def coords(self):
		return (self.x, self.y)
			