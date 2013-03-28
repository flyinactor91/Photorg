#!/usr/bin/python

##--Michael duPont
##--CSC 341 Programming Languages
##--5 December 2012
##--Photorg Language
##--Parser file reads in line and debug boolean and returns output tuple

##--See helpText for available commands and function comments for examples
##--Photo-specific functions support: .jpg .jpeg .png .gif .tiff

import os
import shutil
from PIL import Image
from PIL.ExifTags import TAGS

helpText = '''
Quick Photorg 1.0.0 Language Useage Guide

(...) indicates text optional
[...] indicates text required


separate [folderName] [exifName:exifValue] ([exifName:exifValue]...)
    Runs through current directory and copies photos that match all
    the given criteria into a new folder in the current directory

showexif [fileName]         Lists all exif data for a photo
listphotos                  Lists all photos in current directory
setdir [this/folderPath]    Set photo directory
getdir                      Returns current photo directory

for [varName] in [endNum/startNum..endNum] (by [skipNum]):[statement](;[statement]...)
    Structure of a for-loop
    Supports inner loops with one statement
    All other statements are considdered part of the outer loop

+ - * / ** % ( )            All basic math functions supported
[varName] = [varValue]      Assign a value to a variable
delete [varName]            Remove the variable and value
type [varName]              Check the type of a variable
// (Text)                   Comment out a line
print (Text and $var$)      Output a line to the console
println (number)            Output (number) of empty lines
debug [on/off]              Turn the debugger on or off
quit                        Exit the interactive prompt
'''

varStorage = {}
curDirLoc = ''

def parser(stringIn , debugFlag):
	command = ''
	stringIn = returnCleanStatement(stringIn)
	if debugFlag:
		print 'Debug:\tNow attempting to parse: ' + stringIn
	
	#Determine if higher-level function. Allows (for i in 10:i+1) to not count as a math function
	higherFuncFlag = False
	firstWord = stringIn[:stringIn.find(' ')]
	if firstWord == 'separate' or firstWord == 'showexif' or firstWord == 'listphotos' or firstWord == 'for' or firstWord == 'setdir' or firstWord == 'getdir' or firstWord == 'print':
		higherFuncFlag = True
		
	#Determine command to call
	if stringIn[:2] == '//':
		command = 'comment'
	elif (stringIn.find('+') != -1 or stringIn.find('-') != -1 or stringIn.find('*') != -1 or stringIn.find('/') != -1 or stringIn.find('%') != -1) and stringIn.find('=') == -1 and higherFuncFlag == False:
		command = 'math'
	elif stringIn.find('=') != -1 and higherFuncFlag == False:
		command = 'varAssign'
	else:
		commandEnd = stringIn.find(' ')
		if commandEnd == -1:
			commandEnd = len(stringIn)
		command = stringIn[:commandEnd]
	if debugFlag:
		print 'Debug:\tcommand = ' + command
	
	##--Call appropriate function--##
	
	##--Higher Level Functions--##
	if command == 'separate':
		return separatePhotos(stringIn , debugFlag)
	elif command == 'showexif':
		return showExifData(stringIn , debugFlag)
	elif command == 'listphotos':
		return listPhotos(stringIn , debugFlag)
	elif command == 'setdir':
		return setDirLoc(stringIn , debugFlag)
	elif command == 'getdir':
		if curDirLoc == '':
			return True , 'Error: No location set'
		return True , curDirLoc
	
	##--Lower Level Functions--##
	elif command == 'varAssign':
		return varAssign(stringIn , debugFlag)
	elif command == 'delete':
		return deleteVar(stringIn , debugFlag)
	elif command == 'math':
		return mathFunc(stringIn , debugFlag)
	elif command == 'for':
		return forLoopFunc(stringIn , debugFlag)
	elif command == 'type':
		return typeFunc(stringIn , debugFlag)
	elif command == 'print':
		return printFunc(stringIn , debugFlag)
	elif command == 'println':
		return println(stringIn , debugFlag)
	elif command == 'comment':
		return False , ''
	elif command == 'help':
		return True , helpText
	
	##--Private Functions--##
	elif command == '__showVarStorage':
		ret = '\n'
		for key in varStorage:
			ret += str(key) + '  -:-  ' + str(varStorage[key]) + '  -:-  ' + str(type(varStorage[key])) + '\n'
		return True , ret
	
	##--Catch Statement--##
	else:
		return True , 'Error: Not a recognized command'
	


