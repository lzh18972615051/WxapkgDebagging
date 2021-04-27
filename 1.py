import sys, os
import struct

class WxapkgFile(object):
    nameLen = 0
    name = ""
    offset = 0
    size = 0

if len(sys.argv) < 2:
    print('usage: unwxapkg.py filename [output_dir]')
    exit()

with open(sys.argv[1], "rb") as f:
    root = os.path.dirname(os.path.realpath(f.name))
    name = os.path.basename(f.name) + '_dir'
    if len(sys.argv) > 2:
        name = sys.argv[2]

    #识别文件头
    firstMark = struct.unpack('B', f.read(1))[0]
    print('first header mark = {}'.format(firstMark))

    info1 = struct.unpack('>L', f.read(4))[0]
    print('info1 = {}'.format(info1))

    indexInfoLength = struct.unpack('>L', f.read(4))[0]
    print('indexInfoLength = {}'.format(indexInfoLength))

    bodyInfoLength = struct.unpack('>L', f.read(4))[0]
    print('bodyInfoLength = {}'.format(bodyInfoLength))

    lastMark = struct.unpack('B', f.read(1))[0]
    print('last header mark = {}'.format(lastMark))
    #校验文件格式
    if firstMark != 0xBE or lastMark != 0xED:
        print('这不是一个wxapkg文件！！！')
        f.close()
        exit()

    fileCount = struct.unpack('>L', f.read(4))[0]
    print('fileCount = {}'.format(fileCount))

    #读取索引
    fileList = []
    for i in range(fileCount):
        data = WxapkgFile()
        data.nameLen = struct.unpack('>L', f.read(4))[0]
        data.name = f.read(data.nameLen)
        data.offset = struct.unpack('>L', f.read(4))[0]
        data.size = struct.unpack('>L', f.read(4))[0]
        print('readFile = {} at Offset = {}'.format(str(data.name, encoding = "utf-8"), data.offset))

        fileList.append(data)

    #保存文件
    for d in fileList:
        d.name = '/' + name + str(d.name, encoding = "utf-8")
        path = root + os.path.dirname(d.name)

        if not os.path.exists(path):
            os.makedirs(path)

        w = open(root + d.name, 'wb')
        f.seek(d.offset)
        w.write(f.read(d.size))
        w.close()

        print('writeFile = {}{}'.format(root, d.name))

    f.close()
    #调用js对一次解包的代码进行优化还原
    os.system("node node/wuConfig.js "+name+"/app-config.json")
    os.system("node node/wuJs.js "+name+"/app-service.js")
    os.system("node node/wuWxml.js "+name+"/app-wxss.js")
    os.system("node node/wuWxss.js "+name)
    #考虑到微信开发者debug支持性问题，删除不需要的文件
    os.remove(name+"/app-config.json")
    os.remove(name+"/app-service.js")
    os.remove(name+"/app-wxss.js")
    os.remove(name+"/page-frame.js")
