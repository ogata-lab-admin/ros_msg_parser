

_primitives = [
    'bool',
    'int8',
    'uint8',
    'int16',
    'uint16',
    'int32',
    'uint32',
    'int64',
    'uint64',
    'float32',
    'float64',
    'string',
    'time',
    'duration']

class MsgException(Exception):
    _msg = 'MsgException'

    def addInfo(self, i, line):
        self._i = i
        self._line = line

    def __str__(self):
        return '%s(line=%d, str=%s)' % (self._msg, self._i, self._line)

class InvalidInnerTypeName(MsgException):
    _msg = 'InvalidInnerTypeName'
    pass
 
class InvalidPrimitiveTypeName(MsgException):
    _msg = 'InvalidPrimitiveTypeName'
    pass

class InvalidArgument(MsgException):
    def __init__(self, msg):
        self._msg = msg

    def __str__(self):
        return self._msg

class MsgMemberList(object):
    
    def __init__(self):
        self._m = []

    def append(self, m):
        self._m.append(m)

    def forEach(self, func):
        for m in self._m:
            func(m)

    def filter(self, func):
        return [m for m in self._m if func(m)]
                
    def findByName(self, name):
        rs = self.filter(lambda m:m.name == name)
        if len(rs) == 0: return None
        elif len(rs) == 1: return rs[0]
        else: raise InvalidArgument('Find multiple members by one name(%s)' % name)


class MsgType(object):
    def __init__(self, name):
        self._is_primitive = False
        self.__check_typename(name)
        self._name = name
    
    @property
    def is_primitive(self):
        return self._is_primitive

    @property
    def fullName(self):
        return self._name

    @property
    def name(self):
        if self.is_primitive:
            return self._name
        return self._name.split('/')[1]

    @property
    def packageName(self):
        if self.is_primitive:
            return None
        return self._name.split('/')[0]

    def __check_typename(self, n):
        if n.find('/') >= 0:
            ns = n.split('/')
            if len(ns) < 2:
                raise InvalidInnerTypeName()
            elif len(ns) > 2:
                raise InvalidInnerTypeName()
            return
        
        if not n in _primitives:
            raise InvalidPrimitiveTypeName
        self._is_primitive = True
        return

    def __str__(self):
        return self._name


class MsgMember(object):
    
    def __init__(self, type, name):
        self._type = type
        self._name = name

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type
    
class MsgObject(object):

    def __init__(self, pkgName, name):
        self._name = name
        self._pkgName = pkgName
        self._members = MsgMemberList()

    def addMember(self, m):
        self._members.append(m)

    @property
    def packageName(self):
        return self._pkgName

    @property
    def name(self):
        return self._name

    @property
    def members(self):
        return self._members


class Parser(object):

    def __init__(self):
        pass


    def parse_str(self, name, argstr):
        p = name.split('/')
        if len(p) != 2:
            raise InvalidArgument('Invalid Package/Filename format(%s)' % name)

        msg = MsgObject(p[0], p[1])

        for i, line in enumerate(argstr.split('\n')):
            try:
                line = line.strip()
                if len(line) == 0: # empty line
                    continue
                ms = line.strip().split()
                if len(ms) != 2:
                    raise InvalidArgument('Invalid Syntax(line=%s)' % i)
                m = MsgMember(MsgType(ms[0]), ms[1])
                msg.addMember(m)
            except MsgException, e:
                e.addInfo(i, line)
                raise e
        return msg

