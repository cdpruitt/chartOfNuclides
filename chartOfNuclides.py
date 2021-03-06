import math
import svgwrite

lowEThreshold = 1
highEThreshold = 300

def mergeRanges(newRange, rangeList):
    if not newRange:
        return rangeList

    if not rangeList:
        return [newRange]

    if (rangeList[-1][1] >= newRange[0]):
        rangeList[-1] = (rangeList[-1][0], newRange[1])
        return rangeList

    rangeList.append(newRange)
    return rangeList

def getCSFraction(Z, A):
    crossSectionFile = open('crossSections/' + str(Z) + '-' + str(A) + '.txt')

    totalFraction = 0
    totalRange = []

    for line in crossSectionFile:
        energyRange = line.split(' ')[0]
        energyRange = (float(energyRange.split('-')[0]), float(energyRange.split('-')[1]))

#        if((Z==20) and (A==48)):

        totalRange = mergeRanges(energyRange, totalRange)

    if totalRange:
        for subRange in totalRange:
            fractionOfRange = math.log(subRange[1])-math.log(subRange[0])
            totalFraction += fractionOfRange

    totalFraction /= math.log(highEThreshold)-math.log(lowEThreshold)
    return min(totalFraction, 1)

isotopeFile = open('isotopeList.txt','r')

isotopeList = []

charge = 0

for line in isotopeFile:
    charge += 1
    line = line.strip()
    line = line.replace(',','')
    parsedLine = line.split(' ')

    del parsedLine[0]
    
    for A in parsedLine:
        isotopeList.append((charge,A))

boxSize = 50

drawing = svgwrite.Drawing(filename='chartOfNuclides_template.svg')

maxN = int(isotopeList[-1][1]) - int(isotopeList[-1][0])
maxZ = int(isotopeList[-1][0])

offsetX = 200
offsetY = 200
drawing.viewbox(width=maxN*boxSize+offsetX,height=maxZ*boxSize+offsetY)

# add magic number lines
magicNumbersZ = [8,20,28,50,82]
magicNumbersN = [8,20,28,50,82,126]

offsetZ = [5, 15, 24, 47, 113]
offsetN = [11, 24, 32, 53, 67, 90]

sizeZ = [8, 18, 30, 39, 20]
sizeN = [8, 13, 16, 29, 20, 20]

for index, magicNumber in enumerate(magicNumbersZ):
    Xposition = offsetZ[index]*boxSize
    Yposition = (maxZ-magicNumber)*boxSize

    if(magicNumber<24):
        Yposition -= 33*boxSize

    elif(magicNumber<68):
        Xposition -= 22*boxSize
        Yposition += 13*boxSize

    else:
        Xposition -= 75*boxSize
        Yposition += 68*boxSize

    magicRectangle = drawing.rect(
            insert=(Xposition, Yposition),
            size=(sizeZ[index]*boxSize, boxSize),
            stroke='black',
            stroke_width=0)
    magicRectangle.fill('rgb(190,190,190)', opacity=1)
    drawing.add(magicRectangle)

for index, magicNumber in enumerate(magicNumbersN):
    Xposition = magicNumber*boxSize
    Yposition = (maxZ-offsetN[index])*boxSize

    if(magicNumber<24):
        Yposition -= 33*boxSize

    elif(magicNumber<83):
        Xposition -= 22*boxSize
        Yposition += 13*boxSize

    else:
        Xposition -= 75*boxSize
        Yposition += 68*boxSize

    magicRectangle = drawing.rect(
            insert=(Xposition, Yposition),
            size=(boxSize,sizeN[index]*boxSize),
            stroke='black',
            stroke_width=0)
    magicRectangle.fill('rgb(190,190,190)', opacity=1)
    drawing.add(magicRectangle)

# add isotope boxes
for isotope in isotopeList:
    if(isotope[0]=='' or isotope[1]==''):
        continue

    N = int(isotope[1]) - int(isotope[0])
    Z = int(isotope[0])

    frac = getCSFraction(Z,N+Z)

    if(frac >= 0.5):
        redFrac = int(math.floor(255*(1-((frac-0.5)*2))))
        greenFrac = int(math.floor(255*(1-((frac-0.5)*2))))
        blueFrac = 255
    if(frac < 0.5):
        redFrac = 255
        greenFrac = int(math.floor(255*(frac*2)))
        blueFrac = int(math.floor(255*(frac*2)))

    colorString = 'rgb(' + str(redFrac) + ',' + str(greenFrac) + ',' + str(blueFrac) + ')'

    # draw isotope box
    Xposition = N*boxSize
    Yposition = (maxZ-Z)*boxSize

    if(Z<24):
        Yposition -= 33*boxSize

    elif(Z<68):
        Xposition -= 22*boxSize
        Yposition += 13*boxSize

    else:
        Xposition -= 75*boxSize
        Yposition += 68*boxSize

    rect = drawing.rect(
            insert=(Xposition,Yposition),
            size=(boxSize,boxSize))

    rect.fill(colorString, opacity=1)
    rect.stroke('black',width=5)

    drawing.add(rect)

drawing.save()
