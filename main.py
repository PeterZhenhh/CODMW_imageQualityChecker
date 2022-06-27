import struct
from PIL import Image
import os
import csv
from operator import itemgetter
from functools import reduce
OK_MODEL = []
UNFIXED_MODEL = []
ERROR_MODEL = []
LOWRES_MODEL = []

recordPath = os.path.join(os.getcwd(), "record.csv")
def remove_list_dict_duplicate(list_dict_data):
    run_function = lambda x, y: x if y in x else x + [y]
    return reduce(run_function, [[], ] + list_dict_data)

def StrFromBytes(bar, enc="ASCII"):
    return str(bar, enc).rstrip("\0")


def readBytes(f, numBytes):
    return f.read(numBytes)


def readBool(f):
    return f.read(1)[0] != 0


def readByte(f):
    return struct.unpack("<" + "b", f.read(1))[0]


def readUByte(f):
    return struct.unpack("<" + "B", f.read(1))[0]


def readShort(f):
    return struct.unpack("<" + "h", f.read(2))[0]


def readInt16(f):
    return readShort(f)


def readUShort(f):
    return struct.unpack("<" + "H", f.read(2))[0]


def readUInt16(f):
    return readUShort(f)


def readInt(f):
    return struct.unpack("<" + "i", f.read(4))[0]


def readInt32(f):
    return readInt(f)


def readUInt(f):
    return struct.unpack("<" + "I", f.read(4))[0]


def readUInt32(f):
    return readUInt(f)


def readFloat(f):
    return struct.unpack("<" + "f", f.read(4))[0]


def readDouble(f):
    return struct.unpack("<" + "d", f.read(8))[0]


def readInt64(f):
    return struct.unpack("<" + "q", f.read(8))[0]


def readUInt64(f):
    return struct.unpack("<" + "Q", f.read(8))[0]


def readUInt24(f):
    d = f.read(3)
    if "<" == "<":
        return int(d[0]) | (int(d[1]) << 8) | (int(d[2]) << 16)
    return int(d[2]) | (int(d[1]) << 8) | (int(d[0]) << 16)


def readString(f, enc="utf8"):
    length = readUByte(f)
    if length == 128:
        f.seek(1, 1)  # 01
    data = readBytes(f, length)
    return StrFromBytes(data, enc=enc)


def readGfxMip(f):
    HashID = readUInt(f)
    readBytes(f, 24 + 4)
    Size = readInt(f)
    Width = readUShort(f)
    Height = readUShort(f)
    return {"HashID": HashID, "Size": Size, "Width": Width, "Height": Height}


def readInGameImage(f):
    name = readString(f)
    Type = readString(f)
    width = readInt(f)
    height = readInt(f)
    format = readInt32(f)
    MipMapCount = readInt32(f)
    MipMaps = []
    # readBytes(f, 160)
    MipMaps = [readGfxMip(f), readGfxMip(f), readGfxMip(f), readGfxMip(f)]
    return {
        "Name": name,
        "Type": Type,
        "Width": width,
        "Height": height,
        "Format": format,
        "MipMapCount": MipMapCount,
        "MipMaps": MipMaps,
    }


def readInGameMaterial(f):
    return {"Name": readString(f), "Images": []}


def MaterialCacheParser(cachePath):
    print("Loading cache from", cachePath)
    mtls = []
    f = open(cachePath, "rb")
    GameDirectory = readString(f)
    mtlCount = readInt32(f)
    for i in range(mtlCount):
        mtl = {"Name": readString(f), "Images": []}
        imgCount = readInt32(f)
        for j in range(imgCount):
            mtl["Images"].append(readInGameImage(f))
            # print(mtl["Images"][-1])# Display current image Info
        mtls.append(mtl)
    print("Loaded", str(len(mtls)), "materials from cache")
    return mtls


def findHighestRes(materialsInfo, matName):
    result = []
    for mat in materialsInfo:
        if mat["Name"] == matName:
            result = []
            for img in mat["Images"]:
                result.append(
                    {"imgName": img["Name"], "size": (
                        img["Width"], img["Height"])}
                )
    return result


def loadCache():
    MaterialCachePath_FilePath = os.path.join(
        os.getcwd(), "MaterialCachePath.txt")
    if not (os.path.exists(MaterialCachePath_FilePath)):
        print(MaterialCachePath_FilePath, "not found")
        return 1
    MaterialCachePath = open(MaterialCachePath_FilePath).read()
    materialsInfo = MaterialCacheParser(
        MaterialCachePath)  # Load Material Cache
    return materialsInfo


