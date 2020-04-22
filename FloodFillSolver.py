# FloodFillSolver.py

# Implements a flood fill algorithm, with different color paint cans
# to start.

from collections import deque


class FloodFillSolver:
	def __init__(self, room):
		self.room = room
		self.tiles = deque()

	def AddBucket(self, bucket):
		row = bucket['pos'][0]
		col = bucket['pos'][1]
		if row < 0 or row >= len(self.room):
			return False
		if col < 0 or col >= len(self.room[row]):
			return False
		curColor = self.room[row][col]
		if curColor != [1, 1, 1, 1]:
			return False
		self.room[row][col] = bucket['color']
		self.tiles.append(bucket['pos'])
		return True

	def Generate(self):
		while self.tiles:
			tile = self.tiles.popleft()
			row = tile[0]
			col = tile[1]
			color = self.room[row][col]
			newAlpha = 0.3 + 0.85*(color[3]-0.3)
			newColor = color.copy()
			newColor[3] = newAlpha
			for dpos in [[-1, 0],[0, -1],[1, 0],[0,1]]:
				newTile = [row+dpos[0], col + dpos[1]]
				if self.AddBucket({'color':newColor, 'pos':newTile}):
					yield 1
		yield 2

