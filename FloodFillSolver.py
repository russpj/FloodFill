# FloodFillSolver.py

# Implements a flood fill algorithm, with different color paint cans
# to start.

from collections import deque


class FloodFillSolver:
	def __init__(self, room, limit=0):
		self.room = room
		self.limit = limit
		self.tiles = deque()

	def AddBucket(self, bucket):
		row = bucket['pos'][1]
		col = bucket['pos'][0]
		if row < 0 or row >= len(self.room):
			return
		if col < 0 or col >= len(self.room[row]):
			return
		curColor = self.room[row][col]
		if curColor != [1, 1, 1, 1]:
			return
		self.room[row][col] = bucket['color']
		self.tiles.append(bucket['pos'])

	def Generate(self):
		for i in range(self.limit):
			yield i
		yield