import traceback

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

    def map(self, func):
        return [func(m) for m in self._m]
    
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
    
    def __init__(self, type, name, comment=''):
        self._type = type
        self._name = name
        self._comment = comment

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type

    @property
    def comment(self):
        return self._comment
    
class MsgObject(object):

    def __init__(self, pkgName, name):
        self._name = name
        self._pkgName = pkgName
        self._members = MsgMemberList()
        self._comment = ''

    def addComment(self, c):
        self._comment = c
        
    def addMember(self, m):
        self._members.append(m)

    @property
    def comment(self):
        return self._comment
    
    @property
    def packageName(self):
        return self._pkgName

    @property
    def name(self):
        return self._name

    @property
    def members(self):
        return self._members


class SrvObject(object):

    def __init__(self, pkgName, name):
        self._name = name
        self._pkgName = pkgName
        self._comment = ''
        self.arg = MsgObject(pkgName, name + '_arg')
        self.returns = MsgObject(pkgName, name + '_returns')
        
    def addComment(self, c):
        self._comment = c

    @property
    def comment(self):
        return self._comment
    
    @property
    def packageName(self):
        return self._pkgName

    @property
    def name(self):
        return self._name


class Parser(object):

    def __init__(self):
        pass

    def __parse_name(self, name):
        p = name.split('/')
        if len(p) != 2:
            raise InvalidArgument('Invalid Package/Filename format(%s)' % name)
        return p
    
    def parse_srv_str(self, name, argstr):
        p = self.__parse_name(name)
        srv = SrvObject(p[0], p[1])

        comment = None
        commentLines = []
        commentPhase = 'srv'
        argparsing = True
        for i, line in enumerate(argstr.split('\n')):
            try:
                line = line.strip()
                # print('%d:%s:%s:%s' % (i, line, comment, commentLines))
                if line.startswith('#') and (not commentPhase is 'end'):
                    commentLines.append(line[1:].strip())
                    continue
                
                if comment is None:
                    comment = '\n'.join(commentLines)
                
                if commentPhase == 'srv':
                    srv.addComment(comment if comment else '')
                    commentPhase = 'arg'
                    comment = None
                    commentLines = []
                elif commentPhase == 'arg':
                    srv.arg.addComment(comment if comment else '')
                    commentPhase = 'end'
                    comment = None
                    commentLines = []
                elif commentPhase == 'returns':
                    srv.returns.addComment(comment if comment else '')
                    commentPhase = 'end'
                    
                if line.startswith('-'):
                    comment = None
                    commentPhase = 'returns'
                    argparsing = False
                    continue

                if len(line) == 0: continue

                value_comment = ''
                tokens = line.strip().split('#')
                if len(tokens) > 1:
                    line = tokens[0]
                    value_comment = ''.join(tokens[1:]).strip()
                ms = line.strip().split()
                if len(ms) != 2:
                    raise InvalidArgument('Invalid Syntax(lineNum=%s, line="%s",ms="%s", len(line)=%d)' % (i, line, ms, len(line)))
                m = MsgMember(MsgType(ms[0]), ms[1], value_comment)
                if argparsing:
                    srv.arg.addMember(m)
                else:
                    srv.returns.addMember(m)
            except MsgException, e:
                traceback.print_exc()
                e.addInfo(i, line)
                raise e

        return srv

    def parse_str(self, name, argstr):
        p = self.__parse_name(name)

        msg = MsgObject(p[0], p[1])
        comment = None
        commentLines = []
        for i, line in enumerate(argstr.split('\n')):
            try:
                line = line.strip()
                if line.startswith('#') and comment is None:
                    commentLines.append(line[1:].strip())
                    continue
                
                if len(line) == 0: # empty line
                    if comment is None:
                        comment = '\n'.join(commentLines)
                    continue
                if comment is None:
                    comment = '\n'.join(commentLines)

                value_comment = ''
                tokens = line.strip().split('#')
                if len(tokens) > 1:
                    line = tokens[0]
                    value_comment = tokens[1].strip()
                ms = line.strip().split()
                if len(ms) != 2:
                    raise InvalidArgument('Invalid Syntax(line=%s)' % i)
                m = MsgMember(MsgType(ms[0]), ms[1], value_comment)
                msg.addMember(m)
            except MsgException, e:
                e.addInfo(i, line)
                raise e
        msg.addComment(comment if comment else '')
        return msg

