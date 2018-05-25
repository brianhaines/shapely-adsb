import socket
from shapely.geometry import shape, Point
from shapely.prepared import prep
import numpy as np


def main():
	
	poly_json = {
		"type": "Polygon",
		"coordinates": [[[-73.97371, 40.67048], [-73.98211, 40.69313],
		[-73.96054, 40.70279], [-73.9333, 40.70069], [-73.91155, 40.67309],
		[-73.97371, 40.67048]]]
		}
	
	poly = shape(poly_json)  # Convert geojson dict to shapely geometry
	fast = prep(poly) 

	# Stream ADS-B messages from Rp3 port via socket
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect(('192.168.1.185',30003))
	buffer = b''

	# main loop
	while True:

		# Read 1024 bytes from socket
		data = s.recv(1024)
		if not data:
			print('No Data!')
			break

		# Add the current data read by the socket to a temporary buffer
		buffer += data

		# search complete messages
		messages = buffer.split(b'\r\n')

		# we need at least 2 messages to continue
		if len(messages) == 1:
			continue
		
		# seperator found, iterate across complete messages
		for message in messages [:-1]:
			message = message.decode('utf-8').split(',')

			# If its msg type 3 with no missing values
			if message[1] == '3' and message[11] !='' and message[15]!='':
				# Print if coordinates rec'd are inside the polygon
				if fast.contains(Point(float(message[15]), float(message[14]))): # (x, y)
					print('hex: {0} alt: {1} lat: {2} lon: {3}'.format(
						message[4],message[11],message[14],message[15]))
			else:
				pass
		buffer = messages[-1]
	
if __name__ == '__main__':
	main()