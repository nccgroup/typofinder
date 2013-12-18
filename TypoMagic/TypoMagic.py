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

import time
import http.server
import urllib
import re
from os import curdir, sep
from socketserver import ThreadingMixIn
from dns.resolver import NoNameservers
import typogen
import hostinfo


HOST_NAME = ''      # leave like this for all
PORT_NUMBER = 801   # this will be fine

_hostinfo = hostinfo.hostinfo()

def handleHost(sHostname, self, bMX, bTypo):
    
    if bMX:
        self.wfile.write(bytes("--- [host] MX Host ",'utf-8'))
    elif bTypo:
        self.wfile.write(bytes("[host] Typo Host ",'utf-8'))
    else:
        self.wfile.write(bytes("[host] Host ",'utf-8'))
    
    self.wfile.write(bytes(sHostname + "<br/>",'utf-8'))  

    try:
        IPv4 = _hostinfo.getIPv4(sHostname)
    except:
        IPv4 = None

    try:
       IPv6 = _hostinfo.getIPv6(sHostname)
    except:
       IPv6 = None 

    if IPv4 is None and IPv6 is None:
       self.wfile.write(bytes("--- [host] No IPv6 or IPv4 address<br/>",'utf-8'))
     
    if IPv4 is not None:
        for hostData in IPv4:
            if bMX:
                self.wfile.write(bytes("---",'utf-8'))
            self.wfile.write(bytes("--- [host IPv4] A: " + hostData.address + " from " + sHostname + " ",'utf-8'))
            #print(_hostinfo.getGeoImagebyIP(hostData.address))
            #print(_hostinfo.getGeoImagebyHostname(sHostname))
            strFlag = _hostinfo.getGeoImagebyIP(hostData.address)
            self.wfile.write(bytes(strFlag + "<br/>",'utf-8'))
    
    if IPv6 is not None:
        for hostData in IPv6:  
            if bMX:
                self.wfile.write(bytes("---",'utf-8'))
            self.wfile.write(bytes("--- [host IPv6] AAAA: " +hostData.address + " from " + sHostname + " ",'utf-8')) 
            #print(_hostinfo.getGeoImagebyIP(hostData.address))
            #_hostinfo.getGeoImagebyIP(hostData.address) 
            strFlag = _hostinfo.getGeoImagebyIP(hostData.address)
            self.wfile.write(bytes(strFlag + "<br/>",'utf-8'))   

    if not bMX:
        try:
            IPMX = _hostinfo.getMX(sHostname)
        except NoNameservers:
            IPMX = None
        
        if IPMX is not None:
            for hostData in IPMX:
                #print(hostData.exchange)
                self.wfile.write(bytes("--- [host MX] for " + sHostname + " is " + str(hostData.exchange).strip(".") + "<br/>",'utf-8')) 
                handleHost(str(hostData.exchange).strip("."),self,True, bTypo)     
        else:
            self.wfile.write(bytes("--- [host] No MX records<br/>",'utf-8'))

    try:
        IPWWW = _hostinfo.getWWW(sHostname)
    except:
        IPWWW = None

    if IPWWW is not None:
        for hostData in IPWWW:  
            if not bMX:
                self.wfile.write(bytes("--- [www.host IPv4] A: " +hostData.address + " from " + sHostname + " ",'utf-8')) 
                strFlag = _hostinfo.getGeoImagebyIP(hostData.address)
                self.wfile.write(bytes(strFlag + "<br/>",'utf-8'))   

    try:
        IPWebMail= _hostinfo.getWEBMail(sHostname)
    except:
        IPWebMail = None

    if IPWebMail is not None:
        for hostData in IPWebMail:
            if not bMX:
                self.wfile.write(bytes("--- [webmail.host IPv4] A: " +hostData.address + " from " + sHostname + " ",'utf-8')) 
                strFlag = _hostinfo.getGeoImagebyIP(hostData.address)
                self.wfile.write(bytes(strFlag + "<br/>",'utf-8'))   

    try:
        IPM= _hostinfo.getM(sHostname)
    except:
        IPM = None
    
    if IPM is not None:
        for hostData in IPM:  
            if not bMX:
                self.wfile.write(bytes("--- [m.host IPv4] A: " +hostData.address + " from " + sHostname + " ",'utf-8')) 
                strFlag = _hostinfo.getGeoImagebyIP(hostData.address)
                self.wfile.write(bytes(strFlag + "<br/>",'utf-8'))   

    if bTypo == False and bMX == False:
        #self.wfile.write(bytes("--- [host typos] Generating typos for " + sHostname + "<br/>",'utf-8')) 
        lstTypos = typogen.typogen.generatetypos(sHostname,"GB")
        #self.wfile.write(bytes("--- [host typos] Generated typos for " + sHostname + " " + str(len(lstTypos)) + "<br/>",'utf-8')) 
        if lstTypos is not None:
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
        self.wfile.write(bytes("<html><head><title>NCC Typo Finder Results</title></head>",'utf-8'))
        self.wfile.write(bytes("<style type=\"text/css\">",'utf-8'))
        self.wfile.write(bytes("body {font-family:Consolas,Monaco,Lucida Console,Liberation Mono,DejaVu Sans Mono,Bitstream Vera Sans Mono,Courier New, monospace;}",'utf-8'))
        self.wfile.write(bytes("</style>",'utf-8'))
        self.wfile.write(bytes("Released under AGPL by <a href=\"http://www.nccgroup.com/\">NCC Group</a> - source available <a href=\"https://github.com/nccgroup/typofinder\">here</a><br/>",'utf-8'))
        

        length = int(self.headers['Content-Length'])
        post_data = urllib.parse.parse_qs(self.rfile.read(length).decode('utf-8'))
        
        #for key, value in post_data.items() :
        #    print (key, value)

        strHost = str(post_data['host'])[2:-2]
        if re.match('^[a-zA-Z0-9.-]+$',strHost): 
            handleHost(strHost,self,False,False)
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

class MultiThreadedHTTPServer(ThreadingMixIn, http.server.HTTPServer):
    pass
        
if __name__ == '__main__':
    server_class = http.server.HTTPServer
    #httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    httpd = MultiThreadedHTTPServer((HOST_NAME, PORT_NUMBER), MyHandler)
    print (time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print (time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER))
