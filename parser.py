import random
import re

INTS = '0123456789'
NUMBER_PATT = '\d+\.?\d*'
WHITE_SPACE_PATT = '\s+'
OPEN_TO_CLOSE = {
    '\'': '\'',
    '\"': '\"',
    '(': ')',
    '[': ']',
    '{': '}'
}

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

class NotAJsonSyntaxError(Exception):
    def __init__(self, s, i):
        self.s = s
        self.i = i

    def __str__(self):
        return 'Expected a Python type at index {}; got {}'.format(self.i, self.s[self.i])

class NotAJsonTypeError(Exception):
    def __init__(self, s, type_):
        self.type = type_
        self.s = s

    def __str__(self):
        return '{} contains an invalid substring; this string should begin with a {}'.format(self.s, self.type)

class NotAJsonImbalanceError(Exception):
    def __init__(self, s):
        self.s = s

    def __str__(self):
        return '{} is an invalid substring; it doesn\'t have balanced opening and closing characters.'.format(self.s)

def parse_json(s):
    '''
    Parse json represented by string `s`.
    Return True if `s` represents a valid json; raise an Exception otherwise.

    >>> # white spaces shouldn't matter
    >>> s = "{\
        }"
    >>> parse_json(s)
    json is valid
    True

    >>> s = '{"response":,"answerId":530,"sender":"0x7"}'
    >>> parse_json(s)
    Traceback (most recent call last):
    NotAJsonSyntaxError: Expected a Python type at index 12; got ,

    >>> s = '{\
      "name": "John",\
      "age": 30,\
      "married": True,\
      "divorced": False,\
      "children": ("Ann","Billy"),\
      "pets": None,\
      "cars": [\
        {"model": "BMW 230", "mpg": 27.5},\
        {"model": "Ford Edge", "mpg": 24.1}\
      ]\
    }'
    >>> parse_json(s)
    json is valid
    True

    >>> # randomly remove some characters from json
    >>> # NOTE: needs manual checking, b/c sometimes passes, sometimes fails
    >>> # NOTE: remove '#doctest: +SKIP' if you wanna run this test
    >>> s = re.sub(WHITE_SPACE_PATT, '', s)
    >>> for _ in range(5):
    ...     i = random.randint(0, len(s)-1)
    ...     s = s[:i] + s[i+1:]
    >>> print('CHECK THIS TEST MANUALLY; json with chars removed:', s) #doctest: +SKIP
    >>> res = parse_json(s) #doctest: +SKIP
    '''
    # remove all white spaces
    s = re.sub(WHITE_SPACE_PATT, '', s)
    if s[0] != '{' or s[-1] != '}':
        raise NotAJsonImbalanceError(s)
    __parse_json(s, 0, len(s) - 1)
    # raises an informative exception if parsing fails
    print('json is valid')
    return True

def __parse_json(s, start, end):
    '''
    Parse json at s[start:end+1].

    Precondition: no whitespaces in s.

    >>> __parse_json('{}', 0, 1)
    True
  
    >>> s = '{"k1":1,"k2":"abc","k3":[1,2,3]}'
    >>> __parse_json(s, 0, len(s)-1)
    True

    >>> # training commas allowed
    >>> s = '{"k1":1,"k2":2,5:"b"}'
    >>> __parse_json(s, 0, len(s)-1)
    True
    
    >>> s = '{"k1":1,"k2":"abc"[}'
    >>> __parse_json(s, 0, len(s)-1)
    Traceback (most recent call last):
    NotAJsonFormatError: Expected "," at index 18; got [

    >>> s = '{"k1"1,"k2":"abc"}'
    >>> __parse_json(s, 0, len(s)-1)
    Traceback (most recent call last):
    NotAJsonFormatError: Expected ":" at index 5; got 1
    '''

    assert s[start] == '{',\
        "json doesn't begin with curly open bracket: {}".format(s)
    
    i = start + 1
    
    while i < end and s[i] != '}':
        # KEY
        # s[i] is one of: string, int, float, tuple, list, dict/json
        j = __find_matching_close(s, i)
        __parse_other(s, i, j)
        # move onto next character
        i = j + 1
        # we expect a colon to follow
        if s[i] != ':':
            raise NotAJsonFormatError(s[i], i, ':')
        # move onto next character
        i += 1
        # VALUE
        if s[i] in ':,.':
            raise NotAJsonSyntaxError(s, i)
        j = __find_matching_close(s, i)
        i = j + 1
        assert i <= end,\
            "This shouldn't happen: inner json object longer than json"
        if i == end:
            continue
        # if it's not the end of the json/dict,
        # the next char must be a comma
        if s[i] != ',':
            raise NotAJsonFormatError(s[i], i, ',')
        i += 1

    return True

