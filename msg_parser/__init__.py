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
        self._check_typename(name)
        self._pkgName = '' if self.is_primitive else name.split('/')[0]
        self._name = name if self.is_primitive else name.split('/')[1]
    
    @property
    def is_primitive(self):
        return self._is_primitive

    @property
    def fullName(self):
        return str(self)

    @property
    def name(self):
        return self._name

    @property
    def packageName(self):
        return self._pkgName

    def _check_typename(self, n):
        if n.find('/') >= 0:
            ns = n.split('/')
            if len(ns) < 2:
                raise InvalidInnerTypeName()
            elif len(ns) > 2:
                raise InvalidInnerTypeName()
            return
        
        if n in _primitives:
#            raise InvalidPrimitiveTypeName
            self._is_primitive = True
        return

    def __str__(self):
        if self.is_primitive: return self.name
        return self.packageName + '/' + self.name


class MsgMember(object):
    
    def __init__(self, type, name, comment='', constant_value=None):
        self._type = type
        self._name = name
        self._comment = comment
        self._value = constant_value

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type

    def setType(self, t):
        self._type = t

    @property
    def comment(self):
        return self._comment

    @property
    def is_constant(self):
        return not self._value is None

    @property
    def value_str(self):
        return self._value

    @property
    def value(self):
        if not self.type.is_primitive:
            return self._value
        if self.type.fullName.find('int') >= 0:
            return int(self._value)
        elif self.type.fullName.find('float') >= 0:
            return float(self._value)
        elif self.type.fullName.find('bool') >= 0:
            return self._value == 'true' or self._value == 'True' or self._value == 'TRUE'
        elif self.type.fullName == 'string':
            return self._value
        else:
            return self._value
            
            
            
    
class ROSStruct(MsgType):

    def __init__(self, pkgName, name=None):
        self._is_primitive = False
        if name is None: # only one value passed.
            self._check_typename(pkgName)
            if self._is_primitive:
                name = pkgName
                pkgName = ''
            else:
                if len(pkgName.split('/')) == 2:
                    name = pkgName.split('/')[1]
                    pkgName = pkgName.split('/')[0]
                else:
                    name = pkgName
                    pkgName = ''
        MsgType.__init__(self, name if self._is_primitive else pkgName + '/' + name)
        # self._name = name
        # self._pkgName = pkgName
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
    def members(self):
        return self._members


class SrvObject(object):

    def __init__(self, pkgName, name):
        self._name = name
        self._pkgName = pkgName
        self._comment = ''
        self.request = ROSStruct(pkgName, name + '_request')
        self.response = ROSStruct(pkgName, name + '_response')
        
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


