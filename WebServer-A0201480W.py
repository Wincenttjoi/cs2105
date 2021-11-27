from socket import *
import sys
import math

keypathStore = {}
counterStore = {}

methodName = path = contentLength = contentBody = temp = contentFiller = b""
methodNameDone = pathDone = contentLengthDone = firstWhitespace = contentFillerDone = False

def clear():
    global methodName
    global path
    global contentBody
    global contentLength
    global contentFiller
    global temp
    global methodNameDone
    global pathDone
    global contentFillerDone
    global contentLengthDone
    global firstWhitespace

    methodName = path = contentLength = contentBody = temp = b""
    methodNameDone = pathDone = contentLengthDone = firstWhitespace = contentFillerDone = False

def successMessage():
    return b"200 OK "

def errorMessage():
    return b"404 NotFound "

def respond():
    response = process()
    clear()
    if (response):
        connection.sendall(response)

def process():
    methodnamestr = methodName.decode().lower()
    pathstr = path.decode()
    pathstrsplit = pathstr.split("/")
    prefix = pathstrsplit[1]
    keystring = pathstrsplit[2]

    isKeyPath = prefix = "key"
    isCounterPath = prefix = "counter"
    if methodnamestr == "post":
        if isKeyPath:
            keypathStore[keystring] = contentLength + b"  " + contentBody
            return successMessage() + b" "
        elif isCounterPath:
            if keystring in counterStore:
                counterStore[keystring] += 1
            else:
                counterStore[keystring] = 1
            return successMessage() + b" "
        else:
            pass
    elif methodnamestr == "get":
        if isKeyPath:
            if keystring in keypathStore:
                return successMessage() + b"content-length " + keypathStore[keystring]
            else:
                return errorMessage()
        elif isCounterPath:
            if keystring in counterStore:
                frequency = counterStore[keystring]
                digits = int(math.log10(frequency)) + 1
                return successMessage() + b"content-length " + bytes(str(digits),'utf8') + b"  " + bytes(str(frequency),'utf8')
            else:
                return successMessage() + b"content-length 1  0"
        else:
            pass
    elif methodnamestr == "delete":
        if isKeyPath:
            if keystring not in keypathStore:
                return errorMessage()
            else:
                return successMessage() + b"content-length " + keypathStore.pop(keystring)

def readNext(contentLength):
    data = connection.recv(contentLength)
    while len(data) < contentLength:
        data += connection.recv(contentLength - len(data))
    return data

def printAll():
    print("method : " + methodName.decode())
    print("path : " + path.decode())
    print("contentLength : " + contentLength.decode())
    print("contentBody : " + contentBody.decode())
    print("temp : " + temp.decode())

serverSocket = socket(AF_INET, SOCK_STREAM)

serverPort = int(sys.argv[1])

serverSocket.bind(('', serverPort))

serverSocket.listen(1)
print("Server is ready to listen")

while True:
    print("waiting for connection")
    connection, clientAddr = serverSocket.accept()

    try:
        print('connection from', clientAddr)
        while True:
            data = connection.recv(1)
            if data:
                whitespaceIndex = data.find(b" ") + 1
                if whitespaceIndex:
                    if firstWhitespace and contentLength == b"":
                        respond()
                        continue
                    else:
                        firstWhitespace = True

                    if not methodNameDone:
                        methodName = temp
                        methodNameDone = True
                    elif not pathDone:
                        path = temp
                        pathDone = True
                    elif not contentFillerDone:
                        if temp.lower() == b"content-length":
                            contentFiller = temp
                            contentFillerDone = True
                    else:
                        if temp.decode().isdigit():
                            contentLength = temp
                            first = b" "
                            while True:
                                second = readNext(1)
                                if first != b" " or second != b" ":
                                    first = second
                                else:
                                    break
                            contentBody = readNext(int(contentLength.decode()))
                            respond()
                        else:
                            contentFillerDone = False
                    temp = b""
                else:
                    firstWhitespace = False
                    temp += data
            else:
                print('no more data from', clientAddr)
                break
    finally:
        connection.close()
