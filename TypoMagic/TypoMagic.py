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

from types import *
import time
import http.server
import whois
import dns.resolver
import urllib
import typogen
import hostinfo
import re
from os import curdir, sep

HOST_NAME = ''      # leave like this for all
PORT_NUMBER = 801   # this will be fine

def handleHost(sHostname, self, bMX, bTypo):
    
    if(bMX == True):
        self.wfile.write(bytes("--- [host] MX Host ",'utf-8'))
    elif(bTypo == True):
        self.wfile.write(bytes("[host] Typo Host ",'utf-8'))
    else:
        self.wfile.write(bytes("[host] Host ",'utf-8'))
    
    self.wfile.write(bytes(sHostname + "<br/>",'utf-8'))  

    try:
        IPv4 = hostinfo.hostinfo.getIPv4(sHostname)
    except:
        IPv4 = None

    try:
       IPv6 = hostinfo.hostinfo.getIPv6(sHostname)
    except:
       IPv6 = None 

    if IPv4 == None and IPv6 == None:
       self.wfile.write(bytes("--- [host] No IPv6 or IPv4 address<br/>",'utf-8'))
     
    if IPv4 != None:
        for hostData in IPv4:
            if(bMX == True):
                self.wfile.write(bytes("---",'utf-8'))
            self.wfile.write(bytes("--- [host IPv4] A: " + hostData.address + " from " + sHostname + " ",'utf-8'))
            #print(hostinfo.hostinfo.getGeoImagebyIP(hostData.address))
            #print(hostinfo.hostinfo.getGeoImagebyHostname(sHostname))
            strFlag = hostinfo.hostinfo.getGeoImagebyIP(hostData.address)
            self.wfile.write(bytes(hostinfo.hostinfo.getGeoImagebyIP(hostData.address) + "<br/>",'utf-8'))
    
    if IPv6 != None:  
        for hostData in IPv6:  
            if(bMX == True):
                self.wfile.write(bytes("---",'utf-8'))
            self.wfile.write(bytes("--- [host IPv6] AAAA: " +hostData.address + " from " + sHostname + " ",'utf-8')) 
            #print(hostinfo.hostinfo.getGeoImagebyIP(hostData.address))
            #hostinfo.hostinfo.getGeoImagebyIP(hostData.address) 
            strFlag = hostinfo.hostinfo.getGeoImagebyIP(hostData.address)
            self.wfile.write(bytes(hostinfo.hostinfo.getGeoImagebyIP(hostData.address) + "<br/>",'utf-8'))   

    if bMX == False:
        IPMX = hostinfo.hostinfo.getMX(sHostname)
        if IPMX != None:
            for hostData in IPMX:
                #print(hostData.exchange)
                self.wfile.write(bytes("--- [host MX] for " + sHostname + " is " + str(hostData.exchange).strip(".") + "<br/>",'utf-8')) 
                handleHost(str(hostData.exchange).strip("."),self,True, bTypo)     
        else:
            self.wfile.write(bytes("--- [host] No MX records<br/>",'utf-8'))

    try:
        IPWWW = hostinfo.hostinfo.getWWW(sHostname)
    except:
        IPWWW = None

    if IPWWW != None:  
        for hostData in IPWWW:  
            if(bMX == False):
                self.wfile.write(bytes("--- [www.host IPv4] A: " +hostData.address + " from " + sHostname + " ",'utf-8')) 
                strFlag = hostinfo.hostinfo.getGeoImagebyIP(hostData.address)
                self.wfile.write(bytes(hostinfo.hostinfo.getGeoImagebyIP(hostData.address) + "<br/>",'utf-8'))   

    try:
        IPWebMail= hostinfo.hostinfo.getWEBMail(sHostname)
    except:
        IPWebMail = None

    if IPWebMail != None:  
        for hostData in IPWebMail:
            if(bMX == False):
                self.wfile.write(bytes("--- [webmail.host IPv4] A: " +hostData.address + " from " + sHostname + " ",'utf-8')) 
                strFlag = hostinfo.hostinfo.getGeoImagebyIP(hostData.address)
                self.wfile.write(bytes(hostinfo.hostinfo.getGeoImagebyIP(hostData.address) + "<br/>",'utf-8'))   

    try:
        IPM= hostinfo.hostinfo.getM(sHostname)
    except:
        IPM = None
    
    if IPM != None:  
        for hostData in IPM:  
            if(bMX == False):
                self.wfile.write(bytes("--- [m.host IPv4] A: " +hostData.address + " from " + sHostname + " ",'utf-8')) 
                strFlag = hostinfo.hostinfo.getGeoImagebyIP(hostData.address)
                self.wfile.write(bytes(hostinfo.hostinfo.getGeoImagebyIP(hostData.address) + "<br/>",'utf-8'))   

    if bTypo == False and bMX == False:
        #self.wfile.write(bytes("--- [host typos] Generating typos for " + sHostname + "<br/>",'utf-8')) 
        lstTypos = typogen.typogen.generatetypos(sHostname,"GB")
        #self.wfile.write(bytes("--- [host typos] Generated typos for " + sHostname + " " + str(len(lstTypos)) + "<br/>",'utf-8')) 
        if lstTypos != None:
            for strTypoHost in lstTypos:
                #self.wfile.write(bytes("--- [host typos] Checking typo " + strTypoHost + "<br/>",'utf-8')) 
                handleHost(strTypoHost,self,False,True)
                                   
    # WHOIS
    #domain = whois.query('zemes.com')
    #print(domain)
    return

class MyHandler(http.server.BaseHTTPRequestHandler):
    
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_POST(self):

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>Typo Results</title></head>",'utf-8'))
        self.wfile.write(bytes("<style type=\"text/css\">",'utf-8'))
        self.wfile.write(bytes("body {font-family:Consolas,Monaco,Lucida Console,Liberation Mono,DejaVu Sans Mono,Bitstream Vera Sans Mono,Courier New, monospace;}",'utf-8'))
        self.wfile.write(bytes("</style>",'utf-8'))
        
        length = int(self.headers['Content-Length'])
        post_data = urllib.parse.parse_qs(self.rfile.read(length).decode('utf-8'))
        
        #for key, value in post_data.items() :
        #    print (key, value)

        strHost = str(post_data['host'])[2:-2]
        if re.match('^[a-zA-Z0-9.]+$',strHost): 
            handleHost(strHost,self,False,False); 
        #self.wfile.write(bytes(strHost + "<br/>",'utf-8'))   

              
        
        return

    def do_GET(self):
        """Respond to a GET request."""

        try:
            if self.path.endswith("/"):
                f = open(curdir + sep + "index.html") 
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()
                self.wfile.write(bytes(f.read(),'UTF-8'))
                f.close()
                return
            elif self.path.endswith(".html") and self.path.find("..") != 0:
                f = open(curdir + sep + self.path) 
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return
            elif self.path.endswith(".png") and self.path.find("..") != 0:
                f = open(curdir + sep + self.path, "rb") 
                self.send_response(200)
                self.send_header('Content-type','image/png')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return
            else:
               self.send_error(404,'File Not Found: %s' % self.path)

        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)
        
if __name__ == '__main__':
    server_class = http.server.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    print (time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print (time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER))
