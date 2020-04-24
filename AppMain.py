from enum import Enum
import copy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle, Line
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from FloodFillSolver import FloodFillSolver

floorSquare = [1,1,1,1]
wallSquare = [0,0,0,1]
smallRoom = [
	[floorSquare, wallSquare, floorSquare, floorSquare, floorSquare],
	[floorSquare, wallSquare, floorSquare, floorSquare, floorSquare],
	[floorSquare, wallSquare, floorSquare, floorSquare, floorSquare],
	[floorSquare, wallSquare, wallSquare, wallSquare, floorSquare],
	[floorSquare, floorSquare, floorSquare, floorSquare, floorSquare]
	]

buckets = [
	{
		'color': [1, 0, 0, 1],
		'pos': [0,0]
	},
	{
		'color': [0, 0, 1, 1],
		'pos': [0,4]}
	]

bucketColors = [
	[1, 0, 0, 1],
	[0, 1, 0, 1],
	[0, 0, 1, 1],
	[1, 1, 0, 1],
	[1, 0, 1, 1],
	[0, 1, 1, 1]
	]

def BigEmptyRoom(numRows, numColumns):
	room = []
	for rowNum in range(numRows):
		row = []
		for colNum in range(numColumns):
			row.append(floorSquare)
		room.append(row)
	return room

class AppState(Enum):
	DrawingWalls = 1
	DrawingBuckets = 2
	Running = 3
	Paused = 4
	Finished = 5

nextState={
	AppState.DrawingWalls: AppState.DrawingBuckets,
	AppState.DrawingBuckets: AppState.Running,
	AppState.Running: AppState.Paused,
	AppState.Paused: AppState.Running
	}

class ButtonInfo:
	def __init__(self, enabled=True, text=''):
		self.enabled = enabled
		self.text=text

class AppInfo:
	def __init__(self, statusText='', 
							resetInfo=ButtonInfo(), 
							startInfo=ButtonInfo()):
		self.statusText=statusText
		self.resetInfo=resetInfo
		self.startInfo=startInfo

infoFromState = {
	AppState.DrawingWalls: AppInfo(statusText='Drawing Walls', 
												 resetInfo=ButtonInfo(text='Reset Walls', enabled=True),
												 startInfo=ButtonInfo(text='Draw Buckets', enabled=True)),
	AppState.DrawingBuckets: AppInfo(statusText='Drawing Buckets', 
												 resetInfo=ButtonInfo(text='Reset Buckets', enabled=True),
												 startInfo=ButtonInfo(text='Start', enabled=True)),
	AppState.Finished: AppInfo(statusText='Done', 
												 resetInfo=ButtonInfo(text='Reset Buckets', enabled=True),
												 startInfo=ButtonInfo(text='Pause', enabled=False)),
	AppState.Paused: AppInfo(statusText='Paused', 
												 resetInfo=ButtonInfo(text='Reset Buckets', enabled=True),
												 startInfo=ButtonInfo(text='Start', enabled=True)),
	AppState.Running: AppInfo(statusText='Running Simulation', 
												 resetInfo=ButtonInfo(text='Reset', enabled=False),
												 startInfo=ButtonInfo(text='Pause', enabled=True))
	}