##--Photorg Function Calls--##

##--Create new folder with pictures with appropriate metadata--##
##--Date caters to both DateTime and DateTimeOriginal--##
##--separate foldername Date:yyyy/mm/dd Make:Apple ...
def separatePhotos(stringIn , debugFlag):
	try:
		folderName = getMultiVarString(stringIn.split(' ')[1] , debugFlag)
		exifFlags = stringIn.split(' ')[2:]
		if debugFlag:
			print 'Debug:\tExif Flags: ' + str(exifFlags)
		copyDir = curDirLoc+'/'+folderName
		for fileName in os.listdir(curDirLoc):
			if fileName.endswith('.jpg') or fileName.endswith('.jpeg') or fileName.endswith('.png') or fileName.endswith('.gif') or fileName.endswith('.tiff'):
				info = get_exif(fileName)
				if info != '':
					for crit in exifFlags:
						keyName = getMultiVarString(crit.split(':')[0] , debugFlag)
						keyValue = getMultiVarString(crit.split(':')[1] , debugFlag)
						dateFlag = False
						if keyName == 'Date':
							if 'DateTimeOriginal' in info.keys():
								keyName = 'DateTimeOriginal'
							else:keyName = 'DateTime'
							keyValue = keyValue.replace('/',':')
							firstCol = keyValue.find(':')
							secondCol = keyValue[firstCol+1:].find(':') + firstCol + 1
							if len(keyValue)-secondCol == 2:keyValue = keyValue[:secondCol+1]+'0'+keyValue[secondCol+1:]
							if secondCol-firstCol == 2:keyValue = keyValue[:firstCol+1]+'0'+keyValue[firstCol+1:]
							dateFlag = True
						if keyName in info.keys():
							infoValue = str(info[keyName])
							if dateFlag:
								infoValue = infoValue.split(' ')[0]
							#print infoValue , keyValue
							if str(infoValue) == keyValue:
								#print 'match'
								if not os.path.isdir(copyDir):
									os.mkdir(copyDir)
									if debugFlag:
										print 'Debug:\tNew Folder: ' + str(folderName)
								if debugFlag:
									print 'Debug:\tValue matched: ' + str(fileName)
								shutil.copy2(curDirLoc+'/'+fileName , copyDir)
								#print 'moved file'
		return False , ''
	except OSError:
		return True , 'Error: Requires root access. Check getdir'
	except:
		return True , 'Error: Not a valid expression'

##--Make custom meta value--##
##--Currently unable to implement, PIL does not support write to exif--##
##--add filename/all custom:value

##--List all exif data of a photo
##--showexif filename
def showExifData(stringIn , debugFlag):
	try:
		info = get_exif(stringIn[9:])
		ret = '\n'
		if info != '':
			for key in info:
				ret += str(key) + ' : ' + str(info[key]) + '\n'
			return True , ret
		else:
			return True , 'Warning: Photo has no exif data'
	except IOError:
		return True , 'Error: Not a valid file'
	except:
		return True , 'Error: Not a valid expression'

##--List all photos in the current directory--##
##--listphotos
def listPhotos(stringIn , debugFlag):
	try:
		ret = '\n'
		for fileName in os.listdir(curDirLoc):
			if fileName.endswith('.jpg') or fileName.endswith('.jpeg') or fileName.endswith('.png') or fileName.endswith('.gif') or fileName.endswith('.tiff'):
				ret += fileName + '\n'
		return True , ret
	except OSError:
		return True , 'Error: Requires root access. Check getdir'
	except:
		return True , 'Error: Internal error'

