import os
import sys
import time
import getopt

# Constants
safe = "safe"
unsafe = "unsafe"
needQuote = "needQuote"
quote = "quote"
noQuote = "noQuote"
integer = "int"
safety = "safety"
# block = "block"
# noBlock = "noBlock"
prepared = "prepared"
noPrepared = "noPrepared"
needUrlSafe = "needUrlSafe"
urlSafe = "urlSafe"
needErrorSafe = "needErrorSafe"
errorSafe = "errorSafe"


class InitialSample:  # Initialize path,comment and relevancy parameters
    # compatible with new structure
    def __init__(self, initialSample):  # XML tree in parameter
        self.path = []
        tree_path = initialSample.find("path").findall("dir")
        for dir in tree_path:
            self.path.append(dir.text)

        self.comment = initialSample.find("comment").text
        self.relevancy = float(initialSample.find("relevancy").text)

    def addSafetyAttributes(self, initialSample):
        # Classify XSS injection/sanitazition by rule of OWASP
        safeties = initialSample.find("safeties").findall("safety")
        for safety in safeties:
            if safety.get("flawType") == "XSS":
                # Rule of sanitizing needed
                self.rule = 0
                if safety.get("rule") is not None:
                    self.rule = int(safety.get("rule"))

                # Escaping simple quoted is enough ?
                self.simpleQuote = 0
                if safety.get("simpleQuote") is not None:
                    self.simpleQuote = int(safety.get("simpleQuote"))

                # Escaping double quoted is enough ?
                self.doubleQuote = 0
                if safety.get("doubleQuote") is not None:
                    self.doubleQuote = int(safety.get("doubleQuote"))

                # Unsafe function & co
                self.unsafe = 0
                if safety.get("unsafe") is not None:
                    self.unsafe = int(safety.get("unsafe"))

                # Escape of type " -> \" needed ? (TODO : improve that)
                self.escape = 0
                if safety.get("escape") is not None:
                    self.escape = int(safety.get("escape"))

                # Escape of </script> needed ?
                self.scriptBlock = 0
                if safety.get("scriptBlock") is not None:
                    self.scriptBlock = int(safety.get("scriptBlock"))

                # Escape of </style> needed ?
                self.styleBlock = 0
                if safety.get("styleBlock") is not None:
                    self.styleBlock = int(safety.get("styleBlock"))

                # Prevent data from starting with "javascript" needed ?
                self.URL_CSS_context = 0
                if safety.get("URL_CSS_context") is not None:
                    self.URL_CSS_context = int(safety.get("URL_CSS_context"))

                # Prevent data from starting with "expression" needed ?
                self.property_CSS_context = 0
                if safety.get("property_CSS_context") is not None:
                    self.property_CSS_context = int(safety.get("property_CSS_context"))


class InputSample(InitialSample):  # Initialize the type of input and the code parameters of the class
    # compatible with new structure
    def __init__(self, initialSample):  # XML tree in parameter
        InitialSample.__init__(self, initialSample)
        self.inputType = initialSample.find("inputType").text
        self.code = initialSample.find("code").text


class Sanitize(InitialSample):  # Initialize rules, safety, code and escape
    # new version for new XML
    def __init__(self, initialSample):  # XML tree in parameter
        InitialSample.__init__(self, initialSample)
        self.flaws = []
        tree_flaw = initialSample.find("flaws").findall("flaw")
        for flaw in tree_flaw:
            self.flaws.append(flaw.text)

        self.code = []
        tree_code = initialSample.find("codes").findall("code")
        for code in tree_code:
            self.code.append(code.text)

        safeties = initialSample.find("safeties").findall("safety")
        for safety in safeties:
            # print("S: " + safety.get("flawType"))
            if safety.get("flawType") == "XSS":
                # Universal safe sanitizing (Cast & co)
                self.safe = 0
                if safety.get("safe") is not None:
                    self.safe = int(safety.get("safe"))

                # Rule that can be always sanitize (/!\ Format)
                self.rule1 = 0
                self.rule2 = 0
                self.rule3 = 0
                self.rule4 = 0
                self.rule5 = 0

                if safety.get("rule1") is not None:
                    self.rule1 = int(safety.get("rule1"))
                if safety.get("rule2") is not None:
                    self.rule2 = int(safety.get("rule2"))
                if safety.get("rule3") is not None:
                    self.rule3 = int(safety.get("rule3"))
                if safety.get("rule4") is not None:
                    self.rule4 = int(safety.get("rule4"))
                if safety.get("rule5") is not None:
                    self.rule5 = int(safety.get("rule5"))
                self.addSafetyAttributes(initialSample)
            elif "Injection" in safety.get("flawType"):
                if safety.get("safe") == "1":
                    self.isSafe = safe
                elif safety.get("needQuote") == "1":
                    self.isSafe = needQuote
                elif safety.get("needQuote") == "-1":
                    self.isSafe = noQuote
                else:
                    self.isSafe = unsafe
            elif "IDOR" in safety.get("flawType"):
                self.safe = safe if safety.get("safe") == "1" else unsafe
            elif "URF" in safety.get("flawType"):
                if safety.get("urlSafe") == "1":
                    self.isSafe = urlSafe
                elif safety.get("safe") == "1":
                    self.isSafe = safe
                elif safety.get("needQuote") == "1":
                    self.isSafe = needQuote
                elif safety.get("needQuote") == "-1":
                    self.isSafe = noQuote
                else:
                    self.isSafe = unsafe
            elif "SM" in safety.get("flawType"):
                if safety.get("errorSafe") == "1":
                    self.isSafe = errorSafe
                elif safety.get("safe") == "1":
                    self.isSafe = safe
                else:
                    self.isSafe = unsafe
                #self.isSafe = safe if safety.get("safe") == "1" else unsafe
            elif "SDE" in safety.get("flawType"):
                self.isSafe = safe if safety.get("safe") == "1" else unsafe

        constraints = initialSample.find("constraints").findall("constraint")
        for constraint in constraints:
            if "Injection" in constraint.get("flawType"):
                self.constraintType = constraint.get("type")
                self.constraintField = constraint.get("field")
            if "URF" in constraint.get("flawType"):
                self.constraintType = constraint.get("type")
                self.constraintField = constraint.get("field")
                # if "IDOR" in constraint.get("flawType"):
                # self.isBlock = block if safety.find("block") == "1" else noBlock


