# FloodFillSolver.py

# Implements a flood fill algorithm, with different color paint cans
# to start.

from collections import deque


class FloodFillSolver:
	def __init__(self, limit):
		self.limit = limit

	def Generate(self):
		for i in range(self.limit):
			yield i
		yield