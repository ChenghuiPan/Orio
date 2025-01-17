#!/usr/bin/env python

#
# Contain syntax and grammar specifications of the BTO annotations language
#

# Example:

__example = '''
GEMVER
in
  A : matrix(column), u1 : vector(column), u2 : vector(column), 
  v1 : vector(column), v2 : vector(column),
  a : scalar, b : scalar,
  y : vector(column), z : vector(column)
out
  B : matrix(column), x : vector(column), w : vector(column)
{
  B = A + u1 * v1' + u2 * v2'
  x = b * (B' * y) + z
  w = a * (B * x)
}
'''

import sys
import orio.tool.ply.lex as plylex
#------------------------------------------------

__start_line_no = 1

#------------------------------------------------

class MLexer:
    def __init__(self, error_func, on_lbrace_func, on_rbrace_func,
                 type_lookup_func, debug=1, optimize=0, printToStderr=1):
        self.currentline = ''
        self.debug = debug
        self.optimize = optimize
        self.printToStderr = printToStderr
        self.errors = []
        #
        self.error_func = error_func
        self.on_lbrace_func = on_lbrace_func
        self.on_rbrace_func = on_rbrace_func
        self.type_lookup_func = type_lookup_func
        self.filename = ''
        pass

    
    # The ones that are actually currently in use
    reserved = ['COLUMN', 'FOR', 'IN', 'INOUT', 'MATRIX', 'FORMAT',
                'OUT', 'ROW', 'SCALAR', 'VECTOR', 'ORIENTATION',
                'GENERAL', 'TRIANGULAR', 'UPLO', 'UPPER', 'LOWER',
                'DIAG', 'UNIT', 'NONUNIT']
    
    tokens = reserved + [
    
        # literals (identifier, integer constant, float constant, string constant)
        'ID', 'ICONST', 'FCONST', 'SCONST_D', 'SCONST_S',
    
        # operators (+,-,*,/,%,||,&&,!,<,<=,>,>=,==,!=)
        'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD',
        'LOR', 'LAND', 'LNOT',
        'LT', 'LE', 'GT', 'GE', 'EQ', 'NE',
    
        # assignment (=, *=, /=, %=, +=, -=)
        'EQUALS', 'TIMESEQUAL', 'DIVEQUAL', 'MODEQUAL', 'PLUSEQUAL', 'MINUSEQUAL',
    
        # increment/decrement (++,--)
        'PLUSPLUS', 'MINUSMINUS',
        
    
        # delimeters ( ) [ ] { } , ; :
        'LPAREN', 'RPAREN',
        'LBRACKET', 'RBRACKET',
        'LBRACE', 'RBRACE',
        'COMMA', 'SEMI', 'COLON', 'PERIOD', 'SQUOTE',
        'LINECOMMENT'
        ]
    
    # Comments
    t_LINECOMMENT    = r'[\#!][^\n\r]*'
          
    
    # operators
    t_PLUS             = r'\+'
    t_MINUS            = r'-'
    t_TIMES            = r'\*'
    t_DIVIDE           = r'/'
    t_MOD              = r'%'
    t_LOR              = r'\|\|'
    t_LAND             = r'&&'
    t_LNOT             = r'!'
    t_LT               = r'<'
    t_GT               = r'>'
    t_LE               = r'<='
    t_GE               = r'>='
    t_EQ               = r'=='
    t_NE               = r'!='
    t_SQUOTE            = r'\''
    
    # assignment operators
    t_EQUALS           = r'='
    t_TIMESEQUAL       = r'\*='
    t_DIVEQUAL         = r'/='
    t_MODEQUAL         = r'%='
    t_PLUSEQUAL        = r'\+='
    t_MINUSEQUAL       = r'-='
    
    # increment/decrement
    t_PLUSPLUS         = r'\+\+'
    t_MINUSMINUS       = r'--'
    
    # delimeters
    t_LPAREN           = r'\('
    t_RPAREN           = r'\)'
    t_LBRACKET         = r'\['
    t_RBRACKET         = r'\]'
    t_LBRACE           = r'\{'
    t_RBRACE           = r'\}'
    t_COMMA            = r','
    t_SEMI             = r';'
    t_COLON            = r':'
    t_PERIOD           = r'\.'
    
    # ignored characters
    t_ignore = ' \t'
    
    # reserved words
    reserved_map = {}
    for r in reserved:
        reserved_map[r.lower()] = r

    def reset_lineno(self):
        """ Resets the internal line number counter of the lexer.
        """
        self.lexer.lineno = 1

    #==============================================================
    # Token rules
    
    # identifiersa
    def t_ID(self,t):
        r'[A-Za-z_]([_\.\w]*[_\w]+)*'
        t.type = self.reserved_map.get(t.value,'ID')
        return t
    
    # integer literal
    t_ICONST     = r'\d+'
    
    # floating literal
    t_FCONST     = r'((\d+)(\.\d*)([eE](\+|-)?(\d+))? | (\d+)[eE](\+|-)?(\d+))'
    
    # string literal (with double quotes)
    t_SCONST_D   = r'\"([^\\\n]|(\\.))*?\"'
    
    # string literal (with single quotes)
    #t_SCONST_S   = r'\'([^\\\n]|(\\.))*?\''
    
    # newlines
    def t_NEWLINE(self,t):
        r'\n+'
        t.lineno += t.value.count('\n')
               
    # syntactical error
    def t_error(self,t):
        col = self.find_column(t.lexer.lexdata,t)
        self.err("[matrixlexer] illegal character '%s' at line %s, column %s\n" % (t.value[0], t.lexer.lineno, col))
        t.lexer.skip(1)

    def find_column(self,input,token):
        i = token.lexpos
        while i > 0:
            if input[i] == '\n': 
              break
            i -= 1
        column = (token.lexpos - i) 
        return column


    def err(self, s):
        self.errors.append(s)
        if self.printToStderr:
          sys.stderr.write(s)
        
    def reset(self):
        self.lexer.lineno = 1
        
    def build(self, printToStderr=False, **kwargs):
        self.printToStderr = printToStderr
        if not kwargs.get('debug'): kwargs['debug']=self.debug
        if not kwargs.get('optimize'): kwargs['optimize']=self.optimize
        self.lexer = plylex.lex(object=self, **kwargs)
        
    def test(self, data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok: break
            print(tok)


if __name__ == "__main__":
    #lex.runmain(lexer)
    # Build the lexer and try it out
    # Build the lexer 
    l = MLexer(debug=1, optimize=0)
    l.build()
    for i in range(1, len(sys.argv)):
        print("About to lex %s" % sys.argv[i])
        f = open(sys.argv[i],"r")
        s = f.read()
        f.close()
        # print "Contents of %s: %s" % (sys.argv[i], s)
        if s == '' or s.isspace(): sys.exit(0)
        # Test the lexer; just print out all tokens founds
        l.test(s)

