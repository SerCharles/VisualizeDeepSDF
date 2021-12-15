"""The data loading and processing function used in cuda rendering 
"""

import numpy as np
import os
from plyfile import *
from math import *
import json


def load_ply(model_path):
    """Load a simple ply file with on point places and faces
        V: number of vertexs
        F: number of faces

    Args:
        model_path [string]: [the full path of the model]

    Returns:
        vertexs [numpy float array], [V * 3]: [vertexs]
        faces [numpy int array], [F * 3]: [faces]    
    """

    plydata = PlyData.read(model_path)
    my_vertexs = []
    my_faces = []

    vertexs = plydata['vertex']
    faces = plydata['face']
    for i in range(vertexs.count):
        x = float(vertexs[i][0])
        y = float(vertexs[i][1])
        z = float(vertexs[i][2])
        my_vertexs.append([x, y, z])

    for i in range(faces.count):
        a = int(faces[i][0][0])
        b = int(faces[i][0][1])
        c = int(faces[i][0][2])
        my_faces.append([a, b, c])
    
    vertexs = np.array(my_vertexs, dtype='float32')
    faces = np.array(my_faces, dtype='int32')
    return vertexs, faces


