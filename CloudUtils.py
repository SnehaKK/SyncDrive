import os, sys


MAX_BUFFER_SIZE = 1024
DEBUG = False


def LOG(logStr):
	global DEBUG
	if DEBUG:
		print logStr

#SplitFiles and save the two different files to disk
#input  : Path to the file on the disk and the number of files to be created.
#Output : Path to the newly created files.
def splitsvilla(parentFilePath, parentFileName, splitNum):
	#parentFile = open(parentFilePath, 'rb')
	global MAX_BUFFER_SIZE
	statinfo = os.stat(os.path.join(parentFilePath,parentFileName))
	fileSize = statinfo.st_size  #Obtain file size in bytes. Note: this was tested on windows. 
	listOfSplitFiles = []
	#determin the file sizes of new files.
	#Make sure there is atleast one byte in each file.
	LOG( fileSize)
	if fileSize <= 0:
		return parentFilePath
	if splitNum > fileSize :
		splitNum = fileSize
	extension = ''
	if parentFileName.find(".") != -1:
		extension = parentFileName.split('.')
		LOG( extension )
		extension = parentFileName.split('.')[1]
	sizeOfSegment = int(fileSize/splitNum)
	LOG( 'SOS : ' + str(sizeOfSegment))
	sizeOfExtraSegment = fileSize%splitNum
	if sizeOfExtraSegment > 0 : #Hack: if there is extra segment data then add 1 to the total number of segmentsself.
		sizeOfSegment += sizeOfExtraSegment # We will do this just for the first segment to accomodiate the extra segment. 
		LOG( 'SOS : ' + str(sizeOfSegment))
	fileSegmentNumber = 0
	with open(os.path.join(parentFilePath,parentFileName), 'rb') as parentFile:
		totalRead = 0
		tempFile = None
		tempFilePath = None
		if(sizeOfSegment > MAX_BUFFER_SIZE):
			tempContents = parentFile.read(MAX_BUFFER_SIZE)
			totalRead += MAX_BUFFER_SIZE
		else:
			tempContents = parentFile.read(sizeOfSegment)
			totalRead += sizeOfSegment

		while tempContents :
			if( totalRead >= sizeOfSegment):
				if(tempFile):
					totalRead = 0
					tempFile.write(tempContents)
					LOG( "written----- : " + str(sys.getsizeof(tempContents)))
					tempFile.close()
					listOfSplitFiles.append(parentFileName.split('.')[0] + '_' +str(splitNum)+'_' + str(fileSegmentNumber) + '_' + extension + '.SDPart')
					sizeOfSegment = int(fileSize/splitNum) # reset the sizeOfSegment back to original without the extra segment. Bad Hack. 
					tempFile = None
					fileSegmentNumber = fileSegmentNumber + 1
					tempFilePath = os.path.join(parentFilePath, (parentFileName.split('.')[0] + '_' +str(splitNum)+'_' + str(fileSegmentNumber) + '_' + extension + '.SDPart') )
					tempFile = open(tempFilePath,'a+b')
					if(sizeOfSegment > MAX_BUFFER_SIZE):
						tempContents = parentFile.read(MAX_BUFFER_SIZE)
						totalRead += MAX_BUFFER_SIZE
					else:
						tempContents = parentFile.read(sizeOfSegment)
						totalRead += sizeOfSegment
				else: #There is no file open
					tempFilePath = os.path.join(parentFilePath, (parentFileName.split('.')[0] + '_' +str(splitNum)+'_' + str(fileSegmentNumber) + '_' + extension+  '.SDPart') )
					tempFile = open(tempFilePath,'a+b')
					tempFile.write(tempContents)
					LOG( "written---- : " + str(sys.getsizeof(tempContents)))
					totalRead = 0
					tempFile.close()
					listOfSplitFiles.append(parentFileName.split('.')[0] + '_' +str(splitNum)+'_' + str(fileSegmentNumber) + '_' + extension + '.SDPart')
					sizeOfSegment = int(fileSize/splitNum) # reset the sizeOfSegment back to original without the extra segment. Bad Hack. 
					tempFile = None
					fileSegmentNumber = fileSegmentNumber + 1
					if(sizeOfSegment > MAX_BUFFER_SIZE):
						tempContents = parentFile.read(MAX_BUFFER_SIZE)
						totalRead += MAX_BUFFER_SIZE
					else:
						tempContents = parentFile.read(sizeOfSegment)
						totalRead += sizeOfSegment
			else:
				if tempFile is None:
					tempFilePath = os.path.join(parentFilePath, (parentFileName.split('.')[0]  + '_' + str(splitNum)+'_' + str(fileSegmentNumber) + '_' + extension + '.SDPart') )
					tempFile = open(tempFilePath,'a+b')
					tempFile.write(tempContents)
					LOG( "written : " + str(sys.getsizeof(tempContents)))
					if( (sizeOfSegment - totalRead ) > MAX_BUFFER_SIZE ) :
						tempContents = parentFile.read(MAX_BUFFER_SIZE)
						totalRead += (MAX_BUFFER_SIZE)
					else:
						tempContents = parentFile.read(sizeOfSegment-totalRead)
						totalRead += (sizeOfSegment-totalRead)
				else:
					tempFile.write(tempContents)
					LOG( "written : " + str(sys.getsizeof(tempContents)))
					if( (sizeOfSegment - totalRead ) > MAX_BUFFER_SIZE ) :
						tempContents = parentFile.read(MAX_BUFFER_SIZE)
						totalRead += (MAX_BUFFER_SIZE)
					else:
						tempContents = parentFile.read(sizeOfSegment-totalRead)
						totalRead += (sizeOfSegment-totalRead)

		if tempFile is not None:
			tempFile.close()
			statinfo = os.stat(tempFilePath)
			fileSize = statinfo.st_size
			if fileSize == 0:
				os.remove(tempFilePath)
			else:
				listOfSplitFiles.append(parentFileName.split('.')[0] + '_' +str(splitNum)+'_' + str(fileSegmentNumber) + '_' + extension + '.SDPart')

	print listOfSplitFiles
	return listOfSplitFiles


