from Crypto import Random
from Crypto.Cipher import AES
import hashlib
import base64
import sys,os,struct
from CloudUtils import LOG

# the block size for the cipher object; must be 16, 24, or 32 for AES
BLOCK_SIZE = 64*1024


#Getahashkey returns a 32 byte string
def getHashKey(preHashString):
	return hashlib.sha256(preHashString).digest()

def getIV():
	return Random.new().read( AES.block_size )
#Encrypt the contents of a file and delete the original file after encrypting it.
#isSplitFile is true if the file denoted by the currentFile was split using splitsvilla.
def encrypt_file(currentFile,key):
	#openfile and read data BLOCK_SIZE of data write the encrypted data a new file.
	#If isSplitFile is true The currentFile should have the following format snehaPavan_2_0_jpg.SDPart
	global BLOCK_SIZE
	statinfo = os.stat(currentFile)
	fileSize = statinfo.st_size
	if fileSize == 0:
		return -1
	iv = getIV()		
	encryptor = AES.new(key, AES.MODE_CBC, iv)		
	if str(sys.platform).find("win32") != 1:
		currentFileName = currentFile.split('\\')[-1]  #The last element in the path
	else:
		currentFileName = currentFile.split('/')[-1]  #The last element in the path 
	extension = currentFileName.split('.')[1]
	segmentFileName = currentFileName.split('.')[0]
	#totalSplits = firstSegmentName.split('_')[-3]
	currentFilePath = currentFile.rstrip(currentFileName)	
	encryptedFile = open(os.path.join(currentFilePath,segmentFileName+ '_encrypted'+'.'+extension),'a+b')	
	LOG("currentFileName")	
	#LOG(os.path.join(currentFilePath,currentBaseFileName+ '_encrypted'+'.'+extension))
	with open(currentFile, 'rb') as inFile:
		tempContents = inFile.read(BLOCK_SIZE)
		encryptedFile.write(struct.pack('<Q', fileSize))
		encryptedFile.write(iv)
		while tempContents:
			if len(tempContents) % 16 != 0:
				tempContents += ' ' * (16 - len(tempContents) % 16)
			cipherText = encryptor.encrypt(tempContents)
			encryptedFile.write(cipherText)
			tempContents = inFile.read(BLOCK_SIZE)
	encryptedFile.close()
	return segmentFileName+ '_encrypted'+'.'+extension	

#snehaPavan_2_0_jpg_encrypted.SDPart
def decrypt_file(currentFile,key):
	global BLOCK_SIZE
	statinfo = os.stat(currentFile)
	fileSize = statinfo.st_size
	if fileSize == 0:
		return -1

	if str(sys.platform).find("win32") != 1:
		currentFileName = currentFile.split('\\')[-1]  #The last element in the path 
	else:
		currentFileName = currentFile.split('/')[-1]  #The last element in the path 
	extension = currentFileName.split('.')[1]
	segmentFileName = currentFileName.split('.')[0]
	LOG("segmentFileName:"+ segmentFileName +":"+segmentFileName.rstrip('_encrypted'))
	currentFilePath = currentFile.rstrip(currentFileName)
	isEncryptedFile = segmentFileName.split('_')[-1]
	LOG(isEncryptedFile)
	if isEncryptedFile == 'encrypted' :
		decryptedFile = open(os.path.join(currentFilePath,segmentFileName.rstrip('_encrypted')+'.'+extension),'a+b')	
		#decrypt the file
		with open(currentFile,'rb') as inFile:
			origsize = struct.unpack('<Q', inFile.read(struct.calcsize('Q')))[0]
			iv = inFile.read(16)
			decryptor = AES.new(key, AES.MODE_CBC, iv)
			tempContents = inFile.read(BLOCK_SIZE)
			while tempContents:
				plainText = decryptor.decrypt(tempContents)
				decryptedFile.write(plainText)
				tempContents = inFile.read(BLOCK_SIZE)
		decryptedFile.truncate(origsize)		
		decryptedFile.close()
	return os.path.join(currentFilePath,segmentFileName.rstrip('_encrypted')+'.'+extension)

#Incase you want to run this file independently uncomment the below block.
if  __name__ =='__main__':
	encryptionkey = getHashKey('snehakulkarni')
	#decrypt_file('./file.doc',encryptionkey,True)
#	print 'EncryptionKey :' + encryptionkey
#	cipher = encrypt(encryptionkey, 'test1')
#	print  'PlainTest : test1 CipherText :' + cipher
#	print 'decrypt alog :' + decrypt(encryptionkey,cipher)		