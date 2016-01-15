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

import sys
import codecs
import argparse
import requests
import simplejson

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--domain', help='domain to analyze', required=False, type=str, default='nccgroup.com')
    parser.add_argument('-s', '--server',   help='server to use', required=False, type=str, default='https://labs.nccgroup.trust')
    args = parser.parse_args()

    requests.packages.urllib3.disable_warnings()
    
    strURLTypos  = args.server + "/typofinder/typov2.ncc"
    strURLEntity = args.server +  "/typofinder/entitylight.ncc"

    strHTTPHdrs      = {'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Accept': 'text/plain'}
    strTypoRequest   = "host="+args.domain+"&typos=typos&typoamount=1&tld=tld&bitflip=bitflip&homoglyph=homoglyph&doppelganger=doppelganger&charsetamount=&alexafilter=neveralexa"
    strEntityRequest = "host="
    
    arrTypoResp = requests.post(strURLTypos, data=strTypoRequest, headers=strHTTPHdrs, verify=False)

    if arrTypoResp.text.startswith("[!]"):
        print(arrTypoRest.text)
        sys.exit(0)

    strTypoJSON = arrTypoResp.json()

    for strTDomain in strTypoJSON:
        
        dataFoo = strEntityRequest+strTDomain
        
        try:
            arrDomainResp = requests.post(strURLEntity, data=dataFoo, headers=strHTTPHdrs, verify=False)
            #print(arrDomainResp.text)

            try:
                strDEntityJSON = arrDomainResp.json()
            
                print("[i] " + strDEntityJSON['strDomain'])
                if strDEntityJSON['bError'] is False:
                    for server in strDEntityJSON['nameservers']:
                        print ("[i]    --- " + server);
                else:
                        print ("[!]    --- " + strDEntityJSON['strError'])

            except simplejson.scanner.JSONDecodeError:
                print("[!] JSON decode error")

        except ConnectionAbortedError:
            print("[!] Connected abort for " + print(strTDomain.encode('cp437', 'replace')))

        except ConnectionError:
            print("[!] Connected error for " + print(strTDomain.encode('cp437', 'replace')))
