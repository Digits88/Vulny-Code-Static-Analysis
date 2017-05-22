#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import re
from indicators import *

# Display the found vulnerability with basic informations like the line
def display(path,payload,vulnerability,line,declaration_text,declaration_line):

	# Potential vulnerability found :  SQL Injection
	header = "\033[1mPotential vulnerability found : \033[92m{}\033[0m".format(payload[1])

	# Line  25  in test/sqli.php
	line = "n°\033[92m{}\033[0m in {}".format(line,path)

	# Code : include($_GET['patisserie'])
	vuln = vulnerability[0]+"\033[93m"+vulnerability[1]+"\033[0m"+vulnerability[2]
	vuln = "{}({})".format(payload[0], vuln)

	# Declared at line 1 : $dest = $_GET['who'];
	declared = ""
	if not "$_" in vulnerability[1]:
		if declaration_text != "":
			declared = "Line n°\033[0;92m"+declaration_line+"\033[0m : "+ declaration_text
		else:
			declared = "Undeclared \033[0m"+ declaration_text+" in the file"

	# Final Display
	rows, columns = os.popen('stty size', 'r').read().split()
	print "-" * (int(columns)-1)
	print "Name        " + "\t"+header
	print "-" * (int(columns)-1)
	print "\033[1mLine \033[0m        " + "\t"+line
	print "\033[1mCode \033[0m        " + "\t"+vuln
	print "\033[1mDeclaration \033[0m " + "\t"+declared+"\n"


# Find the line where the vulnerability is located
def find_line_vuln(path,payload,vulnerability,content):
	content = content.split('\n')
	for i in range(len(content)):
		if payload[0]+'('+vulnerability[0]+vulnerability[1]+vulnerability[2]+')' in content[i]:
			return str(i)
	return "-1"


# Find the line where the entry point is declared
# TODO: should be an array of the declaration and modifications
def find_line_declaration(declaration, content):
	content = content.split('\n')
	for i in range(len(content)):
		if declaration in content[i]:
			return str(i)
	return "-1"


# Format the source code in order to improve the detection
def clean_source_and_format(content):
    # Clean up - replace tab by space
    content = content.replace("	"," ")

    # Quickfix to detect both echo("something") and echo "something"
    content = content.replace("echo ","echo(")
    content = content.replace(";",");")
    return content

# Check the line to detect an eventual protection
def check_protection(payload, match):
    for protection in payload:
        if protection in "".join(match):
            return True
    return False

# Check exception - When it's a function($SOMETHING) Match declaration $SOMETHING = ...
def check_exception(match):
    exceptions = ["_GET","_REQUEST","_POST","_COOKIES","_FILES"]
    is_exception = False
    for exception in exceptions:
        if exception in match:
            return True
    return False

# Check declaration
# TODO: should follow any include and add its content
# TODO: should handle constant variable
def check_declaration(content, vuln):
    # Parse include and content = include_content + content
    regex_declaration = re.compile("\$"+vuln[1:]+"([\t ]*)=(?!=)(.*)")
    declaration       = regex_declaration.findall(content)
    if len(declaration)>0:
        declaration_text = "$"+vuln[1:] +declaration[0][0]+"="+declaration[0][1]
        line_declaration = find_line_declaration(declaration_text, content)
        return (declaration_text,line_declaration)
    return ("","")