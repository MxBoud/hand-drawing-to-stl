#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 23 11:44:05 2021

@author: maximeboudreau
"""
import os 
import cv2 
import matplotlib.pyplot as plt
import numpy as np

"""
SETTINGS
"""
FOLDER_NAME = "example_folder"
SCALE_FACTOR = 10 
PRINT_HEIGHT = 5 #Height in mm of the print 
DEBUG_IMVIEW = True #Show binary threshold image and detected contour for debugging

CONTOUR_LENGTH_THRESHOLD = 90

#THE OPEN_SCAD_FILEPATH NEEDS TO BE CHANGED 
OPEN_SCAD_FILEPATH = "/Volumes/Macintosh\ HD\ 1/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"

"""
"""

filesToRender = [i for i in os.listdir(FOLDER_NAME) if i.endswith(".jpg")]

for file in filesToRender:
    print("Rendering file : {}".format(file))


    """
    Performing image analysis to detect contours of the image. 
    Used this link: 
    https://www.thepythoncode.com/article/contour-detection-opencv-python
    """
    image = cv2.imread(FOLDER_NAME+"/"+file)    
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) #RGB FORMAT
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) #GRAY SCALE
    
    # create a binary thresholded image
    GRAY_THRESHOLD = np.min(gray)+50
    _, binary = cv2.threshold(gray, GRAY_THRESHOLD, 255, cv2.THRESH_BINARY_INV)
       
    
    # find the contours from the thresholded image
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    #create the image with the contours 
    image = cv2.drawContours(image, contours, -1, (0, 255, 0), 2)
    
    
    if DEBUG_IMVIEW:
        fig,ax  = plt.subplots(2,1)
        fig.set_size_inches(10,10)
        ax[0].set_title(file+" binary converted")
        ax[0].imshow(binary,cmap = "gray")
        ax[0].set_title(file+" with green contour")
        ax[1].imshow(image)
        
        plt.show()
    
    
    """Sort contours by number of points"""
    contours = sorted(contours,key = lambda x:len(x),reverse = True)
    
    """
    For each contour that has more points than the CONTOUR_LENGTH_THRESHOLD, 
    create a string corresponding to the proper openSCAD instruction to 
    generate a polygon following the contours. 
    """
    
    points = ""
    i = 0
    paths = []
    for contour in contours:
        if len(contour)>CONTOUR_LENGTH_THRESHOLD:
            contour = np.array(contour)
            contour = contour[:,0,:]
            path = []
            for pair in contour:
                points+="["+str(pair[0]/SCALE_FACTOR)+","+str(pair[1]/SCALE_FACTOR)+"]"+","
                path.append(i)
                
                i+=1
            paths.append(path)
    
    
    pathsLine = ""
    for path in paths:       
        pathsLine+="["
        for val in path:
            pathsLine+=str(val)+","
        pathsLine+="],"
    
    polygonLine = ""
    polygonLine+="polygon(points = ["+points +"], paths = [" + pathsLine+"]);"
       
    lines =[ #OPEN SCAD INSTRUCTIONS
    "linear_extrude(height = "+str(PRINT_HEIGHT)+")",
    polygonLine
    
            ]
    
    """
    Write the generated instructions in a openscad file
    """
    outName = "out.scad"
    with open(outName,'w') as f:
        for line in lines:
            f.write(line+"\n")
        
        
    """
    Invoke openscad from the command line to generate the .stl file from 
    the instructions that where generated. 
    """
    stl_FileName = file.replace(".jpg",".stl")
    os.system(OPEN_SCAD_FILEPATH +" -o "+FOLDER_NAME+"/"+stl_FileName+" out.scad")
    print("Rendering file : {} - COMPLETE".format(file))