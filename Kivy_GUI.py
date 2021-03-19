# More info at https://github.com/francesco-scar/arduino-robotic-arm-with-GUI

import time
import serial

from kivy.uix.widget import Widget
from kivy.properties import (NumericProperty, AliasProperty, OptionProperty,
							 ReferenceListProperty, BoundedNumericProperty,
							 StringProperty, ListProperty, BooleanProperty)

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.button import Button

BAUD_RATE = 9600

payload = ""
port = ""
arduino = ""

__all__ = ('Slider', )


time.sleep(1)

def get_port_name():
	for i in range(0, 256):														# Select right port (GNU/Linux and Windows)
		for serial_name in ['/dev/ttyUSB', '/dev/ttyACM', 'COM']:
			try:
				arduino = serial.Serial(serial_name+str(i), BAUD_RATE, timeout=.1)
				for times in range(0, 100):
					data = arduino.readline()[:-2]
					if data:
						return serial_name+str(i)
			except KeyboardInterrupt:
					return 'STOP'
			except:
				pass
	return ''

print('\n\nBasic arduino-based robotic arm controlled by a GUI running on the PC that send command to the board using serial comunication\n\nYou can find more info at https://github.com/francesco-scar/arduino-robotic-arm-with-GUI')

while port == '':
    port = get_port_name()


print('Connecting to port', port)

if port == 'STOP':
    exit()

arduino = serial.Serial(port, 9600, timeout=.5)
time.sleep(5)






class Slider(Widget):
	value = NumericProperty(0.)
	min = NumericProperty(0.)
	max = NumericProperty(100.)
	
	padding = NumericProperty('16sp')
	
	orientation = OptionProperty('horizontal', options=(
		'vertical', 'horizontal'))


	range = ReferenceListProperty(min, max)

	step = BoundedNumericProperty(0, min=0)

	background_horizontal = StringProperty(
		'atlas://data/images/defaulttheme/sliderh_background')

	background_disabled_horizontal = StringProperty(
		'atlas://data/images/defaulttheme/sliderh_background_disabled')
	

	background_vertical = StringProperty(
		'atlas://data/images/defaulttheme/sliderv_background')
	
	background_disabled_vertical = StringProperty(
		'atlas://data/images/defaulttheme/sliderv_background_disabled')

	background_width = NumericProperty('36sp')

	cursor_image = StringProperty(
		'atlas://data/images/defaulttheme/slider_cursor')

	cursor_disabled_image = StringProperty(
		'atlas://data/images/defaulttheme/slider_cursor_disabled')

	cursor_width = NumericProperty('32sp')

	cursor_height = NumericProperty('32sp')

	cursor_size = ReferenceListProperty(cursor_width, cursor_height)

	border_horizontal = ListProperty([0, 18, 0, 18])

	border_vertical = ListProperty([18, 0, 18, 0])

	value_track = BooleanProperty(False)


	value_track_color = ListProperty([1, 1, 1, 1])


	value_track_width = NumericProperty('3dp')


	sensitivity = OptionProperty('all', options=('all', 'handle'))



	def on_min(self, *largs):
		self.value = min(self.max, max(self.min, self.value))

	def on_max(self, *largs):
		self.value = min(self.max, max(self.min, self.value))

	def get_norm_value(self):
		vmin = self.min
		d = self.max - vmin
		if d == 0:
			return 0
		return (self.value - vmin) / float(d)

	def set_norm_value(self, value):
		vmin = self.min
		vmax = self.max
		step = self.step
		val = min(value * (vmax - vmin) + vmin, vmax)
		if step == 0:
			self.value = val
		else:
			self.value = min(round((val - vmin) / step) * step + vmin,
							 vmax)

	value_normalized = AliasProperty(get_norm_value, set_norm_value,
									 bind=('value', 'min', 'max'),
									 cache=True)

	def get_value_pos(self):
		padding = self.padding
		x = self.x
		y = self.y
		nval = self.value_normalized
		if self.orientation == 'horizontal':
			return (x + padding + nval * (self.width - 2 * padding), y)
		else:
			return (x, y + padding + nval * (self.height - 2 * padding))

	def set_value_pos(self, pos):
		padding = self.padding
		x = min(self.right - padding, max(pos[0], self.x + padding))
		y = min(self.top - padding, max(pos[1], self.y + padding))
		if self.orientation == 'horizontal':
			if self.width == 0:
				self.value_normalized = 0
			else:
				self.value_normalized = (x - self.x - padding
										 ) / float(self.width - 2 * padding)
		else:
			if self.height == 0:
				self.value_normalized = 0
			else:
				self.value_normalized = (y - self.y - padding
										 ) / float(self.height - 2 * padding)

	value_pos = AliasProperty(get_value_pos, set_value_pos,
							  bind=('pos', 'size', 'min', 'max', 'padding',
									'value_normalized', 'orientation'),
							  cache=True)


	def on_touch_down(self, touch):
		if self.disabled or not self.collide_point(*touch.pos):
			return
		if touch.is_mouse_scrolling:
			if 'down' in touch.button or 'left' in touch.button:
				if self.step:
					self.value = min(self.max, self.value + self.step)
				else:
					self.value = min(
						self.max,
						self.value + (self.max - self.min) / 20)
			if 'up' in touch.button or 'right' in touch.button:
				if self.step:
					self.value = max(self.min, self.value - self.step)
				else:
					self.value = max(
						self.min,
						self.value - (self.max - self.min) / 20)
		elif self.sensitivity == 'handle':
			if self.children[0].collide_point(*touch.pos):
				touch.grab(self)
		else:
			touch.grab(self)
			self.value_pos = touch.pos
		return True


	def on_touch_move(self, touch):
		if touch.grab_current == self:
			self.value_pos = touch.pos
			return True


	def on_touch_up(self, touch):
		if touch.grab_current == self:
			self.value_pos = touch.pos
			sendPayload()
			return True




