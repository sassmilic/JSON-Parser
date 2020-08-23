import random
import re

ESCAPE_CHARS = ['"', "\\", "/", "b", "f", "n", "r", "t", "u"]


# refer to: https://www.json.org/json-en.html

# NOTE:
#   - asserts are internal checks for things that shouldn't happen according to the logic of the code
#   - Errors/Exceptions are raised when the json isn't valid for whatever reason

class NotAJsonFormatError(Exception):
    def __init__(self, char, i, expected_char):
        self.char = char
        self.i = i
        self.expected_char = expected_char

    def __str__(self):
        return 'Expected "{}" at index {}; got {}'.format(self.expected_char, self.i, self.char)

class JsonEscapeCharError(Exception):
    def __init__(self, char, i):
        self.char = char
        self.i = i

    def __str__(self):
        return 'Invalid escape char; "{}" at index {} cannot follow "/"'.format(self.char, self.i)

class JsonKeyError(Exception):
    def __init__(self, i):
        self.i = i

    def __str__(self):
        return 'The key starting at index {} doesn\'t have a closing quote.'.format(self.i)

class JsonUnknownType(Exception):
    def __init__(self, i):
        self.i = i

    def __str__(self):
        return 'Unknown data type at index {}.'.format(self.i)


class CharReader:
    """
    Reads a string one character at a time and keeps track of our location in the string.
    """
    class EndOfFile(Exception):
        pass
    class StartOfFile(Exception):

    def __init__(self, s):
        self.s = s
        self.i = 0

    def next(self):
        if len(self.s) == self.i:
            raise EndOfFile()
        else:
            ret = (self.i, self.s[self.i])
            self.i += 1
            return ret

    def rewind(self):
        if self.i == 0:
            raise StartOfFile()
        else:
            self.i -= 1


def parse_json(f):
    '''
    `f` is a file.
    '''
    keys = []
    values = []

    reader = CharReader(f)
    i, c = reader.next()
    
    # ignore leading whitespaces
    while re.match('\s', c):
        i, c = reader.next()
    
    # json file must start with '{'
    if c != '{':
        raise NotAJsonFormatError(c, i, '{')
   
    # ignore whitespaces
    while re.match('\s', c):
        i, c = reader.next()

    while c != '}':
        
        ## KEY ##
        # A key is always a string enclosed in quotation marks
        if c != '"':
            # TODO: change to KeyError
            raise NotAJsonFormatError(c, i, '"')
        
        key = parse_key(reader)
        keys.append(key)
    
        # ignore whitespaces
        while re.match('\s', c):
            i, c = reader.next()
       
        ## COLON ##
        if c != ':':
            raise NotAJsonFormatError(c, i, ':')        

        ## VALUE ##
        # ignore whitespaces
        while re.match('\s', c):
            i, c = reader.next()

        if c == '{':
            # object
            value = parse_object(reader)
        elif c == '[':
            # array
            value = parse_array(reader)
        elif c == '"':
            # string
            value = parse_string(reader)
        elif c in '-1234567890':
            # number
            self.rewind()
            value = parse_number(reader)
        elif c in "tfn":
            # "true", "false", "null"
            self.rewind()
            value = parse_bool_or_null(reader)
        else:
            raise JsonUnknownType(i)


def parse_key(reader):
    '''
    Precondition: the reader has already parsed the first "
        and now we are on the first inner character.
    '''
    key = ''
    _, c = reader.next()
    try:
        while c != '"':
            if c == '\\':
                # escape character
                i, c = reader.next()
                if c not in ESCAPE_CHARS:
                    raise JsonEscapeCharError(c, i)
                # TODO: check for hex digits, supported in some JSON versions
                key += "\\" + c
            else:
                key += c
            _, c = reader.next()
    except CharReader.EndOfFile:
        raise JsonKeyError()

    return key

def parse_bool_or_null(reader)
    
    def __parse(word)
        if c == "t":
            val = c
            for _ in range(len("true")):
                _, c = reader.next()
                val += c
            if val != "true":


    i, c = reader.next()

