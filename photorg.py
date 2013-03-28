#!/usr/bin/python

##--Michael duPont
##--CSC 341 Programming Languages
##--5 December 2012
##--Photorg Language
##--Main file which sends lines to parser from file or prompt

##--Usage: ./photorg.py (file-name.ptg) (debug [False]/True)
##--File call without filename and debug boolean launches user prompt
##--Filename must have the .ptg extention
##--Debug boolean turns debug on and overrides in-line changes. False by default

from parser import *
import sys

def runFileAtLine(line , debugFlag , curLine):
	retTuple = parser(line , debugFlag)
	if retTuple[0]:
		if str(retTuple[1])[:6] == "Error:":
			sys.exit("Error at line " + str(curLine) + "\n\t" + line + "\n\t" + retTuple[1])
		else:
			print retTuple[1]

def main():
	debugFlag = False	#Debugger initially off
	
	#Begin interactive user interface
	if len(sys.argv) < 2:
		print '\nPhotorg 1.0.0  Created by Michael duPont'
		print 'Type "help" to view quick language guide or "quit" to exit\n'
		cmdString = ""
		while cmdString != "quit":
			
			#Check to see of Debugger value changed
			if cmdString == "debug on":
				debugFlag = True
				print "Debugger on"
			elif cmdString == "debug off":
				debugFlag = False
				print "Debugger off"
			
			#Else, continue to parser
			else:
				if cmdString != "":
					retTuple = parser(cmdString , debugFlag)
					if retTuple[0]:
						print retTuple[1]
			cmdString = raw_input(">>> ")
		print 'Goodbye\n'
	
	
	
	#Read in from a .lang file
	elif (1 < len(sys.argv) < 4)  and (sys.argv[1].endswith(".ptg")):
		try:
			cmdDebugFlag = False
			if len(sys.argv) == 3:
				if sys.argv[2][:1].lower() == "t":
					debugFlag = True
					cmdDebugFlag = True
					print "Debug has been enabled"
			curLine = 0
			fin = open(sys.argv[1])
			for line in fin:
				curLine = curLine + 1
				line = line.strip()
				if line != "" and line != "help":
					if not cmdDebugFlag:
						if line == "debug on":
							debugFlag = True
						elif line == "debug off":
							debugFlag = False
						else:
							runFileAtLine(line , debugFlag , curLine)
					else:
						if line != "debug on" and line != "debug off":
							runFileAtLine(line , debugFlag , curLine)		
			fin.close()
		except IOError:
			sys.exit("Error: File %s was not found!" % sys.argv[1])
	else:
		sys.exit("Usage: %s (file-name.ptg) (debug [False]/True)" % sys.argv[0])

main()
