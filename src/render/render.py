"""render the basic info of ScanNet, including normal and depth
"""

import numpy as np
import os
import argparse
import glob
import lib.render as render
import PIL.Image as Image
from data_loader import *


def render_one_object(data_place, save_place):
    """Render picture of the scene
        H: the height of the picture
        W: the width of the picture
        V: the number of vertexs
        F: the number of faces
        
    Args:
        data_place [string]: [the place where the model is saved]
        save_place [string]: [the place to save the picture]
    """
    vertexs, faces = load_ply(data_place)
    V = vertexs.shape[0]
    colors = np.array([0, 0, 0.9], dtype=np.float32).reshape(1, 3).repeat(V, axis=0)

    context = render.SetMesh(vertexs, faces)
    info = {'Height': 800, 'Width': 800, 'fx': 200, 'fy': 400, 'cx': 200, 'cy': 200}
    render.setup(info)
    world2cam = np.array([[sqrt(1 / 2), 0, sqrt(1 / 2), 0],
                          [0, -1, 0, 0], 
                          [sqrt(1 / 2), 0, -sqrt(1 / 2), sqrt(2)],
                          [0, 0, 0, 1]], dtype=np.float32)
    render.render(context, world2cam)
    #findices: H * W, the index of the face which is seen from the pixel
    #vindices: H * W * 3, the indices of the vertexs which is seen from the pixel, which are the 3 points of the face in findices
    #vweights: H * W * 3, the ratio of the three points in the triangle
    vindices, vweights, findices = render.getVMap(context, info) 
    H = vindices.shape[0]
    W = vindices.shape[1]
    final_color = np.zeros((H, W, 3), dtype='float32') #H * W * 3
    for k in range(3):
        indice = vindices[:, :, k]
        weight = vweights[:, :, k]
        weight = np.reshape(weight, (H, W, 1))
        weight = np.repeat(weight, 3, axis = 2)
        color_value = colors[indice]
        final_color = final_color + color_value * weight 
    final_color = (final_color * 256).astype(np.uint8)      
    picture_color = Image.fromarray(final_color)
    picture_color.save(save_place[:-4] + '.png')
    print('written', save_place)
        


    

def main():
    """The main function of basic data rendering
    """
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--data_place', default='/home/shenguanlin/dazuoye/results/Meshes/ShapeNetV2/03001627/cbc47018135fc1b1462977c6d3c24550.ply', type=str)
    parser.add_argument('--save_place', default='/home/shenguanlin/result/03001627/cbc47018135fc1b1462977c6d3c24550.ply', type=str)
    args = parser.parse_args()
    render_one_object(args.data_place, args.save_place)
    

if __name__ == "__main__":
    main()