from os import name
from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout
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
					posThis = [squarePos[0]+squareSize[0]*col/numCols, squarePos[1]+squareSize[1]*row/numRows]
					posNext = [squarePos[0]+squareSize[0]*(col+1)/numCols, squarePos[1]+squareSize[1]*(row+1)/numRows]
					size = [posNext[0]-posThis[0], posNext[1]-posThis[1]]
					Color(squareColor[0], squareColor[1], squareColor[2], squareColor[3])
					Rectangle(size = size, pos=posThis)


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
	def __init__(self, **kwargs):
		super().__init__(orientation='horizontal', padding=10, **kwargs)
		self.running = False
		self.PlaceStuff()
		self.bind(pos=self.update_rect, size=self.update_rect)

	def PlaceStuff(self):
		with self.canvas.before:
			Color(0.4, .1, 0.4, 1)  # purple; colors range from 0-1 not 0-255
			self.rect = Rectangle(size=self.size, pos=self.pos)
		
		self.resetButton = Button(text='Reset', )
		self.resetButton.disabled = True
		self.add_widget(self.resetButton)

		self.startButton = Button(text='')
		self.add_widget(self.startButton)
		self.UpdateStartButtonText()
		self.startButton.bind(on_press=self.HandleStartButton)

	def update_rect(self, instance, value):
		instance.rect.pos = instance.pos
		instance.rect.size = instance.size

	def HandleStartButton(self, instance):
		self.running = not self.running
		self.UpdateStartButtonText()

	def UpdateStartButtonText(self):
		if self.running:
			self.startButton.text = 'Pause'
		else:
			self.startButton.text = 'Start'

	def IsPaused(self):
		return not self.running

	def SetButtonsState(self, start_button_text):
		if start_button_text == 'Pause':
			self.running = True;
		if start_button_text == 'Start':
			self.running = False
		self.UpdateStartButtonText()


class FloodFill(App):
	def build(self):
		self.root = layout = BoxLayout(orientation = 'vertical')

		# header
		self.header = HeaderLayout(size_hint=(1, .1))
		layout.add_widget(self.header)

		# board
		self.boardLayout = boardLayout = BoardLayout()
		layout.add_widget(boardLayout)

		# footer
		self.footer = FooterLayout(size_hint=(1, .2))
		layout.add_widget(self.footer)

		self.solver = FloodFillSolver(smallRoom)
		for bucket in buckets:
			self.solver.AddBucket(bucket)
		self.boardLayout.InitRoom(self.solver.room)

		self.generator = self.solver.Generate()
		Clock.schedule_interval(self.FrameN, 1.0)

		return layout

	def FrameN(self, dt):
		if dt != 0:
			fpsValue = 1/dt
		else:
			fpsValue = 0
		if self.footer.IsPaused():
			return

		try:
			result = next(self.generator)
			self.UpdateText(fps=fpsValue)
		except StopIteration:
			# kill the timer
			self.UpdateText(fps=fpsValue, updatePositions = self.footer.IsPaused)
			self.footer.SetButtonsState(start_button_text = 'Start')

	def UpdateText(self, fps, updatePositions = True):
		self.header.UpdateText(fps = fps)
		self.boardLayout.UpdateRoom()

def Main():
	FloodFill().run()

if __name__ == '__main__':
	Main()
