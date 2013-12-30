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

class typogen(object):
    """generate typo"""

    @staticmethod
    def loadkeyb(strCountry):
        keyDict = dict()

        # obviously you can have other maps here
        # I've only included this one
        filename = "./keyb" + strCountry + ".txt"
        with open(filename) as f:
            for line in f:
                split = line.rstrip().split(',')
                if split[0] in keyDict:
                    keyDict[split[0]].append(split[1])
                else:
                    keyDict[split[0]] = [split[1]]

        return keyDict

    @staticmethod
    def generatetypos(strHost,strCountry):
        """generate the typos"""

        # result list of typos
        lstTypos = []
        
        # debug
        #uniqueTypos = set(lstTypos)
        #uniqueTypos.add(strHost)
        #return uniqueTypos

        # missing characters
        idx = 0
        while idx < len(strHost):
            strTypo = strHost[0:idx]+strHost[idx+1:]
            idx+=1
            lstTypos.append(strTypo)

        # duplicate characters
        idx = 0
        while idx < len(strHost):
            strHostList = list(strHost)
            if strHostList[idx] != '.':
                strHostList.insert(idx,strHostList[idx])
                strTypo = "".join(strHostList)
                lstTypos.append(strTypo)
            idx+=1
            

        # tld swap out
        filename = "./tlds.txt"
        with open(filename) as f:
            lastdot = strHost.rfind(".")
            for line in f:
                if not line.lstrip().startswith('#'):
                    gtld = line.rstrip().lower()
                    newHost = strHost[:lastdot] + "." + gtld
                    #print(newHost)
                    lstTypos.append(newHost)

        # load keyboard mapping
        keyDict = typogen.loadkeyb(strCountry)

        # for the keyboard mapping
        for key in keyDict:
            for value in keyDict[key]:
                idx = 0
                while idx < len(strHost):
                    strHostList = list(strHost)
                    strHostList[idx] = strHostList[idx].replace(key, value)
                    strTypo = "".join(strHostList)
                    if strTypo != strHost:
                        lstTypos.append(strTypo)
                    idx+=1

        uniqueTypos = set(lstTypos)
        uniqueTypos.remove(strHost)

        return uniqueTypos

    # v2 API with two new options
    @staticmethod
    def generatetyposv2(strHost,strCountry,bTLDS,bTypos):
        """generate the typos"""

        # result list of typos
        lstTypos = []
        
        # debug
        #uniqueTypos = set(lstTypos)
        #uniqueTypos.add(strHost)
        #return uniqueTypos

        if bTypos:
            # missing characters
            idx = 0
            while idx < len(strHost):
                strTypo = strHost[0:idx]+strHost[idx+1:]
                idx+=1
                lstTypos.append(strTypo)

            # duplicate characters
            idx = 0
            while idx < len(strHost):
                strHostList = list(strHost)
                if strHostList[idx] != '.':
                    strHostList.insert(idx,strHostList[idx])
                    strTypo = "".join(strHostList)
                    lstTypos.append(strTypo)
                idx+=1
        
            # load keyboard mapping
            keyDict = typogen.loadkeyb(strCountry)

            # for the keyboard mapping
            for key in keyDict:
                for value in keyDict[key]:
                    idx = 0
                    while idx < len(strHost):
                        strHostList = list(strHost)
                        strHostList[idx] = strHostList[idx].replace(key, value)
                        strTypo = "".join(strHostList)
                        lstTypos.append(strTypo)
                        idx+=1

        #Load up the list of TLDs
        lstTlds = list()
        filename = "./tlds.txt"
        with open(filename) as f:
            for line in f:
                if not line.lstrip().startswith('#'):
                    lstTlds.append(line.rstrip().lower())

        #Remove any typos with a TLD not in the official list
        for typo in lstTypos[:]:
            lastdot = typo.rfind(".")
            if typo[lastdot + 1:] not in lstTlds:
                lstTypos.remove(typo)

        if bTLDS:
            lastdot = strHost.rfind(".")
            # tld swap out
            for gtld in lstTlds:
                newHost = strHost[:lastdot] + "." + gtld
                #print(newHost)
                lstTypos.append(newHost)

        uniqueTypos = set(lstTypos)

        try:
            uniqueTypos.remove(strHost)
        except KeyError:
            pass

        return uniqueTypos