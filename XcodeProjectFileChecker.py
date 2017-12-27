# Usage: python3 XcodeProjectFileChecker.py --help

import re
import os
import sys
import argparse

def getCommandLineArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path",
    help="the path for project root directory including ~.xcodeproj file. (default: ./)")
    default="./"
    args = parser.parse_args()
    return args

def getPathOption() -> str:
    args = getCommandLineArgs()
    hasSlash = args.path[:-1] == "/"
    path =  args.path if hasSlash else args.path + "/"
    return path

def getProjectDirectoryName(path: str) -> str:
    for file in os.listdir(path):
        base, ext = os.path.splitext(file)
        if ext == ".xcodeproj":
            fileName = base + ext
            return fileName
    print("Error: .xcodeproj file not found in " + path)
    sys.exit(1)

def getProjectFileString(projectDirectoryName: str) -> str:
    xcodeProjectFile: str = open(projectDirectoryName + "/project.pbxproj", 'r')
    projectFileString: str = xcodeProjectFile.read()
    return projectFileString

def getPBXFileReferenceSectionString(projectFileString: str) -> str:
    return getSectionString("PBXFileReference", projectFileString)

def getPBXSourcesBuildPhaseSectionString(projectFileString: str) -> str:
    return getSectionString("PBXSourcesBuildPhase", projectFileString)

def getPBXResourcesBuildPhaseSectionString(projectFileString: str) -> str:
    return getSectionString("PBXResourcesBuildPhase", projectFileString)

def getPBXBuildFileSectionString(projectFileString: str) -> str:
    return getSectionString("PBXBuildFile", projectFileString)

def getPBXNativeTargetSectionString(projectFileString: str) -> str:
    return getSectionString("PBXNativeTarget", projectFileString)

def getSectionString(sectionName: str, projectFileString: str) -> str:
    sectionString = projectFileString.split("/* Begin " + sectionName + " section */")[1]
    sectionString = sectionString.split("/* End " + sectionName + " section */")[0]
    return sectionString

def getCommentedFileNameList(projectFileString: str) -> []:
    # sample pattern: /* MyClass.swift */
    pattern = r"(/\* [0-9a-zA-Z]+\.(xib|storyboard|h|m|mm|swift|plist|json|string|png|jpeg|jpg|gif|pch).+ \*/)"
    fileList = re.findall(pattern, projectFileString)
    # print(fileList)
    fileNameList = set([])
    for file in fileList:
        fileName = file[0].strip("/* ").replace(" in Resources", "").replace(" in Sources", "")
        fileNameList.add(fileName)
    return fileNameList

def getAllFileNameList(path: str) -> []:
    fileNameList = set([])
    for root, dirs, files in os.walk(path):
        fileNameList |= set(files)
    return fileNameList

def printFileNameList(fileNameList: [], sectionName: str):
    sortedFileNameList = sorted(fileNameList)
    print("---------------------------------------------------------------")
    print("%s (%d files)" % (sectionName, len(fileNameList)))
    print("---------------------------------------------------------------")
    for fileName in sortedFileNameList:
        print(fileName)

def checkFile(refelencefileNameList: [], allFileNameList: [], targetFileNameList: []):
    # 特定ファイルを除外する場合
    # refelencefileNameList -= set(["MyClass.swift"])
    sortedRefelenceFileNameList = sorted(refelencefileNameList)
    ghostFileNameList = set([])
    nonTargetFileNameList = set([])
    print("---------------------------------------------------------------")
    print("Refelence Files (%d files)" % len(refelencefileNameList))
    print("---------------------------------------------------------------")
    for refelencefileName in sortedRefelenceFileNameList:
        if refelencefileName in allFileNameList:
            print("[ OK ] " + refelencefileName)
        else:
            print("[    ] " + refelencefileName)
            ghostFileNameList.add(refelencefileName)

        if not refelencefileName in targetFileNameList:
            nonTargetFileNameList.add(refelencefileName)

    print("---------------------------------------------------------------")
    print("Ghost Files (%d files)" % len(ghostFileNameList))
    print("---------------------------------------------------------------")
    if len(ghostFileNameList) == 0:
        print("No Files")

    for ghostFileName in ghostFileNameList:
        print(ghostFileName)

    # print(nonTargetFileNameList)
    print(refelencefileNameList - targetFileNameList)

if __name__ == "__main__":
    
    path = getPathOption()
    projectDirectoryName = getProjectDirectoryName(path)
    projectFileString = getProjectFileString(path + projectDirectoryName)
    fileRefelenceList = getCommentedFileNameList(getPBXFileReferenceSectionString(projectFileString))
    buildFileList = getCommentedFileNameList(getPBXBuildFileSectionString(projectFileString))
    sourcesBuildPhaseList = getCommentedFileNameList(getPBXSourcesBuildPhaseSectionString(projectFileString))
    resourcesBuildPhaseList = getCommentedFileNameList(getPBXResourcesBuildPhaseSectionString(projectFileString))
    allFileNameList = getAllFileNameList(path)

    printFileNameList(fileRefelenceList, "PBXFileReferenceSection")
    printFileNameList(buildFileList, "PBXBuildFileSection")
    printFileNameList(sourcesBuildPhaseList, "SourcesBuildPhaseSection")
    printFileNameList(resourcesBuildPhaseList, "ResourcesBuildPhase")

    # checkFile(fileRefelenceList, allFileNameList, buildFileList)