class WidgetContainer(GridLayout):
	def __init__(self, **kwargs):

		super(WidgetContainer, self).__init__(**kwargs)



		self.cols = 3

		self.label1 = Label(text='Servo 1   ', font_size=25)
		self.label2 = Label(text='Servo 2   ', font_size=25)
		self.label3 = Label(text='Servo 3   ', font_size=25)
		self.label4 = Label(text='Servo 4   ', font_size=25)
		self.label5 = Label(text='Servo 5   ', font_size=25)
		self.label6 = Label(text='Servo 6   ', font_size=25)
		self.speedLabel = Label(text='Velocita\' (manuale):  50', font_size=25)


		self.servo1 = Slider(min=0, max =180, value=0)
		self.servo2 = Slider(min=0, max =180, value=100)
		self.servo3 = Slider(min=0, max =180, value=90)
		self.servo4 = Slider(min=0, max =180, value=180)
		self.servo5 = Slider(min=0, max =180, value=160)
		self.servo6 = Slider(min=0, max =80, value=0)
		self.motionSpeed = Slider(min=0, max =100, value=50)


		self.saveButton = Button(text='Salva Posizione', background_color = (0, 1, 0, 1), font_size=30)
		self.durationLabel = Label(text='Durata spostamento:  2 sec', font_size=25)
		self.motionDuration = Slider(min=0, max =10, step=0.1, value=2)
		self.cancelButton = Button(text='Elimina Ultima Posizione', background_color = (1, 0, 0, 1), font_size=30)
		self.eepromButton = Button(text='Esegui Posizioni in EEPROM', font_size=30)
		self.executeButton = Button(text='Esegui Posizioni Salvate', background_color = (0, 0, 1, 1), font_size=30)
		self.exitButton = Button(text='Chiudi ed Esci', background_color = (100, 0, 0, 1), font_size=30)



		self.add_widget(self.label1)
		self.add_widget(self.servo1)
		self.add_widget(self.durationLabel)

		self.add_widget(self.label2)
		self.add_widget(self.servo2)
		self.add_widget(self.motionDuration)

		self.add_widget(self.label3)
		self.add_widget(self.servo3)
		self.add_widget(self.saveButton)


		self.add_widget(self.label4)
		self.add_widget(self.servo4)
		self.add_widget(self.cancelButton)

		self.add_widget(self.label5)
		self.add_widget(self.servo5)
		self.add_widget(self.eepromButton)

		self.add_widget(self.label6)
		self.add_widget(self.servo6)
		self.add_widget(self.executeButton)

		self.add_widget(self.speedLabel)
		self.add_widget(self.motionSpeed)
		self.add_widget(self.exitButton)


		self.servo1.bind(value=self.updateText1)
		self.servo2.bind(value=self.updateText2)
		self.servo3.bind(value=self.updateText3)
		self.servo4.bind(value=self.updateText4)
		self.servo5.bind(value=self.updateText5)
		self.servo6.bind(value=self.updateText6)
		self.motionSpeed.bind(value=self.updateTextSpeed)
		self.motionDuration.bind(value=self.updateTextDuration)
		self.saveButton.bind(on_press=self.savePosition)
		self.cancelButton.bind(on_press=self.cancelPosition)
		self.eepromButton.bind(on_press=self.eeprom)
		self.executeButton.bind(on_press=self.execute)
		self.exitButton.bind(on_press=exit)

