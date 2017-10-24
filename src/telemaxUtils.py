import re


# ......................................................................................................................
def BuildTelemax(x: int, c: int) -> str:
    """
    utility fct to build Telemax Pointage
    """
    msg = '123456MAC:4c24e9870203PROT005170817100*Q:'
    msg += str(x + c + 1).zfill(6)
    msg += '9103'
    msg += '0071'
    msg += '0093'
    msg += '2   '
    msg += '0'
    # msg += 'xx'
    msg += '10020100^1*'
    msg += '\r\n'
    return msg


# ......................................................................................................................
def ParseTelemaxAnswer(answer: str) -> (bool, str):
    """
    utility fct to build Telemax Pointage
    """
    msg = re.sub('{##\[END_DATAGRAM\].\*\*}\r\n', '', answer)
    x = re.compile('ERRM.*')
    res = x.search(msg)
    if res:
        msg = res.group(0)
        return False, msg
    return True, msg
