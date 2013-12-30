#
# Domain Bit-Flip test harness
#
# Developed by Matt Summers, matt dot summers at nccgroup dot com
#
# Written for Typofinder
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
import bitflipdomain
  
if __name__ == '__main__':
    print("Starting bit flip")
    bitflipdomain.bitflip("AAAAA")
