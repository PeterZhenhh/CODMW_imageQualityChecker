import struct


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
    print("Loading cache")
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
    return mtls


def main():
    MaterialCacheParh = input("Material Cache Path: ").replace("\\", "/")
    materialsInfo = MaterialCacheParser(MaterialCacheParh)
    while True:
        imgFileName = input("imgFileName to search: ")
        for mat in materialsInfo:
            for img in mat["Images"]:
                if img["Name"] == imgFileName:
                    print(img["Width"], "x", img["Height"])


main()
