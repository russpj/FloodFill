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
			return
		if col < 0 or col >= len(self.room[row]):
			return
		curColor = self.room[row][col]
		if curColor != [1, 1, 1, 1]:
			return
		self.room[row][col] = bucket['color']
		self.tiles.append(bucket['pos'])

	def Generate(self):
		while self.tiles:
			tile = self.tiles.popleft()
			row = tile[0]
			col = tile[1]
			color = self.room[row][col]
			newAlpha = 0.5 + 0.9*(color[3]-0.5)
			newColor = color
			newColor[3] = newAlpha
			for drow in [-1, 0, 1]:
				for dcol in [-1, 0, 1]:
					if drow != 0 or dcol != 0:
						newTile = [row+drow, col+dcol]
						self.AddBucket({'color':newColor, 'pos':newTile})
			yield 1
		yield 2

