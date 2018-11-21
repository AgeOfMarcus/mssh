from hackerman.transport import tcp
from hackerman.crypto import xor, rsa, blowfish
from subprocess import Popen, PIPE
import os, signal

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

		quit = False

		while True:
			cmd = self.dec(self.conn.recv()).decode()

			proc = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
			for ln in iter(proc.stdout.readline, b''):
				if self.dec(self.conn.recv()) == msg.ctrl_c:
					os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
					self.conn.send(self.enc(ln))
					self.conn.send(self.enc(msg.ctrl_c))
					nope = True
					break
				else:
					self.conn.send(self.enc(ln))


			if not nope: self.conn.send(self.enc(msg.end_t))
			if nope: nope = False