# BoardLayout encapsulates the playing board
class BoardLayout(BoxLayout):
	def __init__(self, touch_notification=None):
		super().__init__()
		self.room = []
		self.PlaceStuff()
		self.bind(pos=self.update_rect, size=self.update_rect)
		self.touch_notification = touch_notification

	def PlaceStuff(self):
		pass

	def InitRoom(self, room):
		self.room = room

	def update_rect(self, instance, value):
		self.UpdateRoom()

	def UpdateRoom(self):
		rectSize = self.size
		rectPos = self.pos
		self.squareSize = []
		self.squarePos = []

		if rectSize[0] > rectSize[1]:
			# wider than tall
			self.squareSize = [rectSize[1], rectSize[1]]
			self.squarePos = [rectPos[0]+(rectSize[0]-self.squareSize[0])/2, rectPos[1]]
		else:
			# taller than wide
			self.squareSize = [rectSize[0], rectSize[0]]
			self.squarePos = [rectPos[0], rectPos[1]+(rectSize[1]-self.squareSize[1])/2]

		with self.canvas:
			self.canvas.clear()
			Color(0.5, 0.5, 0.5, 1)
			Rectangle(size=rectSize, pos=rectPos)

			squareSize = self.squareSize
			squarePos = self.squarePos

			numRows = len(self.room)
			for row in range(numRows):
				numCols = len(self.room[row])
				for col in range(numCols):
					squareColor = self.room[row][col]
					posThis = [squarePos[0]+squareSize[0]*col/numCols, 
								squarePos[1]+squareSize[1]*row/numRows]
					posNext = [squarePos[0]+squareSize[0]*(col+1)/numCols, 
								squarePos[1]+squareSize[1]*(row+1)/numRows]
					size = [posNext[0]-posThis[0], posNext[1]-posThis[1]]
					Color(squareColor[0], squareColor[1], squareColor[2], squareColor[3])
					Rectangle(size = size, pos=posThis)

	# Calculates the location in the square, as fractions
	def PosFromTouch(self, touch):
		pos = [(touch.pos[0]-self.squarePos[0])/self.squareSize[0], 
				 (touch.pos[1]-self.squarePos[1])/self.squareSize[1]]
		return pos

	def on_touch_down(self, touch):
		if self.touch_notification is None:
			return
		pos = self.PosFromTouch(touch)
		self.touch_notification(pos, first_touch = True)

	def on_touch_move(self, touch):
		if self.touch_notification is None:
			return
		pos = self.PosFromTouch(touch)
		self.touch_notification(pos)


class HeaderLayout(BoxLayout):
	def __init__(self, **kwargs):
		super().__init__(orientation='horizontal', **kwargs)
		self.PlaceStuff()
		self.bind(pos=self.update_rect, size=self.update_rect)

	def PlaceStuff(self):
		with self.canvas.before:
			Color(0.6, .6, 0.1, 1)  # yellow; colors range from 0-1 not 0-255
			self.rect = Rectangle(size=self.size, pos=self.pos)
		self.statusLabel = Label(text='Status:', color=[0.7, 0.05, 0.7, 1])
		self.add_widget(self.statusLabel)
		self.fpsLabel = Label(text='0 fps', color=[0.7, 0.05, 0.7, 1])
		self.add_widget(self.fpsLabel)
		
	def UpdateText(self, fps=0, appInfo=infoFromState[AppState.DrawingWalls]):
		self.fpsLabel.text = '{fpsValue:.0f} fps'.format(fpsValue=fps)
		self.statusLabel.text = appInfo.statusText

	def update_rect(self, instance, value):
		instance.rect.pos = instance.pos
		instance.rect.size = instance.size


class FooterLayout(BoxLayout):
	def __init__(self, start_button_callback=None, 
							reset_button_callback=None, 
							**kwargs):
		super().__init__(orientation='horizontal', padding=10, **kwargs)
		self.PlaceStuff(start_button_callback, reset_button_callback)
		self.bind(pos=self.update_rect, size=self.update_rect)

	def PlaceStuff(self, startButtonCallback, resetButtonCallback):
		with self.canvas.before:
			Color(0.4, .1, 0.4, 1)  # purple; colors range from 0-1 not 0-255
			self.rect = Rectangle(size=self.size, pos=self.pos)
		
		self.resetButton = Button(text='Reset', )
		self.resetButton.disabled = True
		if resetButtonCallback is not None:
			self.resetButton.bind(on_press=resetButtonCallback)
		self.add_widget(self.resetButton)

		self.startButton = Button(text='Start')
		self.add_widget(self.startButton)
		if startButtonCallback is not None:
			self.startButton.bind(on_press=startButtonCallback)

	def update_rect(self, instance, value):
		instance.rect.pos = instance.pos
		instance.rect.size = instance.size

	def UpdateButtons(self, appInfo=infoFromState[AppState.DrawingWalls]):
		startInfo = appInfo.startInfo
		self.startButton.text = startInfo.text
		self.startButton.disabled = not startInfo.enabled
		resetInfo = appInfo.resetInfo
		self.resetButton.text = resetInfo.text
		self.resetButton.disabled = not resetInfo.enabled

		
