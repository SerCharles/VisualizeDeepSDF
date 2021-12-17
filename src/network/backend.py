import os 
import csv
import json
from math import *
import glob
import numpy as np
import torch
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt


class Backend():
    """The backend of the visualization program
    """
    def __init__(self):
        """Init all the data
        """
        self.types_name = ['plane', 'chair', 'lamp', 'sofa', 'table']
        self.types_id = ['02691156', '03001627', '03636649', '04256520', '04379243']
        self.types = {'02691156':'plane', '03001627':'chair', '03636649':'lamp', '04256520':'sofa', '04379243':'table'}
        self.resolution = 200
        self.load_data()

    def load_data(self):
        """Load the code and chamfer distance
        """
        code_base_dir = '/home/shenguanlin/dazuoye/results/Codes/ShapeNetV2'
        cd_dir = '/home/shenguanlin/dazuoye/evaluation/chamfer.csv'
        self.codes = []
        self.chamfer_distances = []
        self.names = []
        self.labels = []
        name_index_map = {}
        i = 0
        #load the code
        for type in self.types.keys():
            code_base_dir_type = os.path.join(code_base_dir, type)
            names = sorted(glob.glob(os.path.join(code_base_dir_type, '*.pth')))
            for name in names:
                image_name = name.split(os.sep)[-1][:-4]
                code = torch.load(name).detach().cpu().numpy().reshape(1, 256)
                label = i 
                self.codes.append(code)
                self.names.append(image_name)
                self.labels.append(label)
                self.chamfer_distances.append(0.0)
                name_index_map[image_name] = len(self.names) - 1
            i += 1
        self.codes = np.concatenate(self.codes, axis=0)
        self.labels = np.array(self.labels, dtype=np.int32)
        self.n = len(self.names)
        
        #load the cd 
        with open(cd_dir, 'r', encoding="utf-8-sig") as csvfile:
            data_reader = csv.reader(csvfile)
            for row in data_reader:
                i = data_reader.line_num - 1
                if i == 0:
                    continue
                name = row[0]
                cd = float(row[1])
                real_name = name.split('/')[-1]
                index = name_index_map[real_name]
                self.chamfer_distances[index] = cd 
        self.chamfer_distances = np.array(self.chamfer_distances)

    def tsne(self):
        """TSNE process of the data
        """
        tsne = TSNE(n_components=2)
        result = tsne.fit_transform(self.codes)
        min_x = np.min(result[:, 0])
        max_x = np.max(result[:, 0])
        min_y = np.min(result[:, 1])
        max_y = np.max(result[:, 1])
        show_result_x = (result[:, 0] - min_x) / (max_x - min_x)
        show_result_y = (result[:, 1] - min_y) / (max_y - min_y)
        self.tsne_results = np.stack((show_result_x, show_result_y), axis=1)
        
        #test
        
        colors = ['red', 'blue', 'yellow', 'green', 'purple']
        for i in range(5):
            color = colors[i]
            mask = (self.labels == i)
            indice = np.arange(0, self.n)
            selected_result_x = self.tsne_results[:, 0][mask]
            selected_result_y = self.tsne_results[:, 1][mask]
            plt.scatter(selected_result_x, selected_result_y, c=color)

        plt.show()
        plt.savefig('/home/shenguanlin/test.png')
        
    



    def get_json_result(self):
        """Get the json result
        """
        result = {}
        data = []
        for i in range(self.n):
            the_data = {}
            the_data['id'] = i
            the_data['name'] = self.names[i]
            the_data['class'] = self.types_name[self.labels[i]]
            the_data['tsneX'] = float(self.tsne_results[i, 0])
            the_data['tsneY'] = float(self.tsne_results[i, 1])
            type_id = self.types_id[self.labels[i]]
            the_data['img'] = os.path.join('picture', 'pred', type_id, self.names[i] + '.png')
            the_data['img_gt'] = os.path.join('picture', 'gt', type_id, self.names[i] + '.png')
            data.append(the_data)
        result['data'] = data
        json_result = json.dumps(result)
        with open('/home/shenguanlin/result.json', 'w') as f:
            f.write(json_result)

a = Backend()
a.tsne()
a.get_json_result()
