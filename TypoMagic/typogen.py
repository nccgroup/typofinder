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

    def loadkeyb(strCountry):
        keyDict = dict()

        # obviously you can have other maps here
        # I've only included this one
        filename = "./keyb" + strCountry + ".txt"
        mynumbers = []
        with open(filename) as f:
            for line in f:
                split = line.rstrip().split(',')
                if split[0] in keyDict:
                    keyDict[split[0]].append(split[1])
                else:
                    keyDict[split[0]] = [split[1]]

        return keyDict

    def generatetypos(strHost,strCountry):
        """generate the typos"""

        lstTypos = []
        idx = 0

        # missing characters
        while(idx < len(strHost)):
            strTypo = strHost[0:idx]+strHost[idx+1:]
            idx+=1
            lstTypos.append(strTypo)

        # load
        keyDict = typogen.loadkeyb(strCountry)

        for key in keyDict:
            for value in keyDict[key]:
                idx = 0
                while(idx < len(strHost)):
                    strHostList = list(strHost)
                    strHostList[idx] = strHostList[idx].replace(key, value)
                    strTypo = "".join(strHostList)
                    if strTypo != strHost:
                        lstTypos.append(strTypo)
                    idx+=1

        return set(lstTypos)