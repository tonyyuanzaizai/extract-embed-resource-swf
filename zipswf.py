# -*- coding: UTF-8 -*-
#!/usr/bin/python
#
# This script is inspired by jspiro's swf2lzma repo: https://github.com/jspiro/swf2lzma
#
#
# SWF Formats:
## ZWS(LZMA)
## | 4 bytes       | 4 bytes    | 4 bytes       | 5 bytes    | n bytes    | 6 bytes         |
## | 'ZWS'+version | scriptLen  | compressedLen | LZMA props | LZMA data  | LZMA end marker |
##
## scriptLen is the uncompressed length of the SWF data. Includes 4 bytes SWF header and
## 4 bytes for scriptLen itself
##
## compressedLen does not include header (4+4+4 bytes) or lzma props (5 bytes)
## compressedLen does include LZMA end marker (6 bytes)
#
import os
import pylzma
import struct
import zlib

def get_fullpath_by_extension(rootdir,extensions=None):
    '''获取路径下的所有文件 根据extensions'''
    __re=[]
    for parent,dirnames,filenames in os.walk(rootdir):
        for filename in filenames:
            fullpath=os.path.join(parent,filename)
#             if os.path.dirname(fullpath).count(".")!=0:
#                 continue
            path_extension=os.path.splitext(fullpath)[1]
            if (extensions and path_extension in extensions) or not extensions:
                result=fullpath.replace("\\","/")
                __re.append(result)
    return __re

def confirm(prompt, resp=False):
    """prompts for yes or no response from the user. Returns True for yes and
    False for no.

    'resp' should be set to the default value assumed by the caller when
    user simply types ENTER.

    >>> confirm(prompt='Create Directory?', resp=True)
    Create Directory? [y]|n:
    True
    >>> confirm(prompt='Create Directory?', resp=False)
    Create Directory? [n]|y:
    False
    >>> confirm(prompt='Create Directory?', resp=False)
    Create Directory? [n]|y: y
    True

    """

    if prompt is None:
        raise Exception('Not valid prompt')

    if resp:
        prompt = '%s %s/%s: ' % (prompt, 'Y', 'n')
    else:
        prompt = '%s %s/%s: ' % (prompt, 'N', 'y')

    while True:
        ans = raw_input(prompt)
        print("")
        if not ans:
            return resp
        if ans not in ['y', 'Y', 'n', 'N']:
            print('please enter y or n.')
            continue
        if ans == 'y' or ans == 'Y':
            return True
        if ans == 'n' or ans == 'N':
            return False

def debug(msg, level='info'):
    st='''%s : %s''' %(level, msg)
    print(st)

def check(test, msg):
    if not test :
        print(msg)

def unzip(inData):
    if inData[0] == 'C':
        # zlib SWF
        debug('zlib compressed swf detected.')
        decompressData = zlib.decompress(inData[8:])
    elif inData[0] == 'Z':
        # lzma SWF
        debug('lzma compressed swf detected.')
        decompressData = pylzma.decompress(inData[12:])
    elif inData[0] == 'F':
        # uncompressed SWF
        debug('Uncompressed swf detected.')
        decompressData = inData[8:]
    else:
        print('not a SWF file')

    sigSize = struct.unpack("<I", inData[4:8])[0]
    debug('Filesize in signature: %s' % sigSize)

    decompressSize = len(decompressData) +8
    debug('Filesize decompressed: %s' % decompressSize)

    check((sigSize == decompressSize), 'Length not correct, decompression failed')
    header = list(struct.unpack("<8B", inData[0:8]))
    header[0] = ord('F')

    debug('Generating uncompressed data')
    return struct.pack("<8B", *header)+decompressData

def zip(inData, compression):
    if(compression == 'lzma'):
        check((inData[0] != 'Z'), "already LZMA compressed")

        rawSwf = unzip(inData);

        debug('Compressing with lzma')
        compressData = pylzma.compress(rawSwf[8:], eos=1)
        # 5 accounts for lzma props

        compressSize = len(compressData) - 5

        header = list(struct.unpack("<12B", inData[0:12]))
        header[0]  = ord('Z')
        header[3]  = header[3]>=13 and header[3] or 13
        header[8]  = (compressSize)       & 0xFF
        header[9]  = (compressSize >> 8)  & 0xFF
        header[10] = (compressSize >> 16) & 0xFF
        header[11] = (compressSize >> 24) & 0xFF

        debug('Packing lzma header')
        headerBytes = struct.pack("<12B", *header);
    else:
        check((inData[0] != 'C'), "already zlib compressed")

        rawSwf = unzip(inData);

        debug('Compressing with zlib')
        compressData = zlib.compress(rawSwf[8:])

        compressSize = len(compressData)

        header = list(struct.unpack("<8B", inData[0:8]))
        header[0] = ord('C')
        header[3]  = header[3]>=6 and header[3] or 6

        debug('Packing zlib header')
        headerBytes = struct.pack("<8B", *header)

    debug('Generating compressed data')
    return headerBytes+compressData

def process(infile, outfile, operation='unzip', compression='zlib'):
    debug('Reading '+infile)
    fi = open(infile, "rb")
    infileSize = os.path.getsize(infile)
    inData = fi.read()
    fi.close()

    check((inData[1] == 'W') and (inData[2] == 'S'), "not a SWF file")


    if(operation=='unzip'):
        outData = unzip(inData)
        increment = round(100.0 * len(outData) / infileSize) - 100
        print('File decompressed, size increased: %d%%' % increment)
    else:
        compression = compression == 'lzma' and 'lzma' or 'zlib'
        outData = zip(inData, compression)
        decrement = increment = 100 - round(100.0 * len(outData) / infileSize)
        print('File compressed with %s, size decreased: %d%% %s' % (compression, decrement,
            decrement<0 and '\n\nNotice: Recompressing may cause filesize increased' or''))

    fo = open(outfile, 'wb')
    fo.write(outData)
    fo.close()

if __name__ == "__main__":
    
    li=get_fullpath_by_extension(os.getcwd(), [".swf"])
    
    for path in li:
        process(path,path,"zip","lzma")
    raw_input("Success")
