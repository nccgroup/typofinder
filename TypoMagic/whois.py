#
# Typofinder for domain typo discovery
# 
# Released as open source by NCC Group Plc - http://www.nccgroup.com/
# 
# Simple whois query function
# 
# Based on RFC3912
# 
# Developed by Matt Summers, matt dot summers at nccgroup dot com
#
# http://www.github.com/nccgroup/typofinder
#
# Released under AGPL see LICENSE for more information#
#



import socket
import sys

def ourwhois(sDomain):
	# TODO, add more whois servers for other TLDs
	server = 'whois.internic.net'
	tld = sDomain[-4:]
	if tld == ".com" or tld == '.org' or tld == ".net":
		s = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
		s.connect((server , 43))
		query = sDomain + '\r\n'
		s.send(query.encode())
		response = ''
		while len(response) < 10000:
			block = s.recv(1000).decode()
			if block == '':
				break
			response = response + block
		s.shutdown
		s.close
		return response