#		self.servo2.bind(on_touch_up=self.func)

#	def func (self, instance, val):
#		print(instance)
#		print(val)
#		print("here")

	def updateText1(self, instance, val):
		self.label1.text = "Servo 1:  %d"%val
		self.updatePayload()
	def updateText2(self, instance, val):
		self.label2.text = "Servo 2:  %d"%val
		self.updatePayload()
	def updateText3(self, instance, val):
		self.label3.text = "Servo 3:  %d"%val
		self.updatePayload()
	def updateText4(self, instance, val):
		self.label4.text = "Servo 4:  %d"%val
		self.updatePayload()
	def updateText5(self, instance, val):
		self.label5.text = "Servo 5:  %d"%val
		self.updatePayload()
	def updateText6(self, instance, val):
		self.label6.text = "Servo 6:  %d"%val
		self.updatePayload()
	def updateTextSpeed(self, instance, val):
		self.speedLabel.text = "Velocita\' (manuale):  %d"%val
		self.updatePayload()
	def updateTextDuration(self, instance, val):
		self.durationLabel.text = "Durata spostamento:  %.1f sec"%val



	def updatePayload(self):
		global payload
		payload = str(int(self.servo1.value))+'|'+str(int(self.servo2.value))+'|'+str(int(self.servo3.value))+'|'+str(int(self.servo4.value))+'|'+str(int(self.servo5.value))+'|'+str(int(self.servo6.value))+'|'+str(int(self.motionSpeed.value))+'|$'


	def savePosition (self, arg):
		payload = '|'+str(int(self.servo1.value))+'|'+str(int(self.servo2.value))+'|'+str(int(self.servo3.value))+'|'+str(int(self.servo4.value))+'|'+str(int(self.servo5.value))+'|'+str(int(self.servo6.value))+'|'+str(int(self.motionDuration.value*1000))+'|$'
		arduino.write(payload.encode())
		print("Saved: "+payload)

	def cancelPosition(self, arg):
		arduino.write("-".encode())
		print("Ultima posizione cancellata")

	def eeprom (self, arg):
		arduino.write("*".encode())
		print("Inizio esecuzione da EEPROM")

	def execute (self, arg):
		arduino.write("+".encode())
		print("Inizio esecuzione posizioni salvate")


def sendPayload():
	arduino.write(payload.encode())
	print(payload)





if __name__ == '__main__':
	from kivy.app import App

	class SliderApp(App):
		def build(self):
			return WidgetContainer()

	SliderApp().run()