def __parse_other(s, i, j):
    '''
    Parse non-json objects.

    Precondition: `j` is computed by calling `__find_matching_close`,
    which already does a lot of checks and raises the appropriate Exceptions.

    >>> __parse_other('123456', 0, 5)
    True

    >>> __parse_other('123.456', 0, 6)
    True

    >>> __parse_other('[1,2,3]', 0, 6)
    True

    >>> __parse_other('(1,2,3,)', 0, 7)
    True
    
    >>> __parse_other('123.45.6', 0, 7)
    Traceback (most recent call last):
    NotAJsonTypeError: 123.45.6 contains an invalid substring; this string should begin with a Number
    '''
    if s[i] in INTS:
        # make sure the entire substring is a number
        patt = '^' + NUMBER_PATT + '$'
        patt = re.compile(patt)
        if not patt.match(s[i: j+1]):
            raise NotAJsonTypeError(s[i: j+1], 'Number')
    elif s[i] in 'TFN':
        assert s[i:j+1] in ('True', 'False', 'None'),\
            'This shouldn\'t happen; the bool should be valid.'
        pass
    else:
        if OPEN_TO_CLOSE[s[i]] != s[j]:
            raise NotAJsonImbalanceError(s[i: j+1])

    if s[i] in '[(':
        __parse_iterable(s, i, j)
    
    if s[i] == '{':
        __parse_json(s, i, j)

    return True


def __find_matching_close(s, i):
    '''
    Return the index of the matching close bracket of s[i].

    Precondition: s[i] is one of: [, (, {, \", \' or an integer.

    Note: this is a leetcode problem ;o
    
    >>> __find_matching_close('[[[[123,456]]]]', 0)
    14
    
    >>> __find_matching_close('[[[[123,456],7,8]]]', 2)
    16

    >>> __find_matching_close('545454,asdasdas],[]]', 0)
    5
    
    >>> __find_matching_close('44.0123, 55, 5]]', 0)
    6

    >>> __find_matching_close("'asdasd", 0)
    Traceback (most recent call last):
    NotAJsonImbalanceError: 'asdasd is an invalid substring; it doesn't have balanced opening and closing characters.
    '''
    char_open = s[i]
    assert char_open in '[({\"\'' or char_open in INTS or char_open in 'TFN',\
        "This shouldn't happen: string doesn't start with expected char"

    if char_open in INTS:
        # get number starting at i
        patt = re.compile(NUMBER_PATT)
        m = patt.search(s, i)
        assert m,\
            "This shouldn't happen: number pattern doesn't match start of string"
        return m.end() - 1 # inclusive
 
    # case: bool and None
    if char_open in 'TFN':
        bools_ = ('True', 'False', 'None')
        for bl in bools_:
            if s[i:i+len(bl)] == bl:
                j = i + len(bl) - 1
                return j
        raise NotAJsonTypeError(s[i:], 'bool')

    if char_open in '\'\"':
        # open is same as close
        j = i + 1
        while j < len(s) and s[j] != char_open:
            j += 1
        if j == len(s):
            raise NotAJsonImbalanceError(s[i: j+1])
        return j

    # all other types
    nopen = 1
    j = i + 1
    while j < len(s):
        if s[j] == char_open:
            nopen += 1
        if s[j] == OPEN_TO_CLOSE[char_open]:
            nopen -= 1
        # various checks
        if nopen == 0:
            return j
        if nopen < 0:
            raise NotAJsonImbalanceError(s[i: j+1])
        j += 1

    if nopen != 0:
        raise NotAJsonImbalanceError(s[i: j+1])

    return j

def __parse_iterable(s, i, j):
    """
    Precondition: s[i] and s[j] are, respectively, one of: (),[],{}

    >>> __parse_iterable("[1,2,3,4]", 0, 8)
    True

    >>> __parse_iterable("[(1,2,3,4)]", 1, 9)
    True

    >>> __parse_iterable("[1,2,3,4]", 0, 8)
    True

    >>> __parse_iterable("[[['abc',2,[],4]]]", 2, 15)
    True

    >>> __parse_iterable("[]", 0, 1)
    True

    >>> __parse_iterable("[1,2,3 6]", 0, 8)
    Traceback (most recent call last):
    NotAJsonFormatError: Expected "," at index 6; got  
    """
    assert s[i] in '[({',\
        "This shouldn't happen: we expected the string to represent an iterable"
    assert OPEN_TO_CLOSE[s[i]] == s[j],\
        "This shouldn't happen: the substring should be properly enclosed."
    i += 1
    while i < j:
        # check element in iterable
        k = __find_matching_close(s, i)
        __parse_other(s, i, k)
        assert k < j,\
            "This shouldn't happen: objects in iterable are smaller than iterable"
        i = k + 1
        if i == j:
            continue
        # we expect a comma to follow
        if s[i] != ',':
            raise NotAJsonFormatError(s[i], i, ',')
        i += 1
    return True

if __name__ == "__main__":
    #import doctest
    #doctest.testmod()
    filename = 'oracle_db.json'
    s = open(filename).read()
    parse_json(s)
    
