import numpy as np
import pygame
from scipy.interpolate import interp1d
import sys

class ViewController:
	BLACK = (0, 0, 0)
	WHITE = (255, 255, 255)
	GREEN = (0, 200, 0)
	RED = (200,0,0)
	BLUES = []
	YELLOW = (200, 200, 0)
	VERTEX_SIZE = 15
	FPS = 10

	def __init__(self, configuration):
		self.configuration = configuration
		self.WINDOW_HEIGHT = self.configuration.N*self.VERTEX_SIZE
		self.WINDOW_WIDTH = self.configuration.M*self.VERTEX_SIZE
		pygame.init()
		self.SCREEN = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
		self.make_grid()

		self.font = pygame.font.SysFont(None, int(self.VERTEX_SIZE*1.2))

		blues = np.linspace(0,200, configuration.prop_timeout*5)
		for b in blues:
			self.BLUES.append( (b,b,255) )

	def make_grid(self):
		self.SCREEN.fill(self.WHITE)
		for x in range(0, self.configuration.M):
			for y in range(0, self.configuration.N):
				rect = pygame.Rect(x*self.VERTEX_SIZE, self.WINDOW_HEIGHT-y*self.VERTEX_SIZE-self.VERTEX_SIZE, self.VERTEX_SIZE, self.VERTEX_SIZE)
				pygame.draw.rect(self.SCREEN, self.BLACK, rect, 1)
		pygame.display.update()

	def draw_configuration(self):
		for x in range(0, self.configuration.M):
			for y in range(0, self.configuration.N):
				rect = pygame.Rect(x*self.VERTEX_SIZE+1, self.WINDOW_HEIGHT-y*self.VERTEX_SIZE-self.VERTEX_SIZE+1, self.VERTEX_SIZE-2, self.VERTEX_SIZE-2)
				num_agents = len([x for x in self.configuration.vertices[(x,y)].agents if x.state.type == "Follower"])
				data_at_vertex = False
				min_ctr = len(self.BLUES) - 1
				for agent in self.configuration.vertices[(x,y)].agents:
					if agent.state.type == "Propagator":
						if len(agent.state.data) > 0:
							data_at_vertex = True
						for t in agent.state.data:
							if agent.state.data[t][1] < min_ctr:
								min_ctr = agent.state.data[t][1]

				if self.configuration.vertices[(x,y)].state.is_task and self.configuration.vertices[(x,y)].state.residual_demand > 0:
					pygame.draw.rect(self.SCREEN, self.YELLOW, rect, 0)
					demand_text = self.font.render(str(self.configuration.vertices[(x,y)].state.residual_demand), True, self.BLACK)
					self.SCREEN.blit(demand_text, ((x+.1)*self.VERTEX_SIZE, self.WINDOW_HEIGHT-(y+.8)*self.VERTEX_SIZE))
				elif num_agents > 0:
					pygame.draw.rect(self.SCREEN, self.GREEN, rect, 0)
				# elif self.configuration.vertices[(x,y)].state.is_home:
				# 	pygame.draw.rect(self.SCREEN, self.WHITE, rect, 0)
				elif data_at_vertex:
					idx = map
					pygame.draw.rect(self.SCREEN, self.BLUES[min_ctr], rect, 0)  # Darker blue represents newer task information
				else:
					pygame.draw.rect(self.SCREEN, self.WHITE, rect, 0)

	def update(self):
		self.draw_configuration()
		pygame.display.update()
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
		if self.FPS is not None:
			pygame.time.delay(int(1000/self.FPS))

	def quit(self):
		pygame.quit()
