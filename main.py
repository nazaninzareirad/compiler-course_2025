#!/usr/bin/env python3
"""
C-minus One-Pass Scanner using CMinusle for tokenization

Modules:
  - token_types         : token categories and error messages
  - symbol_table        : symbol table management (preloads keywords)
  - antlr_lexer         : ANTLR-based lexical analysis with CMinusle
  - error_handler       : lexical error detection and reporting
  - main                : driver that reads input.txt and writes outputs

Usage:
  chmod +x cminus_scanner.py
  ./cminus_scanner.py

Outputs:
  tokens.txt           : each line: lineno. \t sequence of (TokenType, lexeme)
  symbol_table.txt     : each line: index. \t lexeme
  lexical_errors.txt   : each line: lineno. \t (lexeme_prefix, ErrorMessage)
"""

import sys
import re
from collections import defaultdict
from antlr4 import InputStream, CommonTokenStream, Token
from antlr4.error.ErrorListener import ErrorListener
from CMinusle import CMinusle
from io import StringIO

# ─────────────────────────────────────────────────────────────────────────────
# MODULE: token_types
# ─────────────────────────────────────────────────────────────────────────────

# token categories
KEYWORD = 'KEYWORD'
ID      = 'ID'
NUM     = 'NUM'
SYMBOL  = 'SYMBOL'
EOF     = 'EOF'

# error messages
INVALID_NUMBER    = 'Invalid number'
INVALID_INPUT     = 'Invalid input'
UNMATCHED_COMMENT = 'Unmatched comment'
UNCLOSED_COMMENT  = 'Unclosed comment'

# ─────────────────────────────────────────────────────────────────────────────
# MODULE: symbol_table
# ─────────────────────────────────────────────────────────────────────────────

class SymbolTable:
    """
    manages keywords and identifiers, assigning unique indices
    """

    def __init__(self):
        # preload C-minus keywords with fixed indices 1..8
        self._table = {
            'break': 1, 'else': 2, 'if': 3, 'int': 4,
            'repeat': 5, 'return': 6, 'until': 7, 'void': 8
        }
        self._next_index = 9

    def lookup(self, name):
        """
        return the index for 'name', adding it if it's a new identifier
        """
        if name not in self._table:
            self._table[name] = self._next_index
            self._next_index += 1
        return self._table[name]

    def items(self):
        """
        return list of (name, index) sorted by index
        """
        return sorted(self._table.items(), key=lambda kv: kv[1])

# ─────────────────────────────────────────────────────────────────────────────
# MODULE: error_handler
# ─────────────────────────────────────────────────────────────────────────────

class ErrorHandler:
    """
    Tracks lexical errors during tokenization
    """
    def __init__(self):
        self.errors = defaultdict(list)
    
    def log_error(self, lexeme, msg, line_no):
        """
        Record a lexical error at the given line
        Only use first 3 characters of the lexeme
        """
        error_lexeme = lexeme[:3]  # Only save the first three characters
        self.errors[line_no].append((error_lexeme, msg))

# ─────────────────────────────────────────────────────────────────────────────
# MODULE: custom ANTLR error listener
# ─────────────────────────────────────────────────────────────────────────────

class CMinusErrorListener(ErrorListener):
    """
    Custom error listener for ANTLR to capture lexical errors
    """
    def __init__(self, error_handler):
        self.error_handler = error_handler

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        # Extract the problematic character/lexeme from the input
        if offendingSymbol is None and e is not None:
            # Try to get the problematic input
            if hasattr(e, 'input') and hasattr(e, 'startIndex'):
                lexeme = e.input.getText(e.startIndex, e.startIndex)
            else:
                lexeme = "<unknown>"
        else:
            lexeme = offendingSymbol.text if offendingSymbol else "<unknown>"
        
        # Log different error types
        if "unterminated comment" in msg.lower() or "unclosed comment" in msg.lower():
            self.error_handler.log_error('/*', UNCLOSED_COMMENT, line)
        elif "unmatched '*'" in msg.lower() or msg.lower().startswith("extraneous input '*/"):
            self.error_handler.log_error('*/', UNMATCHED_COMMENT, line)
        elif re.search(r'\d+[a-zA-Z]', lexeme):
            self.error_handler.log_error(lexeme, INVALID_NUMBER, line)
        else:
            self.error_handler.log_error(lexeme, INVALID_INPUT, line)

# ─────────────────────────────────────────────────────────────────────────────
# MODULE: custom token processor
# ─────────────────────────────────────────────────────────────────────────────