##--Set image folder location--##
def setDirLoc(stringIn , debugFlag):
	try:
		global curDirLoc
		location = stringIn.split(' ')[1]
		if location == 'this':
			curDirLoc = str(os.getcwd())
			if debugFlag:
				print 'Debug:\tNew Location: ' + str(curDirLoc)
			return False , ''
		elif location[:5] == 'this+':
			extension = getMultiVarString(location[5:] , debugFlag)
			if extension[1] == '':
				extension = location[5:]
			if os.path.isdir(str(os.getcwd())+'/'+extension):
				curDirLoc = str(os.getcwd())+'/'+extension
				if debugFlag:
					print 'Debug:\tNew Location: ' + str(curDirLoc)
				return False , ''
			else:
				return True , 'Error: Not a valid path'
		elif os.path.isdir(location):
			if location[len(location)-1] == '/':
				location = location[:len(location)-1]
			curDirLoc = location
			if debugFlag:
				print 'Debug:\tNew Location: ' + str(curDirLoc)
			return False , ''
		else:
			return True , 'Error: Not a valid path'
	except:
		return True , 'Error: Not a valid expression'

##--For Loop--##
##--Supports nested for-loops but inner loops are limitted to one statement--##
##--for i in [10 , 0..10] (by 2):print i;print t;t = t + i
def forLoopFunc(stringIn , debugFlag):
	try:
		forStruct = stringIn[:stringIn.find(':')].split()
		loopLines = stringIn[stringIn.find(':')+1:].split(';')
		if debugFlag:
			print 'Debug:\tFor Sctructure: ' + str(forStruct)
			print 'Debug:\tLines to loop: ' + str(loopLines)
		if forStruct[3].find('..') != -1:
			startInt = int(getMultiVarString(forStruct[3][:forStruct[3].find('..')] , debugFlag))
			endInt = int(getMultiVarString(forStruct[3][forStruct[3].find('..')+2:] , debugFlag))+1
		else:
			startInt = 0
			endInt = int(getMultiVarString(forStruct[3] , debugFlag))
		if len(forStruct) == 6:
			byInt = int(getMultiVarString(forStruct[5] , debugFlag))
		else:
			byInt = 1
		if debugFlag:
			print 'Debug:\tStart num: ' + str(startInt)
			print 'Debug:\tEnd num: ' + str(endInt)
			print 'Debug:\tSkip num: ' + str(byInt)
		varCheck = varAssign(forStruct[1]+' = '+str(startInt) , debugFlag)
		if varCheck[0] == True:
			return True , 'Error: Not a valid expression'
		for iterValue in range(startInt,endInt,byInt):
			for command in loopLines:
				rec = parser(command , debugFlag)
				if rec[0] == True:
					if str(rec[1])[:6] == 'Error:':
						return True , 'Error: Not a valid expression'
					print rec[1]
			varStorage[forStruct[1]] = (1 * byInt) + int(varStorage[forStruct[1]])
		del varStorage[forStruct[1]]
		return False , ''
	except:
		return True , 'Error: Not a valid expression'

##--Assign value to variable and store--##
##--t = a + 5
def varAssign(stringIn , debugFlag):
	try:
		equalsLoc = stringIn.find('=')
		newVar = stringIn[:equalsLoc].strip(' ')
		if newVar[0].isdigit() and newVar[len(newVar)-1].isdigit():
			return True , 'Error: Not a valid expression'
		varValue = returnCleanStatement(stringIn[equalsLoc+1:])
		##--Check to see if math is involved--##
		if(varValue.find('+') != -1 or varValue.find('-') != -1 or varValue.find('*') != -1 or varValue.find('/') != -1 or varValue.find('%') != -1 or varValue.find('**') != -1) and varValue.find('=') == -1:
			if debugFlag:
				print 'Debug:\tFound math statement: ' + str(varValue)
			varValue = mathFunc(varValue , debugFlag)[1]
		elif varValue[0].isdigit() and varValue[len(varValue)-1].isdigit():
			if varValue.find('.') != -1:
				varValue = float(varValue)
			else:
				varValue = int(varValue)
		if len(str(varValue)) > 6 and str(varValue[:6]) == 'Error:':
			return True , 'Error: Not a valid expresion'
		if debugFlag:
			print 'Debug:\tVariable name = ' + str(newVar)
			print 'Debug:\tVariable value = ' + str(varValue)
		varStorage[newVar] = varValue
		return False , ''
	except:
		return True , 'Error: Not a valid expression'

