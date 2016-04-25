import socket
from threading import *
import time
import sys
from datetime import datetime
import os

def pad(text, length = len("xxx.xxx.xxx.xxx"), pad = " "):
	if len(text) > length:
		if length > 10:
			return text[:length - 3] + "..."
		return text[:length]
	else:
		return text + (pad * (length - len(text)))

class TimeoutThread(Thread):
	def __init__(self, f, timeout, *args, **kwargs):
		self.time_started = time.time()
		self.timeout = timeout
		self.finished = Event()
		self.output = None
		Thread.__init__(self, None, f, None, *args, **kwargs)
		self.start()
		self._timeout()
	
	def run(self):
		try:
			if self._Thread__target:
				self.output = self._Thread__target(*self._Thread__args, **self._Thread__kwargs)
				self.finished.set()
		except:
			pass
			#~ print str(self._Thread__args) + " was not found. Time = " + str(time.time() - self.time_started)
		finally:
			# Avoid a refcycle if the thread is running a function with
			# an argument that has a member that points to the thread.
			del self._Thread__target, self._Thread__args, self._Thread__kwargs
	
	def _timeout(self):
		self.finished.wait(self.timeout)
		if not self.finished.is_set():
			self._Thread__stop()
		self.finished.set()

def recurse(current, new):
	new_stuff = []
	for c in current:
		for n in new:
			if len(c) > 0:
				new_stuff.append(c + "." + n)
			else:
				if not n in new_stuff:
					new_stuff.append(n)
	return new_stuff

def map_(small, big, current):
	return float(current - small)/float(big - small)

def percentagebar(small, big, current, bars = 20):
	percent = map_(small, big, current)
	bar = int(round(bars * percent))
	return "[%s]" % (pad("="*bar, bars))

def main():
	pattern = ""
	tries = 0
	while len(pattern.split(".")) != 4:
		prompt = "Enter IP pattern>"
		pattern = raw_input(prompt)
		shortcuts = {"home":"192.168.0:255.0:255", #192.168.*.*
					 "odyssey":"192.168.0:10.0:255"} #active subnets on World Odyssey
		if pattern == "cancel" or pattern == "exit":
			exit()
		if pattern in shortcuts:
			pattern = shortcuts[pattern]
			print "Using pattern %s" % (pattern)
		
		if len(pattern.split(".")) != 4:
			if tries == 0:
				print """Range format is as follows:
n.n.n.n where each n is a range specifier
Range specifiers are formatted as follows:
colons mark ranges (inclusize) and commas separate them. Example:
192.168.0:255.0:255 will test every IP 192.168.*.*
192.168.2:6,10.234 test IP 234 on subnets 2, 3, 4, 5, 6, and 10
0:255.0:255.0:255.0:255 every IPv4 IP. Don't. It'll take like year and a half (no exaggeration)

Commands recognized:
home - shortcut for 192.168.0:255.0:255
odyssey - shortcut for 192.168.0:10.0:255
exit or cancel - exit()"""
			else:
				print "still no. Refer to above instructions"
			tries += 1
	
	start_time = time.time()
	
	tree = [[]]*4
	data = pattern.replace(" ", "").split(".")
	for i in range(len(data)):
		c_data = data[i]
		ranges = c_data.split(",")
		for r in ranges:
			bounds = map(int, r.split(":"))
			if len(bounds) == 1:
				bounds = bounds * 2
			bounds[1] = bounds[1] + 1 #make the range inclusive
			tree[i] = tree[i] + [new for new in range(*bounds) if new not in tree[i]] #no need for dupes
	
	current = [""]*len(tree)
	for level in range(len(tree)):
		current = recurse(current, map(str, tree[level]))
	
	now = datetime.fromtimestamp(start_time)
	filename = now.strftime(os.path.join("network_scanner_logs", "%m-%d-%Y-%H-%M.txt"))
	with open(filename, "w") as f:
		f.write(pattern)
	
	known_hosts = {}
	len_things = len(tree[3])
	total_ips = len(tree[0]) * len(tree[1]) * len(tree[2]) * len(tree[3])
	ip_count = 0
	for ip in current:
		ip_data = ip.split(".")
		
		subdomain = ip.split(".")[2]
		subdomain_progessbar = percentagebar(0, len_things, tree[3].index(int(ip_data[3])))
		total_progressbar = percentagebar(0, total_ips, ip_count)
		
		sys.stdout.write("\rNow scanning subnet %s %s (%s)" % (".".join((ip_data[0], ip_data[1], subdomain)), subdomain_progessbar, total_progressbar))
		prev_subdomain = subdomain
		n = TimeoutThread(socket.gethostbyaddr, .1, [ip])
		if n.output != None:
			known_hosts[ip] = n.output[0]
			with open(filename, "a") as f:
				f.write("\n%s - %s" % (pad(ip), known_hosts[ip]))
		ip_count += 1

if __name__ == "__main__":
	main()
