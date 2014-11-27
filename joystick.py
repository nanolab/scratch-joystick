import usb.core
import time
from blockext import *

device = usb.core.find(idVendor=0x0079, idProduct=0x0006)
device.set_configuration()
endpoint = device[0][(0,0)][0]

class Joystick:

	def __init__(self):
		self.data = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

	@command("read joystick", is_blocking=True)
	def joystick_read_data(self):
		try:
			self.data = device.read(endpoint.bEndpointAddress, endpoint.wMaxPacketSize)
		except usb.core.USBError as e:
			self.data = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
			print("USB error")
		print(bin(self.data[5])[2:].zfill(8))
			
	@predicate("joystick button %m.button pressed?")
	def joystick_button_pressed(self, button):
		if button in {"1", "2", "3", "4"}:
			mask = {
				"1": 0b00010000,
				"2": 0b00100000,
				"3": 0b01000000,
				"4": 0b10000000,
			}[button]
			if self.data[5] & mask > 0:
				return True
		elif button in {"L1", "R1", "L2", "R2", "9", "10", "S1", "S2"}:
			mask = {
				"L1": 0b00000001,
				"R1": 0b00000010,
				"L2": 0b00000100,
				"R2": 0b00001000,
				"9":  0b00010000,
				"10": 0b00100000,
				"S1": 0b01000000,
				"S2": 0b10000000,
			}[button]
			if self.data[6] & mask > 0:
				return True
				
	@reporter("joystick %m.axis axis")
	def joystick_axis(self, axis):
		axis = {
			"x" : 0,
			"y" : 1,
			"throttle" : 3,
			"rudder" : 4,
		}[axis]
		return self.data[axis]

descriptor = Descriptor(
    name = "Joystick",
    port = 5002,
    blocks = get_decorated_blocks_from_class(Joystick),
    menus = dict(
        button = ["1", "2", "3", "4", "L1", "R1", "L2", "R2", "9", "10", "S1", "S2"],
		axis = ["x", "y", "throttle", "rudder"]
    ),
)

extension = Extension(Joystick, descriptor)

if __name__ == "__main__":
    extension.run_forever(debug=True)
