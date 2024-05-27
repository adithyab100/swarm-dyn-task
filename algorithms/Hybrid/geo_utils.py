directions = ["S", "L", "R", "D", "U"]
from constants import N, M, TORUS
import numpy as np
import random

"""
Given a vertex location (x,y), generate a map from local coordinates to other vertices

Parameters
vertex: Vertex
	the central vertex from which to generate the local map around 
influence_radius: int
	generate the map with vertices in the square {-d, +d} around the 
	central vertex, where d is the influence radius 
global_vertices: dict
	mapping from locations (x,y) to Vertex from the global configuration
"""
def generate_local_mapping(vertex, influence_radius, global_vertices):

	vertex_mapping = {}
	vx = vertex.x
	vy = vertex.y

	for dx in range(-influence_radius,influence_radius+1):
		for dy in range(-influence_radius,influence_radius+1):
			if TORUS:
				vertex_mapping[(dx, dy)] = global_vertices[(vx+dx)%M, (vy+dy)%N]
			else:
				if vx + dx < M and vx + dx >= 0 and vy+dy < N and vy+dy >= 0:
					vertex_mapping[(dx, dy)] = global_vertices[vx+dx, vy+dy]

	return vertex_mapping

"""
Given a direction of motion, computes the new coordinate 
Parameters
x: int
	the x coordinate of original location
y: int 
	the y coordinate of original location
direction: str
	{S, D, U, L, R} representing which direction to move
ignore_bound: bool
	whether we prevent the user from moving in an illegal direction or let them 
	handle it
"""
def get_coords_from_movement(x, y, direction, ignore_bound = False):
	if direction == "S":
		return x, y
	elif direction == "L":
		if x-1 >= 0 or not TORUS and ignore_bound:
			return x-1, y
		elif TORUS:
			return (x-1)%M, y
	elif direction == "R":
		if x+1 < M or not TORUS and ignore_bound:
			return x+1, y
		elif TORUS:
			return (x+1)%M, y
	elif direction == "D":
		if y-1 >= 0 or not TORUS and ignore_bound:
			return x, y-1
		elif TORUS:
			return x, (y-1)%N
	elif direction == "U":
		if y+1 < N or not TORUS and ignore_bound:
			return x, y+1
		elif TORUS:
			return x, (y+1)%N
	return x, y

def get_slope(x1, y1, x2, y2):
	if x1-x2 == 0:
		return np.tan(np.pi/2) # essentially infinity
	else:
		return (y1-y2)/(x1-x2)

"""
Given a direction of motion, a starting point, and the agents current location,
computes what direction the agent should go next
Parameters
angle: int
	the angle in radians of motion
start: (int,int)
	the starting coordinates of the agent
curr_loc: (int, int)
	where the agent is curently located
"""
def get_direction_from_angle(angle, start, curr_loc):
	x_direction = np.sign(np.cos(angle))
	y_direction = np.sign(np.sin(angle))

	move_x = (curr_loc[0] + x_direction, curr_loc[1])
	move_y = (curr_loc[0], curr_loc[1]+y_direction)

	curr_slope = np.tan(angle)
	x_closeness = abs(get_slope(start[0], start[1], move_x[0], move_x[1]) - curr_slope)
	y_closeness = abs(get_slope(start[0], start[1], move_y[0], move_y[1]) - curr_slope)

	# Check if x direction is the closer slope; if x and y are equal closeness pick one at random
	# Edge case makes sure if we are moving vertically we don't move in the x direction
	if (x_closeness < y_closeness or (x_closeness == y_closeness and random.randint(0,1) == 0)) and x_direction != 0:
		if x_direction > 0:
			return "R"
		else:
			return "L"
	else:
		if y_direction > 0:
			return "U"
		else:
			return "D"
	
def get_direction_from_destination(destination, curr_loc):
	best_dist = l2_distance(destination[0], destination[1], curr_loc[0], curr_loc[1])
	best_dir = "S"

	for direction in directions:
		new_loc = get_coords_from_movement(curr_loc[0], curr_loc[1], direction)
		new_dist = l2_distance(new_loc[0], new_loc[1], destination[0], destination[1])
		if new_dist < best_dist:
			best_dist = new_dist
			best_dir = direction
	return best_dir

# Get euclidean distance between points 
def l2_distance(x1, y1, x2, y2):
	return np.sqrt((x1-x2)**2 + (y1-y2)**2)

# Checks if a point is within bounds
def within_bounds(x,y, site=None):
	if site is None:
		if x >= 0 and x < M and y >= 0 and y < N:
			return True
		return False
	else:
		if x >= site.site_location[0][0] and x <= site.site_location[0][1] and y >= site.site_location[1][0] and y <= site.site_location[1][1]:
			return True
		return False







