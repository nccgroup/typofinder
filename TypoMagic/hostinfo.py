#
# Typofinder for domain typo discovery
# 
# Released as open source by NCC Group Plc - http://www.nccgroup.com/
# 
# Developed by Ollie Whitehouse, ollie dot whitehouse at nccgroup dot com
#
# http://www.github.com/nccgroup/typofinder
#
# Released under AGPL see LICENSE for more information#
#

import dns.resolver
import pygeoip

class hostinfo(object):
    """Host information class"""

    def __init__(self):
        self._resolver = dns.resolver.Resolver()
        self._gi = pygeoip.GeoIP('GeoIP.dat')

    def getWWW(self, sHostname):
        # WWW
        try:
            dnsAnswers = self._resolver.query("www." + sHostname, 'A')
            return dnsAnswers
        except dns.exception.Timeout:
            return None
        except dns.resolver.NoAnswer:
            return None
        except dns.resolver.NXDOMAIN:
            return None

    def getM(self, sHostname):
        # M
        try:
            dnsAnswers = self._resolver.query("m." + sHostname, 'A')
            return dnsAnswers
        except dns.exception.Timeout:
            return None
        except dns.resolver.NoAnswer:
            return None
        except dns.resolver.NXDOMAIN:
            return None

    def getWEBMail(self, sHostname):
        # webmail
        try:
            dnsAnswers = self._resolver.query("webmail." + sHostname, 'A')
            return dnsAnswers
        except dns.exception.Timeout:
            return None
        except dns.resolver.NoAnswer:
            return None
        except dns.resolver.NXDOMAIN:
            return None

    def getMX(self, sHostname):
        # MX
        try:
            dnsAnswers = self._resolver.query(sHostname, 'MX')
            return dnsAnswers
        except dns.exception.Timeout:
            return None
        except dns.resolver.NoAnswer:
            return None
        except dns.resolver.NXDOMAIN:
            return None

    def getIPv4(self, sHostname):
        # IPv4
        try:  
            dnsAnswers = self._resolver.query(sHostname, 'A')
            return dnsAnswers
        except dns.exception.Timeout:
            return None
        except dns.resolver.NoAnswer:
            return None

    def getIPv6(self, sHostname):
        # IPv6
        try:       
            dnsAnswers = self._resolver.query(sHostname, 'AAAA')
            return dnsAnswers
        except dns.exception.Timeout:
            return None
        except dns.resolver.NoAnswer:
            return None

    def getGeobyIP(self, sIP):
        try:
            # Geo Location
            #print(gi.country_code_by_addr(sIP))
            return self._gi.country_code_by_addr(sIP)
        except Exception as e:
            #print("Error doing getGeoIP ")
            pass

    def getGeobyHostname(self, sHostname):
        try:
            # Geo Location
            #print(gi.country_code_by_name(sHostname))
            return self._gi.country_code_by_name(sHostname)
        except Exception as e:
            #print("Error doing getGeoHostname ")
            pass

    def getGeoImagebyIP(self, sIP):
        try:
            return "<img src=\"/flags/flags-iso/shiny/16/"+ self.getGeobyIP(sIP)+".png\" alt=\"" + self.getGeobyIP(sIP) + "\">"
        except Exception as e:
            #print("Error doing getGeoImagebyIP ")
            return "<img src=\"/flags/flags-iso/shiny/16/_unknown.png\">"

    def getGeoImagebyHostname(self, sHostname):
        try:
            return "<img src=\"/flags/flags-iso/shiny/16/"+ self.getGeobyHostname(sHostname)+".png\" alt=\"" + self.getGeobyHostname(sHostname) + "\">"
        except Exception as e:
            #print("Error doing getGeoImagebyHostname ")
            return "<img src=\"/flags/flags-iso/shiny/16/_unknown.png\">"
            
        