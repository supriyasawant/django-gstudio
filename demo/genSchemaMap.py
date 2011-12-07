#!/usr/bin/env python
# This file reads the gstudio and objectapp models and generates the gstudio_schema.png file
# Please make sure graphviz(django-graphviz) app folder 'graphviz' is in the application.
# And the settings.py file has a GRAPHVIZ_DOT_CMD='<dot command path>'. The <dot command path>' should contain the right path to graphviz,
# Usually its GRAPHVIZ_DOT_CMD='/usr/bin/dot'. 
#                                                                                                                       
# Then run python manage.py syncdb. 

import os
import fileinput

dot_path = 'gstudio_schema.dot'
img_path = 'gstudio_schema.svg'

try:
    # generate dot file
    os.system('python manage.py modelviz objectapp gstudio auth reversion mptt >' + dot_path )
    
    # find and Replace "Node" in the file
    #dotfile = open(dot_path,'rw')

    # replacing Node to gbNode in the dotfile as it conflicts with graphvizdot notation

    os.system("sed -i 's/Node ->/gbNode ->/g' " + dot_path)
    os.system("sed -i 's/-> Node/-> gbNode/g' " + dot_path)
    os.system("sed -i 's/-> Edge/-> gbEdge/g' " + dot_path)
    os.system("sed -i 's/Edge ->/gbEdge ->/g' " + dot_path)

    '''
    for line in fileinput.input(dot_path, inplace = 1): 
        print line.replace("-> Node", "-> gbNode"),
    
    for line in fileinput.input(dot_path, inplace = 1): 
        print line.replace("Node ->", "gbNode ->"),
    '''

    #reduce graph

    os.system("tred " + dot_path + "> reduced_" + dot_path )

    # generate png
    os.system('dot reduced_'+dot_path+' -Tsvg -o '+img_path)


except(Error):
    print "Please make sure django-graphviz app folder 'graphviz' is installed, the GRAPHVIZ_DOT_CMD contains the right path to graphviz, then run syncdb."



    

