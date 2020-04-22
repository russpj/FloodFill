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


class AppState(Enum):
	Ready = 1
	Running = 2
	Paused = 3
	Finished = 4


# BoardLayout encapsulates the playing board
class BoardLayout(BoxLayout):
	def __init__(self):
		super().__init__()
		self.room = []
		self.PlaceStuff()
		self.bind(pos=self.update_rect, size=self.update_rect)

	def PlaceStuff(self):
		pass

	def InitRoom(self, room):
		self.room = room

	def update_rect(self, instance, value):
		self.UpdateRoom()

	def UpdateRoom(self):
		rectSize = self.size
		rectPos = self.pos
		squareSize = []
		squarePos = []

		if rectSize[0] > rectSize[1]:
			# wider than tall
			squareSize = [rectSize[1], rectSize[1]]
			squarePos = [rectPos[0]+(rectSize[0]-squareSize[0])/2, rectPos[1]]
		else:
			# taller than wide
			squareSize = [rectSize[0], rectSize[0]]
			squarePos = [rectPos[0], rectPos[1]+(rectSize[1]-squareSize[1])/2]

		with self.canvas:
			self.canvas.clear()
			Color(0.5, 0.5, 0.5, 1)
			Rectangle(size=rectSize, pos=rectPos)

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

	def on_touch_down(self, touch):
		print('Touch down at {touch} in pos={pos}, size={size}'.
				format(touch=touch, pos=self.pos, size=self.size))

	def on_touch_up(self, touch):
		print('Touch up at {touch}'.format(touch=touch))

	def on_touch_move(self, touch):
		print('Touch move at {touch}'.format(touch=touch))


class HeaderLayout(BoxLayout):
	def __init__(self, **kwargs):
		super().__init__(orientation='horizontal', **kwargs)
		self.PlaceStuff()
		self.bind(pos=self.update_rect, size=self.update_rect)

	def PlaceStuff(self):
		with self.canvas.before:
			Color(0.6, .6, 0.1, 1)  # yellow; colors range from 0-1 not 0-255
			self.rect = Rectangle(size=self.size, pos=self.pos)
		self.fpsLabel = Label(text='0 fps', color=[0.7, 0.05, 0.7, 1])
		self.add_widget(self.fpsLabel)
		
	def UpdateText(self, fps):
		self.fpsLabel.text = '{fpsValue:.0f} fps'.format(fpsValue=fps)

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

	def UpdateButtons(self, state):
		if state==AppState.Finished:
			self.startButton.text = 'Start'
			self.startButton.disabled = True
			self.resetButton.text = 'Reset'
			self.resetButton.disabled = False
			return
		if state == AppState.Paused or state == AppState.Ready:
			self.startButton.text = 'Start'
			self.startButton.disabled = False
			self.resetButton.text = 'Reset'
			self.resetButton.disabled = True
			return
		if state == AppState.Running:
			self.startButton.text = 'Pause'
			self.startButton.disabled = False
			self.resetButton.text = 'Reset'
			self.resetButton.disabled = True
			return

		
class FloodFill(App):
	def build(self):
		self.state = AppState.Ready

		self.root = layout = BoxLayout(orientation = 'vertical')

		# header
		self.header = HeaderLayout(size_hint=(1, .1))
		layout.add_widget(self.header)

		# board
		self.boardLayout = boardLayout = BoardLayout()
		layout.add_widget(boardLayout)

		# footer
		self.footer = FooterLayout(size_hint=(1, .2), 
														 start_button_callback = self.StartButtonCallback,
														 reset_button_callback = self.ResetButtonCallback)
		layout.add_widget(self.footer)

		self.InitRoom()

		Clock.schedule_interval(self.FrameN, 0.3)

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
			self.UpdateText(fps=fpsValue)
		except StopIteration:
			# kill the timer
			self.UpdateText(fps=fpsValue)
			self.state = AppState.Finished
			self.footer.UpdateButtons(self.state)

	def UpdateText(self, fps):
		self.header.UpdateText(fps = fps)
		self.boardLayout.UpdateRoom()
		self.footer.UpdateButtons(self.state)

	def StartButtonCallback(self, instance):
		if self.state == AppState.Ready or self.state == AppState.Paused:
			self.state = AppState.Running
		else:
			if self.state == AppState.Running:
				self.state = AppState.Paused
		self.footer.UpdateButtons(self.state)

	def InitRoom(self):
		self.solver = FloodFillSolver(copy.deepcopy(smallRoom))
		for bucket in buckets:
			self.solver.AddBucket(bucket)
		self.boardLayout.InitRoom(self.solver.room)
		self.state = AppState.Ready
		self.boardLayout.UpdateRoom()
		self.footer.UpdateButtons(self.state)
		self.generator = self.solver.Generate()

	def ResetButtonCallback(self, instance):
		self.InitRoom()


def Main():
	FloodFill().run()

if __name__ == '__main__':
	Main()
