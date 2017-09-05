import re
import urllib

def check_devops_status(shortname):

    if shortname:
        try:
            DEVOPS_URL = 'http://devops.oraclecorp.com/host/api/%s/data' % shortname
            response = urllib.urlopen(DEVOPS_URL)
            result = response.read().decode('utf-8')
            if re.search('(type=hypervisor|type=server)', result.lower()):
                if re.search('status=active', result.lower()):
                    return True
                else:
                    return False

        except:
            return False




