from hackerman.transport import tcp
from hackerman.crypto import xor, rsa, blowfish

from mssh import messages as msg
from mssh import errors

class Client(object):
	def __init__(self, addr, enc_func, dec_func):
		conn = tcp.Client(addr)
		who = conn.recv()
		if who == msg.am_mssh:
			conn.send(msg.am_mssh)
		else:
			raise errors.NotMSSH("Server did not respond as mssh")
		self.conn = conn
		self.enc = enc_func
		self.dec = dec_func

	def sh(self, cmd):
		enc = self.enc(cmd.encode())
		self.conn.send(enc)
		
		while True:
			try:
				recv = self.dec(self.conn.recv())
				if recv.endswith(msg.end_t):
					print(utils.force_decode(recv.split(msg.end_t)[0]))
					break
				else:
					print(utils.force_decode(recv))
			except KeyboardInterrupt:
				self.conn.send(self.enc(msg.ctrl_c))
				final = self.dec(self.conn.recv())
				while not final.endswith(msg.ctrl_c):
					final += self.dec(self.conn.recv())
				final = final.replace(msg.ctrl_c,b'')
				final = final.replace(msg.end_t, b'')
				print(utils.force_decode(final),"^C\n")