def main(materialsInfo):
    global OK_MODEL, UNFIXED_MODEL, ERROR_MODEL, LOWRES_MODEL
    xmodelsPath_FilePath = os.path.join(os.getcwd(), "xmodelsPath.txt")
    if not (os.path.exists(xmodelsPath_FilePath)):
        print(xmodelsPath_FilePath, "not found")
        return 1
    xmodelsPath = open(xmodelsPath_FilePath).read()

    # Init recordCSV
    recordCsvHeaders = [
        "IssueType",
        "xmodelName",
        "materialName",
        "materialPath",
        "ImgName",
        "HQResolution",
        "exportedResolution",
    ]
    f_csv_file = open(
        recordPath,
        "w",
        newline="",
    )
    f_csv = csv.writer(f_csv_file)
    f_csv.writerow(recordCsvHeaders)
    # Inited recordCSV

    for xmodelDir in os.listdir(xmodelsPath):
        modelStatus = 0
        # 0:normal, 1:has tex not exported, 2:has extra unknown tex, 3:has low-res tex
        texNotExported = []
        imagesPath = os.path.join(xmodelsPath, xmodelDir, "_images")
        for materialDir in os.listdir(imagesPath):
            materialPath = os.path.join(imagesPath, materialDir)
            exportedMaterial = []
            for imgFile in os.listdir(materialPath):
                imgFilePath = os.path.join(materialPath, imgFile)
                exportedImg = Image.open(imgFilePath)
                exportedMaterial.append(
                    {"imgName": os.path.splitext(
                        imgFile)[0], "size": exportedImg.size}
                )
            expectedMaterial = sorted(remove_list_dict_duplicate(findHighestRes(materialsInfo, materialDir)), key=itemgetter('imgName', 'size'))
            exportedMaterial = sorted(
                exportedMaterial, key=itemgetter('imgName', 'size'))
            if not (expectedMaterial):
                f_csv.writerow(
                    ["Mat_NotFoundInCache\t", xmodelDir, materialDir, materialPath]
                )
                print(
                    "Material cache is outdated, please use ModernModellingWarfare to update")
                print(xmodelDir, materialDir)
                os.system("pause")
                return 1
            if(exportedMaterial == expectedMaterial):
                continue  # goto check next material
            else:
                if(len(exportedMaterial) < len(expectedMaterial)):
                    if(modelStatus != 3):
                        modelStatus = 1
                elif(len(exportedMaterial) > len(expectedMaterial)):
                    if(modelStatus != 3):
                        modelStatus = 2
                if True:  # find which tex is low-res or not exported
                    for expectedImg in expectedMaterial:
                        texFound = False
                        for exportedImg in exportedMaterial:
                            if(exportedImg["imgName"] == expectedImg["imgName"]):
                                texFound = True
                                if(exportedImg["size"] != expectedImg["size"]):
                                    modelStatus = 3
                                    print(
                                        "Img_LowRes\t",
                                        xmodelDir,
                                        materialDir,
                                        expectedImg["imgName"],
                                        expectedImg["size"],
                                        exportedImg["size"]
                                    )
                                    f_csv.writerow([
                                        "Img_LowRes\t",
                                        xmodelDir,
                                        materialDir,
                                        materialPath,
                                        expectedImg["imgName"],
                                        expectedImg["size"],
                                        exportedImg["size"]]
                                    )
                        if not texFound:
                            texNotExported.append(
                                str(expectedImg["imgName"]+" "+materialPath))
                            print(
                                "Img_NotExported",
                                xmodelDir,
                                materialDir,
                                expectedImg["imgName"],
                                expectedImg["size"]
                            )
                            f_csv.writerow(
                                [
                                    "Img_NotExported",
                                    xmodelDir,
                                    materialDir,
                                    materialPath,
                                    expectedImg["imgName"],
                                    expectedImg["size"],
                                ]
                            )
        if(modelStatus == 0):
            OK_MODEL.append(xmodelDir)
        elif(modelStatus == 1):
            UNFIXED_MODEL.append([xmodelDir, texNotExported])
        elif(modelStatus == 2):
            ERROR_MODEL.append(xmodelDir)
        elif(modelStatus == 3):
            LOWRES_MODEL.append(xmodelDir)

    f_csv_file.close()
    return 0


materialsInfo = loadCache()
while True:
    OK_MODEL = []
    LOWRES_MODEL = []
    UNFIXED_MODEL = []
    ERROR_MODEL = []
    main(materialsInfo)
    if(OK_MODEL):
        print("OK "+str(len(OK_MODEL))+" - The following "+str(len(OK_MODEL))+" model textures are all Hi-res")
        for i in OK_MODEL:
            print(i)
    print()
    if(LOWRES_MODEL):
        print("LOWRES "+str(len(LOWRES_MODEL))+" - The following "+str(len(LOWRES_MODEL))+" model have low-res texture")
        for i in LOWRES_MODEL:
            print(i)
    print()
    if(UNFIXED_MODEL):
        print("CanFix "+str(len(UNFIXED_MODEL))+" - The following "+str(len(UNFIXED_MODEL))+" model need to export texture manually")
        for i in UNFIXED_MODEL:
            print(i[0])
            for j in i[1]:
                print(j)
            print()
    print()
    if(ERROR_MODEL):
        print("ERROR "+str(len(ERROR_MODEL))+" - The following "+str(len(ERROR_MODEL))+" model have textures that shouldn't exist")
        for i in ERROR_MODEL:
            print(i)

    os.system("pause")