# Merge files and return the path to the new merged file. 
# Input : Path to the first or any segment of the file. For this to work the file format
# has to be filename_totalSplitNo_0_extension.SDPart  this is how splitsvilla does it. 
def marriage(firstSegmentPath):
	# When running on windows 
	if str(sys.platform).find("win32") != 1:
		firstSegmentName = firstSegmentPath.split('\\')[-1]  #The last element in the path 
	else:
		firstSegmentName = firstSegmentPath.split('/')[-1]  #The last element in the path 
	extension = firstSegmentName.split('.')[0].split('_')[-1]
	segmentFileName = firstSegmentName.split('.')[0]
	totalSplits = firstSegmentName.split('_')[-3]
	parentFileName = segmentFileName.rstrip('_' + totalSplits + '_' + segmentFileName.split('_')[-2] + '_' + extension)
	parentFilePath = firstSegmentPath.rstrip(firstSegmentName)
	parentFile = open(os.path.join(parentFilePath,parentFileName+'.'+extension),'a+b')
	LOG('firstSegmentName :' + firstSegmentName)
	LOG( 'extension :' + extension)
	LOG( 'parentFileName :' + parentFileName)
	LOG( 'totalSplits :' + totalSplits)
	LOG( 'parentFilePath :' + parentFilePath)	
	for x in range(0,int(totalSplits)):
		tempSegmentName = parentFileName + '_' + str(totalSplits) + '_' + str(x) + '_' + extension + '.SDPart'
		with open(os.path.join(parentFilePath,tempSegmentName),'rb') as tempFile:
			tempContent = tempFile.read()
			parentFile.write(tempContent)
	parentFile.close()
	return os.path.join(parentFilePath,parentFileName+'.'+extension)





if  __name__ =='__main__':
	parentFilePath = '/useruploads'
	splitNum = 4
	parentFileName = 'image.jpg'
	splitsvilla(parentFilePath,parentFileName,splitNum)
	#marriage(os.path.join(parentFilePath,'image_2_0_jpg.SDPart'))
