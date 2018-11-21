from hackerman.transport import tcp
from hackerman.crypto import xor, rsa, blowfish

from mssh import messages as msg
from mssg import errors

class Server(object):
	def __init__(self, port, enc_func, dec_func):
		conn = tcp.Server(port)
		conn.send(msg.am_mssh)
		if not conn.recv() == msg.am_mssh:
			conn.exit()
			raise errors.notMSSH("Client did not respond as mssh")
		self.conn = conn
		self.enc = enc_func 
		self.dec = dec_func

		while True:
			cmd = self.dec(self.conn.recv()).decode()

			pipe = utils.interactive_sh #CONT