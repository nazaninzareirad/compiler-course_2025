# C-Minus Compiler - Phase 1: Lexical Analysis

This repository contains the first phase of a C-Minus compiler implementation, focusing on lexical analysis (scanning). It was developed as part of a compiler design course project.

## Table of Contents
1. [Overview](#overview)
2. [C-Minus Language](#c-minus-language)
3. [Implementation Details](#implementation-details)
4. [Components](#components)
5. [Output Files](#output-files)
6. [How to Use](#how-to-use)
7. [Error Handling](#error-handling)
8. [Limitations](#limitations)
9. [Next Steps](#next-steps)
10. [Contributors](#contributors)

## Overview
This compiler phase performs lexical analysis (scanning) of C-Minus source code, which includes:
- Tokenizing the input program
- Building a symbol table
- Detecting and reporting lexical errors
- Generating output files for the next compilation phases

## C-Minus Language
C-Minus is a simplified subset of C with the following lexical elements:

**Keywords**: `if`, `else`, `void`, `int`, `repeat`, `break`, `until`, `return`

**Identifiers**:
- Start with a letter (a-z, A-Z)
- Can contain letters and digits (0-9)

**Numbers**: Integer literals (one or more digits)

**Symbols**: `;` `,` `[` `]` `(` `)` `{` `}` `+` `-` `*` `<` `=` `==`

**Comments**: Multi-line between `/*` and `*/`

## Implementation Details
The scanner is implemented using:
1. **ANTLR4** for tokenization (lexical analysis)
2. A **Symbol Table** to track identifiers and keywords
3. An **Error Handler** to detect and report lexical errors
4. A **Driver Program** that coordinates the scanning process

The implementation follows a one-pass design where the input is processed once to:
1. Identify tokens
2. Record symbols
3. Detect errors

## Components

### 1. ANTLR Lexer Grammar (`CMinusle.g4`)
Defines the lexical rules for the C-Minus language, including:
- Token patterns for keywords, identifiers, numbers, and symbols
- Rules for skipping whitespace and comments

### 2. Symbol Table
- Pre-loaded with C-Minus keywords (indices 1-8)
- Dynamically adds identifiers with subsequent indices
- Provides fast lookup and insertion

### 3. Error Handler
Detects and records:
- Invalid numbers (e.g., "123abc")
- Invalid symbols (e.g., "#", "=#")
- Unmatched or unclosed comments
- Other malformed input

### 4. Main Driver (`cminus_scanner.py`)
Coordinates the entire scanning process:
1. Reads input from `input.txt`
2. Processes tokens through the lexer adapter
3. Generates output files

## Output Files
The compiler produces three output files:

**tokens.txt**  
Format: `[line number]. (TYPE, lexeme) (TYPE, lexeme)...`  
Example: `3. (KEYWORD, if) (SYMBOL, () (ID, x) (SYMBOL, ))`

**symbol_table.txt**  
Format: `[index]. [lexeme]`  
Example: break, else, x

**lexical_errors.txt**  
Format: `[line number]. (lexeme, error_message)`  
Example: `5. (23a, Invalid number)`  
If no errors: `there is no lexical error.`

## How to Use
1. Place your C-Minus source code in `input.txt`
2. Run the scanner:
```bash
chmod +x cminus_scanner.py
./cminus_scanner.py
Check the output files:

tokens.txt - Tokenized program

symbol_table.txt - All identifiers

lexical_errors.txt - Any lexical errors

Error Handling
The scanner detects and reports:

Invalid numbers: Numbers containing letters (e.g., "123abc")

Invalid symbols: Unrecognized symbols (e.g., "@", "#")

Comment errors:

Unclosed comments (missing */)

Unmatched comment closers (*/ without /*)

General invalid input: Any text that doesn't match language rules

Errors are reported with:

The line number where they occurred

The first 3 characters of the invalid lexeme

A descriptive error message

Limitations
This phase has some intentional limitations:

Only performs lexical analysis (no parsing/semantic analysis)

Numbers must be integers (no floating point)

Error messages show truncated lexemes (first 3 characters)

The symbol table doesn't track scope (will be added in later phases)

Next Steps
This is Phase 1 of the compiler. Future phases will add:

Syntax analysis (parsing)

Semantic analysis

Code generation

Contributors
[Taha Hosseinpour] (https://github.com/ThomasGraceman)
[Nazanin Zarei] (https://github.com/nazaninzareirad)
[Foozhan Fahimzade] (https://github.com/FoozhanFahimzade)
