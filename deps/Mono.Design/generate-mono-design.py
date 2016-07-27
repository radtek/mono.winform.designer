#!/usr/bin/python
import os
import os.path
import re
import sys
import subprocess
import urllib.request
import urllib.error
import shutil
import string

def main ():
    try:
        print ("--> Step 1: Fetching source code...")
        files = get_files ();
        fetch_source_code (files)
        print ("--> Step 2: Applying patches...")
        #apply_patches (get_patches ())
        print ("--> Step 3: Replacing namespaces...")
        replace_namespaces (files)
        print ("Done!")
    except Exception as exc:
        print ("Unexpected Error: ")
        print (exc)

def fetch_source_code (files):
    specList=["ComponentSerializationService.cs","DefaultSerializationProviderAttribute.cs","MemberRelationship.cs","MemberRelationshipService.cs","SerializationStore.cs","DesignerOptionService.cs","IComponentInitializer.cs","ITreeDesigner.cs","INestedContainer.cs","INestedSite.cs","NestedContainer.cs"]
    specDir=("class/referencesource/System/compmod/system/componentmodel/design/serialization/",
        "class/referencesource/System/compmod/system/componentmodel/design/",
        "class/referencesource/System/compmod/system/componentmodel/")
    for file in files:
        sourceFile="/home/leo/mono/mcs/"
        directory = os.path.dirname (file)
        fileName = os.path.basename(file)
        if not fileName in specList:
            sourceFile=sourceFile+file
        else:
            if directory.rfind("Serialization") != -1:
                sourceFile = sourceFile + specDir[0] + fileName
            elif directory.rfind("Design") != -1:
                sourceFile = sourceFile + specDir[1] + fileName
            else:
                sourceFile = sourceFile + specDir[2] + fileName        
        if directory != "": # quick hack to only download assembly files and not the ones we already have
            if not os.path.exists (directory):
                os.makedirs (directory)
            if os.path.exists(file):
                continue
            for i in range (1, 4): # retry 3 times
                try:
                    if os.path.exists(sourceFile) and not os.path.exists(file):
                        shutil.copy(sourceFile,file)
                        print ("A " + file)
                        break
                except Exception as exc:
                    print ("E " + file)
                    print (exc)

# def file_to_url (file):
    # specList = ["ComponentSerializationService.cs","DefaultSerializationProviderAttribute.cs","MemberRelationship.cs","MemberRelationshipService.cs","SerializationStore.cs","DesignerOptionService.cs","IComponentInitializer.cs","ITreeDesigner.cs","INestedContainer.cs","INestedSite.cs","NestedContainer.cs"]
    # specDir = ("class/referencesource/System/compmod/system/componentmodel/design/serialization/","class/referencesource/System/compmod/system/componentmodel/design/","class/referencesource/System/compmod/system/componentmodel/")
    # directory = os.path.dirname (file)
    # fileName = os.path.basename(file)
    # sourceFile = "https://github.com/mono/mono/tree/master/mcs/"
    # if not fileName in specList:
        # sourceFile=sourceFile+file
    # else:
        # if directory.rfind("Serialization")!=-1:
            # sourceFile = sourceFile + specDir[0]+fileName
        # elif directory.rfind("Design")!=-1:
            # sourceFile = sourceFile + specDir[1]+fileName
        # else:
            # sourceFile = sourceFile +  specDir[2]+fileName   
    # return  sourceFile + "?view=co"

def get_files ():
    try:
        file = open ("Mono.Design.sources")
        filesList = []
        for fileEntry in file:
            filesList.append (fileEntry.strip ())
        file.close ()
        return filesList
    except Exception:
        print ("Unable to open file: Mono.Design.sources")
        return None

def replace_namespaces (filesList):
    if filesList == None:
        return

    regexp = re.compile (r"namespace (.*?)( ?\{?)$", re.M)
    for currentFile in filesList:
        try:
            inputFile = open (currentFile)
            input = inputFile.read ()
            inputFile.close ()
            if input.find ("namespace Mono.Design") == -1:
                output = regexp.sub (r"using \1;" + os.linesep + r"namespace Mono.Design\2", input, 1)
                outputFile = open (currentFile, "w")
                outputFile.write (output)
                outputFile.flush ()
                outputFile.close ()
        except Exception as exc:
            print (exc)

def get_patches ():
    patches = []
    patchesDir = os.path.join (os.getcwd (), "patches")
    if os.path.exists (patchesDir):
        for item in os.listdir (patchesDir):
            patchFile = os.path.join (patchesDir, item)
            if os.path.isfile (patchFile) and patchFile.endswith (".patch"):
                patches.append (patchFile)
                patches.sort ()
    return patches

def file_lf_to_clrf (fileName):
        inputFile = open (fileName, "rb")
        input = inputFile.read ()
        inputFile.close ()
        output = re.sub (bytes ("\r?\n", "utf8"), bytes ("\r\n", "utf8"), input)
        outputFile = open (fileName, "wb")
        outputFile.write (output)
        outputFile.flush ()
        outputFile.close ()

def apply_patches (patches):
    for patch in patches:
        returnCode = 0
        if os.name == "nt":
            file_lf_to_clrf (patch); # fix line endings just in case
            returnCode = subprocess.call ("patches/patch.exe -p0 -i \"" + patch + "\"")
        else:
            returnCode = subprocess.call ("patch -p0 -i \"" + patch + "\"")

        if returnCode < 0:
            print (os.path.basename (patch) + ": " + error)

if __name__ == "__main__":
        main ()