class ActionObject(object):

    def __init__(self, pkgName, name):
        self._name = name
        self._pkgName = pkgName
        self._comment = ''
        self.goal = ROSStruct(pkgName, name + '_goal')
        self.result = ROSStruct(pkgName, name + '_result')
        self.feedback = ROSStruct(pkgName, name + '_feedback')
        
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

    def __init__(self, ignore_header=True, ignore_goal_id=False):

        self._ignore_header = ignore_header
        self._ignore_goal_id = ignore_goal_id
        pass

    def __parse_name(self, name):
        p = name.split('/')
        if len(p) != 2:
            raise InvalidArgument('Invalid Package/Filename format(%s)' % name)
        return p
    
    def parse_action_str(self, name, argstr, typeDict={}):
        p = self.__parse_name(name)
        m = ActionObject(p[0], p[1])

        comment = None
        commentLines = []
        commentPhase = 'action'
        parsePhase = 'goal'
        for i, line in enumerate(argstr.split('\n')):
            try:
                line = line.strip()
                if line.startswith('#') and (not commentPhase.startswith('end')):
                    commentLines.append(line[1:].strip())
                    continue

                if len(commentLines) == 0 and len(line) == 0:
                    continue

                if self._ignore_header:
                    if line.startswith('Header'):
                        continue
                if self._ignore_goal_id:
                    if line.startswith('actionlib_msgs/GoalID'):
                        continue
                    
                
                if comment is None:
                    comment = '\n'.join(commentLines)
                
                if commentPhase == 'action':
                    m.addComment(comment if comment else '')
                    commentPhase = 'goal'
                    comment = None
                    commentLines = []
                elif commentPhase == 'goal':
                    m.goal.addComment(comment if comment else '')
                    commentPhase = 'end_goal'
                    comment = None
                    commentLines = []
                elif commentPhase == 'result':
                    m.result.addComment(comment if comment else '')
                    commentPhase = 'end_result'
                    comment = None
                    commentLines = []
                elif commentPhase == 'feedback':
                    m.feedback.addComment(comment if comment else '')
                    commentPhase = 'end'
                    
                if line.startswith('-'):
                    comment = None
                    if parsePhase == 'goal': parsePhase = 'result'
                    elif parsePhase == 'result': parsePhase = 'feedback'
                    if commentPhase == 'end_result' or commentPhase == 'result':
                        commentPhase = 'feedback'
                    elif commentPhase == 'goal' or commentPhase == 'end_goal':
                        commentPhase = 'result'
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
                mem = MsgMember(self.create_ros_struct(ms[0], typeDict), ms[1], value_comment)
                if parsePhase == 'goal':
                    m.goal.addMember(mem)
                elif parsePhase == 'result':
                    m.result.addMember(mem)
                elif parsePhase == 'feedback':
                    m.feedback.addMember(mem)
            except MsgException, e:
                traceback.print_exc()
                e.addInfo(i, line)
                raise e

        return m

    def parse_srv_str(self, name, argstr, typeDict={}):
        p = self.__parse_name(name)
        srv = SrvObject(p[0], p[1])

        comment = None
        commentLines = []
        commentPhase = 'srv'
        argparsing = True
        for i, line in enumerate(argstr.split('\n')):
            try:
                line = line.strip()
                if line.startswith('#') and (not commentPhase is 'end'):
                    commentLines.append(line[1:].strip())
                    continue

                if len(commentLines) == 0 and len(line) == 0:
                    continue
                
                if comment is None:
                    comment = '\n'.join(commentLines)
                
                if commentPhase == 'srv':
                    srv.addComment(comment if comment else '')
                    commentPhase = 'request'
                    comment = None
                    commentLines = []
                elif commentPhase == 'request':
                    srv.request.addComment(comment if comment else '')
                    commentPhase = 'end'
                    comment = None
                    commentLines = []
                elif commentPhase == 'response':
                    srv.response.addComment(comment if comment else '')
                    commentPhase = 'end'
                    
                if line.startswith('-'):
                    comment = None
                    commentPhase = 'response'
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
                m = MsgMember(self.create_ros_struct(ms[0], typeDict=typeDict), ms[1], value_comment)
                if argparsing:
                    srv.request.addMember(m)
                else:
                    srv.response.addMember(m)
            except MsgException, e:
                traceback.print_exc()
                e.addInfo(i, line)
                raise e

        return srv


    def parse_str(self, name, argstr, typeDict={}):
        return self.parse_msg_str(name, argstr, typeDict)

    def parse_msg_str(self, name, argstr, typeDict={}):
        # print 'parse_msg_str(', name,',ignore_header=', self._ignore_header, ')'
        p = self.__parse_name(name)

        msg = ROSStruct(p[0], p[1])
        comment = None
        commentLines = []
        for i, line in enumerate(argstr.split('\n')):
            try:
                orgLine = line
                line = line.strip()
                if line.startswith('#'):
                    if comment is None:
                        commentLines.append(line[1:].strip())
                    continue
                
                if len(commentLines) == 0 and len(line) == 0:
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
                tokens = line.strip().split('=')
                is_constant_definition = False
                constant_value = ''
                if len(tokens) > 1: # Constant Definition
                    line = tokens[0]
                    is_constant_definition = True
                    constant_value = tokens[1].strip()
                    pass
                
                ms = line.strip().split()
                if len(ms) != 2:
                    # print 'argstr:', argstr
                    raise InvalidArgument('Invalid Syntax(line=%s, linedata="%s", len(line)="%d", value_comment="%s")' % (i, orgLine, len(line), value_comment))
                if not is_constant_definition:
                    if self._ignore_header:
                        if line.startswith('Header'):
                            continue
                    if self._ignore_goal_id:
                        #print line
                        if line.startswith('actionlib_msgs/GoalID'):
                            continue
                    # print 'MsgMember creating...', ms
                    m = MsgMember(self.create_ros_struct(ms[0], typeDict, p[0]), ms[1], value_comment)
                    msg.addMember(m)
                else:
                    m = MsgMember(self.create_ros_struct(ms[0], typeDict, p[0]), ms[1], value_comment, constant_value)
                    msg.addMember(m)
            except MsgException, e:
                e.addInfo(i, line)
                raise e
        msg.addComment(comment if comment else '')
        return msg

    def create_ros_struct(self, typeName, typeDict={}, current_package=''):
        # print 'create_ros_struct(', typeName, ')'
        if typeName in _primitives:
            return ROSStruct(typeName)
        else:
            if typeName in typeDict.keys():
                return self.parse_msg_str(typeName, typeDict[typeName], typeDict)
            elif typeName == 'Header':
                typeName2 = 'std_msgs/Header'
                return self.parse_msg_str(typeName2, typeDict[typeName2], typeDict)
            else:
                typeName2 = current_package + '/' + typeName
                if typeName2 in typeDict.keys():
                    return self.parse_msg_str(typeName2, typeDict[typeName2], typeDict)
                else:
                    print 'No type (', typeName2, ') found.'
                return ROSStruct(typeName)

    def parse_type_dictionary(self, full_text):
        ft = []
        lines = full_text.split('\n')
        line_buf = []
        for line in lines:
            if line.startswith('==='):
                ft.append('\n'.join(line_buf))
                line_buf = []
            else:
                line_buf.append(line)
        ft.append('\n'.join(line_buf))
        subtypes = {}
        if len(ft) > 1:
            for f in ft[1:]:
                lines = [l for l in f.split('\n') if len(l.strip()) > 0]
                if not lines[0].startswith('MSG:'):
                    raise InvalidArgument('This member is not available to parse')
                name = lines[0][4:].strip()
                value = '\n'.join(lines[1:])
                subtypes[name] = value
        return ft[0], subtypes
        
    def parse_msg_class(self, cls):
        #print 'parse_msg_class:', cls
        clsText, typeDict = self.parse_type_dictionary(cls._full_text)
        #print 'subTypes:'
        #for key, value in typeDict.items():
        #    print key, ':', value
        return self.parse_msg_str(cls._type, clsText, typeDict)

    def parse_srv_class(self, cls):
        p = self.__parse_name(cls._type)
        srv = SrvObject(p[0], p[1])
        srv.request = self.parse_msg_class(cls._request_class)
        srv.response = self.parse_msg_class(cls._response_class)
        return srv

    def parse_action_class(self, cls):

        clsText, typeDict = self.parse_type_dictionary(cls._full_text)
        # return self.parse_action_str(cls._type, clsText, typeDict)
        return self.create_ros_struct(cls._type + 'Goal', typeDict)