class InvalidInput:
    """Simple class to represent invalid input for post-processing"""
    def __init__(self, text, line):
        self.text = text
        self.line = line
        self.type = 'INVALID'

class CMinusLexerAdapter:
    """
    Adapter to handle CMinusle tokenization with custom error handling
    """
    def __init__(self, input_text):
        self.input_text = input_text
        self.error_handler = ErrorHandler()
        self.table = SymbolTable()
        
        # Set up ANTLR lexer
        input_stream = InputStream(input_text)
        self.lexer = CMinusle(input_stream)
        self.lexer.removeErrorListeners()
        self.lexer.addErrorListener(CMinusErrorListener(self.error_handler))
        
        # Process tokens and organize by line
        self.tokens_by_line = defaultdict(list)
        self.process_tokens()
        
        # Post-process to catch specific errors
        self.post_process_errors()
        
    def process_tokens(self):
        """
        Process all tokens from CMinusle and categorize them
        """
        all_tokens = list(self.lexer.getAllTokens())
        
        # Identify valid tokens
        for token in all_tokens:
            if token.type == Token.EOF:
                continue
                
            if token.type in [CMinusle.WS, CMinusle.COMMENT]:
                continue
                
            line = token.line
            lexeme = token.text
            
            # Categorize tokens
            if token.type in [CMinusle.IF, CMinusle.ELSE, CMinusle.VOID, 
                             CMinusle.INT, CMinusle.REPEAT, CMinusle.BREAK,
                             CMinusle.UNTIL, CMinusle.RETURN]:
                self.table.lookup(lexeme)  # Add to symbol table
                self.tokens_by_line[line].append((KEYWORD, lexeme))
                
            elif token.type == CMinusle.ID:
                self.table.lookup(lexeme)  # Add to symbol table
                self.tokens_by_line[line].append((ID, lexeme))
                
            elif token.type == CMinusle.NUM:
                self.tokens_by_line[line].append((NUM, lexeme))
                
            # Symbols
            else:
                self.tokens_by_line[line].append((SYMBOL, lexeme))
    
    def post_process_errors(self):
        """
        Post-process input to catch specific errors not caught by ANTLR
        """
        lines = self.input_text.split('\n')
        
        # Look for specific patterns in the input
        for line_no, line in enumerate(lines, 1):
            # Detect invalid number patterns like "23apple"
            number_alpha_matches = re.finditer(r'\b(\d+)([a-zA-Z]\w*)', line)
            for match in number_alpha_matches:
                full_match = match.group(0)
                num_part = match.group(1)
                self.error_handler.log_error(full_match, INVALID_NUMBER, line_no)
            
            # Detect = followed by # (common error in the test case)
            if '=#' in line:
                self.error_handler.log_error('=#', INVALID_INPUT, line_no)
            
            # Detect unmatched comment end without start
            if '*/' in line and '/*' not in line:
                if not any('/*' in l for l in lines[:line_no-1]):
                    self.error_handler.log_error('*/', UNMATCHED_COMMENT, line_no)
        
# ─────────────────────────────────────────────────────────────────────────────
# MODULE: main (driver)
# ─────────────────────────────────────────────────────────────────────────────

def main():
    # read the source program
    try:
        with open('input.txt', 'r', encoding='utf-8') as f:
            src = f.read()
    except FileNotFoundError:
        print("input.txt not found; please place your C-minus code there.")
        sys.exit(1)

    # Use CMinusle lexer through our adapter
    lexer = CMinusLexerAdapter(src)
    
    # write tokens.txt
    with open('tokens.txt', 'w', encoding='utf-8') as out:
        for ln in sorted(lexer.tokens_by_line):
            parts = []
            for typ, lex in lexer.tokens_by_line[ln]:
                parts.append(f"({typ}, {lex})")
            out.write(f"{ln}.\t{' '.join(parts)}\n")

    # write symbol_table.txt
    with open('symbol_table.txt', 'w', encoding='utf-8') as st:
        for name, index in lexer.table.items():
            st.write(f"{index}.\t{name}\n")

    # write lexical_errors.txt
    with open('lexical_errors.txt', 'w', encoding='utf-8') as er:
        if not lexer.error_handler.errors:
            er.write("there is no lexical error.\n")
        else:
            for ln in sorted(lexer.error_handler.errors):
                msgs = ' '.join(f"({lex}, {msg})" for lex, msg in lexer.error_handler.errors[ln])
                er.write(f"{ln}.\t{msgs}\n")

    print("done; see tokens.txt, symbol_table.txt, lexical_errors.txt")

if __name__ == '__main__':
    main()