##--Deletes a given variable if it exists--##
##--delete a
def deleteVar(stringIn , debugFlag):
	try:
		varName = stringIn[stringIn.find(' ')+1:]
		for key in varStorage:
			if key == varName:
				del varStorage[varName]
				if debugFlag:
					print 'Debug:\tVariable deleted: ' + str(varName)
				return False , ''
		return True , 'Error: Variable not found'
	except:
		return True , 'Error: Not a valid expression'

##--Math ops that accepts user vars--##
##--(5+6)**2
def mathFunc(stringIn , debugFlag):
	try:
		text = stringIn
		text = text.replace('+',' ').replace('-',' ').replace('**',' ').replace('*',' ').replace('/',' ').replace('%',' ').replace('^',' ').replace('(','').replace(')','')
		varsIn = text.split(' ')
		if debugFlag:
			print 'Debug:\tOperands: ' + str(varsIn)
		for i in range(len(varsIn)):
			if replaceVar(varsIn[i]) != '':
				if debugFlag:
					print 'Debug:\tFound varName A: ' + str(varsIn[i])
				stringIn = stringIn.replace(varsIn[i] , str(replaceVar(varsIn[i])))
		numberOut = eval(stringIn)
		return True , numberOut
	except:
		return True , 'Error: Not a valid expression'

##--Returns type of given var if it exists--##
##--type a
def typeFunc(stringIn , debugFlag):
	try:
		varName = stringIn[5:]
		varFlag = False
		varValue = replaceVar(varName)
		if varValue != '':
			if debugFlag:
				print 'Debug:\tVariable found: ' + str(varName)
				print 'Debug:\tVariable value: ' + str(varValue)
			return True , type(varValue)
		else:
			return True , 'Error: Could not find variable with name: ' + varName
	except:
		return True , 'Error: Not a valid expression'

##--Outputs var value if it exists. Else return text following call--##
##--print a=$a$ ---> b=$b$
def printFunc(stringIn , debugFlag):
	try:
		followText = stringIn[6:]
		retString = getMultiVarString(stringIn[6:] , debugFlag)
		return True , retString
	except:
		return True , 'Error: Internal error'

##--Outputs n number of empty lines--##
##--println 5
def println(stringIn , debugFlag):
	followText = getMultiVarString(stringIn[8:] , debugFlag)
	if followText.isdigit():
		if debugFlag:
			print 'Debug:\tRepeat value = ' + followText
		retString = ''
		for i in range(int(followText) - 1):
			retString = retString + '\n'
		return True , retString
	return True , ''

##--Helper Functions--##

##--Returns value of var if it exists. Else returns empty string--##
def replaceVar(varName):
	for key in varStorage:
		if key == varName:
			return varStorage[varName]
	return ''

##--Removes outside spaces for parser input--##
def returnCleanStatement(stringIn):
	leftOffset = 0
	rightOffset = len(stringIn)-1
	while stringIn[leftOffset] == ' ':
		leftOffset += 1
	while stringIn[rightOffset] == ' ':
		rightOffset -= 1
	return stringIn[leftOffset:rightOffset+1]

##--Returns string with marked variables replaced with their value--##
def getMultiVarString(stringIn , debugFlag):
	ret = ''
	varNames = stringIn.split('$')
	for var in varNames:
		varValue = replaceVar(var)
		if str(varValue) != '':
			if debugFlag:
				print 'Debug:\tVariable found: ' + str(var)
				print 'Debug:\tVariable value: ' + str(varValue)
			ret += str(varValue)
		else:
			ret += var
	return ret
		
##--Takes a fileName and returns a dictionary of decoded exif data--##
##--Thank you to litster.org for providing this code--##
def get_exif(fn):
	try:
		ret = {}
		i = Image.open(curDirLoc+'/'+fn)
		info = i._getexif()
		if info != None:
			for tag, value in info.items():
				decoded = TAGS.get(tag, tag)
				ret[decoded] = value
		else:
			ret = ''
		return ret
	except:
		return ''
