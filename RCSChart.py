import math
import svgwrite

lowEThreshold = 8
highEThreshold = 200

energyBins = []

for i in range(0,11):
    logE = math.log(lowEThreshold)\
            +(i/10.0)*(math.log(highEThreshold)-math.log(lowEThreshold))
    energyBins.append(math.exp(logE))

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
    try:
        crossSectionFile = open('RCS/' + str(Z) + '-' + str(A) + '.txt')
    except IOError as e:
        print "Skipping Z=" + str(Z) + ", A=" + str(A)
        return 0

    totalFraction = 0
    CSBins = [0]*10

    for line in crossSectionFile:
        energyRange = line.split(' ')[0]
        try:
            energyRange = (float(energyRange.split('-')[0]), float(energyRange.split('-')[1]))
        except IndexError as indexError:
            print "Error: encountered index error at Z=" + str(Z) + ", A = " + str(A)
            continue
        except ValueError as valueError:
            print "Error: could not parse " + str(energyRange) + " into floats."
            continue

        # check to make sure that the lowest energy bin is not larger than the range we want to plot, and
        # that the high energy bin is not lower than the range we want to plot
        if(energyRange[0] > energyBins[-1] or energyRange[1] < energyBins[0]):
            print "At Z=" + str(Z) + ", A=" + str(A) + ", skipping line with energy range "
            print str(energyRange[0]) + "-" + str(energyRange[1])
            continue
        
        if(energyRange[0]==energyRange[1]):
            #print str(energyRange[0])
            # single data point - update the CSBins to be 1 in the appropriate energy range
            for index in range(0,len(CSBins)):
                if(energyRange[0] >= energyBins[index] and energyRange[0] <= energyBins[index+1]):
                    #print "found match in " + str(energyBins[index]) + "-" + str(energyBins[index+1])
                    CSBins[index] = 1
                    #print CSBins
        else:
            # multiple data points - update all CSBins in-between the lowest and highest energies to be 1
            #print str(energyRange[0]) + "-" + str(energyRange[1])

            for index, energyBin in enumerate(energyBins):
                if(energyRange[0] <= energyBin):
                    lowBin = index-1
                    if(lowBin<0):
                        lowBin=0
                    break

            for index, energyBin in enumerate(energyBins):
                if(energyRange[1] > energyBin):
                    highBin = index
                    if(highBin>len(CSBins)):
                        highBin=len(CSBins)

            for index in range(lowBin, highBin):
                #print "found match in " + str(energyBins[lowBin]) + "-" + str(energyBins[highBin])
                CSBins[index] = 1
                #print CSBins

    totalFraction = 0
    for CSBin in CSBins:
        totalFraction += CSBin

    if (totalFraction<0):
        print "Error: calculated total fraction <0. Returning 0 for Z=" + str(Z) + ", A=" + str(A)
        return 0

    #print str(totalFraction/10.0)
    return totalFraction/10.0

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

drawing = svgwrite.Drawing(filename='RCSChart.svg')

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
            insert=(Xposition,Yposition),
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