class Construction(InitialSample):  # Load parameters and code beginning and end
    # new version for new XML
    def __init__(self, initialSample):  # Add parameters showing the beginning and the end of the sample
        InitialSample.__init__(self, initialSample)

        self.flaws = []
        tree_flaw = initialSample.find("flaws").findall("flaw")
        for flaw in tree_flaw:
            self.flaws.append(flaw.text)

        self.code = []
        tree_code = initialSample.find("codes").findall("code")
        for code in tree_code:
            self.code.append(code.text)

        safeties = initialSample.find("safeties").findall("safety")
        for safety in safeties:
            # print("F: " + safety.get("flawType"))
            if safety.get("flawType") == "XSS":
                # Universal safe sanitizing (Cast & co)
                self.safe = 0
                if safety.get("safe") is not None:
                    self.safe = int(safety.get("safe"))

                # Rule that can be always sanitize (/!\ Format)
                self.rule1 = 0
                self.rule2 = 0
                self.rule3 = 0
                self.rule4 = 0
                self.rule5 = 0

                if safety.get("rule1") is not None:
                    self.rule1 = int(safety.get("rule1"))
                if safety.get("rule2") is not None:
                    self.rule2 = int(safety.get("rule2"))
                if safety.get("rule3") is not None:
                    self.rule3 = int(safety.get("rule3"))
                if safety.get("rule4") is not None:
                    self.rule4 = int(safety.get("rule4"))
                if safety.get("rule5") is not None:
                    self.rule5 = int(safety.get("rule5"))
                self.addSafetyAttributes(initialSample)
            elif "Injection" in safety.get("flawType"):
                if safety.get("safe") == "1":
                    self.isSafe = safe
                elif safety.get("needQuote") == "1":
                    self.isSafe = needQuote
                elif safety.get("needQuote") == "-1":
                    self.isSafe = noQuote
                else:
                    self.isSafe = unsafe
            elif "IDOR" in safety.get("flawType"):
                self.safe = safe if safety.get("safe") == "1" else unsafe
            elif "URF" in safety.get("flawType"):
                if safety.get("needUrlSafe") == "1":
                    self.isSafe = needUrlSafe
                elif safety.get("safe") == "1":
                    self.isSafe = safe
                elif safety.get("needQuote") == "1":
                    self.isSafe = needQuote
                elif safety.get("needQuote") == "-1":
                    self.isSafe = noQuote
                else:
                    self.isSafe = unsafe
            elif "SM" in safety.get("flawType"):
                if safety.get("needErrorSafe") == "1":
                    self.isSafe = needErrorSafe
                elif safety.get("safe") == "1":
                    self.isSafe = safe
                else:
                    self.isSafe = unsafe
                #self.isSafe = safe if safety.get("safe") == "1" else unsafe
            elif "SDE" in safety.get("flawType"):
                self.isSafe = safe if safety.get("safe") == "1" else unsafe

        constraints = initialSample.find("constraints").findall("constraint")
        for constraint in constraints:
            if "Injection" in constraint.get("flawType"):
                self.constraintType = constraint.get("type")
                self.constraintField = constraint.get("field")
            if "IDOR" in constraint.get("flawType"):
                self.prepared = prepared if constraint.find("prepared") == "1" else noPrepared
            if "URF" in constraint.get("flawType"):
                self.constraintType = constraint.get("type")
                self.constraintField = constraint.get("field")