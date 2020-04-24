# FloodFillSolver.py

# Implements a flood fill algorithm, with different color paint cans
# to start.

from collections import deque


class FloodFillSolver:
	def __init__(self, room):
		self.room = room
		self.tiles = deque()

	def AddBucket(self, bucket, painting_walls=False):
		row = bucket['pos'][0]
		col = bucket['pos'][1]
		if row < 0 or row >= len(self.room):
			return False
		if col < 0 or col >= len(self.room[row]):
			return False
		curColor = self.room[row][col]
		if not painting_walls and curColor != [1, 1, 1, 1]:
			return False
		self.room[row][col] = bucket['color']
		if not painting_walls:
			self.tiles.append(bucket['pos'])
		return True

	def GetColor(self, tile):
		row = tile[0]
		col = tile[1]
		curColor = [1, 1, 1, 1]
		if row < 0 or row >= len(self.room):
			return curColor
		if col < 0 or col >= len(self.room[row]):
			return curColor
		curColor = self.room[row][col]
		return curColor

	def ClearPaint(self):
		self.tiles.clear()
		for row in self.room:
			for col in range(len(row)):
				tile = row[col]
				if tile != [0, 0, 0, 1] and tile != [1, 1, 1, 1]:
					row[col] = [1, 1, 1, 1]

	def Generate(self):
		while self.tiles:
			tile = self.tiles.popleft()
			row = tile[0]
			col = tile[1]
			color = self.room[row][col]
			newAlpha = 0.3 + 0.96*(color[3]-0.3)
			newColor = color.copy()
			newColor[3] = newAlpha
			for dpos in [[-1, 0],[0, -1],[1, 0],[0,1]]:
				newTile = [row+dpos[0], col + dpos[1]]
				if self.AddBucket({'color':newColor, 'pos':newTile}):
					yield 1
		yield 2