class FloodFill(App):
	def build(self):
		self.state = AppState.DrawingWalls
		self.curBucketColor = 0

		self.root = layout = BoxLayout(orientation = 'vertical')

		# header
		self.header = HeaderLayout(size_hint=(1, .1))
		layout.add_widget(self.header)

		# board
		self.boardLayout = boardLayout = BoardLayout(self.TouchNotificationCallback)
		layout.add_widget(boardLayout)

		# footer
		self.footer = FooterLayout(size_hint=(1, .2), 
														 start_button_callback = self.StartButtonCallback,
														 reset_button_callback = self.ResetButtonCallback)
		layout.add_widget(self.footer)

		self.InitRoom()

		Clock.schedule_interval(self.FrameN, 1/10.0)

		return layout

	def FrameN(self, dt):
		if dt != 0:
			fpsValue = 1/dt
		else:
			fpsValue = 0
		if self.state != AppState.Running:
			return

		try:
			result = next(self.generator)
			self.UpdateText(fps=fpsValue, state=self.state)
		except StopIteration:
			# kill the timer
			self.UpdateText(fps=fpsValue, state=self.state)
			self.state = AppState.Finished
			self.UpdateUX(fps=fpsValue, state=self.state)

	def UpdateUX(self, fps=0, state=AppState.DrawingWalls):
		self.footer.UpdateButtons(appInfo=infoFromState[self.state])
		self.header.UpdateText(fps=fps, appInfo=infoFromState[self.state])

	def UpdateText(self, fps, state):
		self.boardLayout.UpdateRoom()
		self.UpdateUX(fps=fps, state=self.state)

	def StartButtonCallback(self, instance):
		self.state = nextState[self.state]
		self.UpdateUX(state=self.state)

	def InitRoom(self):
		self.solver = FloodFillSolver(BigEmptyRoom(40,40))
		self.boardLayout.InitRoom(self.solver.room)
		self.state = AppState.DrawingWalls
		self.paintingColor = floorSquare
		self.boardLayout.UpdateRoom()
		self.UpdateUX(state=self.state)
		self.generator = self.solver.Generate()

	def ClearPaint(self):
		self.solver.ClearPaint()
		self.state = AppState.DrawingWalls
		self.boardLayout.UpdateRoom()
		self.UpdateUX(state=self.state)
		self.generator = self.solver.Generate()

	def ResetButtonCallback(self, instance):
		if (self.state == AppState.DrawingBuckets or 
				self.state == AppState.Finished or 
				self.state == AppState.Paused):
			self.ClearPaint()
		else:
			self.InitRoom()

	def TouchNotificationCallback(self, pos, first_touch = False):
		# pos is in fractions
		row = int(pos[1]*len(self.solver.room))
		if (len(self.solver.room) > 0):
			col = int(pos[0]*len(self.solver.room[0]))
		else:
			col = -1
		tile = [row, col]
		if self.state == AppState.DrawingBuckets:
			if first_touch:
				bucket = {'color': bucketColors[self.curBucketColor], 'pos': tile}
				self.curBucketColor = (self.curBucketColor+1)%len(bucketColors)
				self.solver.AddBucket(bucket)
		else:
			if first_touch:
				curColor = self.solver.GetColor(tile)
				if curColor == wallSquare:
					self.paintingColor = floorSquare
				else:
					self.paintingColor = wallSquare
			bucket = {'color': self.paintingColor, 'pos': tile}
			self.solver.AddBucket(bucket, painting_walls=True)
		self.boardLayout.UpdateRoom()


def Main():
	FloodFill().run()

if __name__ == '__main__':
	Main()
