import os
import xml.etree.ElementTree as ET
import sys
from Classes.FileManager import *
from .Generator_Abstract_Class import *
from .InitializeSample import *
from Classes.File import *

# Constants
safe = "safe"
unsafe = "unsafe"
needQuote = "needQuote"
quote = "quote"
noQuote = "noQuote"
integer = "int"
safety = "safety"
needUrlSafe = "needUrlSafe"
urlSafe = "urlSafe"


# Manages final samples, by a combination of 3 initialSample
class GeneratorURF(Generator):
    # Initializes counters
    safe_Sample = 0
    unsafe_Sample = 0

    def getType(self):
        return ['Open_Redirect_URF']

    def __init__(self, date, manifest, select, ordered):
        Generator.__init__(self, date, manifest, select, ordered)

    def testSafety(self, flaw, sanitize):
        if flaw.isSafe == needUrlSafe:
            if sanitize.isSafe == urlSafe:
                self.safe_Sample += 1
                return 1

        else :
            if sanitize.isSafe == urlSafe:
                self.safe_Sample += 1
                return 1
            if sanitize.isSafe == safe:
                self.safe_Sample += 1
                return 1
            if flaw.isSafe == safe:
                self.safe_Sample += 1
                return 1
            if sanitize.isSafe == needQuote and flaw.isSafe == quote:
                self.safe_Sample += 1
                return 1
            # case of pg_escape_literal
            if sanitize.isSafe == noQuote and flaw.isSafe == 0:
                self.safe_Sample += 1
                return 1

        self.unsafe_Sample += 1
        return 0


    def generate(self, params):
        for param in params:
            if isinstance(param, Construction):
                for param2 in params:
                    if isinstance(param2, Sanitize):
                        for value in set(param.flaws).intersection(param2.flaws):
                            if value == "Open_Redirect_URF":
                                return self.generateWithType("Open_Redirect", params)

    # Generates final sample
    def generateWithType(self, urf, params):
        for param in params:
            if isinstance(param, InputSample):
                self.manifest.beginTestCase(param.inputType)
                break

        file = File()

        # test if the samples need to be generated
        relevancy = 1
        for param in params:
            relevancy *= param.relevancy
            if (relevancy < self.select):
                return

        # Coherence test
        for param in params:
            if (isinstance(param, Sanitize) and param.constraintType != ""):
                for param2 in params:
                    if (isinstance(param2, Construction) and (param.constraintType != param2.constraintType)):
                        return
            if (isinstance(param, Sanitize) and param.constraintField != ""):
                for param2 in params:
                    if (isinstance(param2, Construction) and (param.constraintField != param2.constraintField)):
                        return

        # retreve parameters for safety test
        safe = None
        for param in params:
            if isinstance(param, Construction):
                for param2 in params:
                    if isinstance(param2, Sanitize):
                        safe = self.testSafety(param, param2)

        flawCwe = {"Open_Redirect": "CWE_601"
        }

        # Creates folder tree and sample files if they don't exists
        file.addPath("generation_"+self.date)
        file.addPath("URF")
        file.addPath(flawCwe[urf])

        # sort by safe/unsafe
        if self.ordered:
            file.addPath("safe" if safe else "unsafe")

        for param in params:
            for dir in param.path:
                if dir != params[-1].path[-1]:
                    file.addPath(dir)
                else:
                    file.setName(flawCwe[urf] + "_" + dir)

        file.addContent("<?php\n")
        #file.addContent("/*\n")

        # Adds comments
        file.addContent("/* \n" + ("Safe sample\n" if safe else "Unsafe sample\n"))

        for param in params:
            file.addContent(param.comment + "\n")
        file.addContent("*/\n\n")

        # Gets copyright header from file
        header = open("./rights_PHP.txt", "r")
        copyright = header.readlines()
        header.close()

        # Writes copyright statement in the sample file
        file.addContent("\n\n")
        for line in copyright:
            file.addContent(line)

        # Writes the code in the sample file
        file.addContent("\n\n")
        for param in params:
            for line in param.code:
                file.addContent(line)
            file.addContent("\n\n")

        #if injection != "eval" and injection != "include_require":
        #    #Gets query execution code
        #    footer = open("./execQuery_" + injection + ".txt", "r")
        #    execQuery = footer.readlines()
        #    footer.close()

        #    #Adds the code for query execution
        #    for line in execQuery:
        #        file.addContent(line)

        file.addContent("\n\n?>")

        FileManager.createFile(file)

        flawLine = 0 if safe else self.findFlaw(file.getPath() + "/" + file.getName())

        self.manifest.addFileToTestCase(file.getPath() + "/" + file.getName(), flawLine)
        self.manifest.endTestCase()
        return file

