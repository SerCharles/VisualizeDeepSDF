import os 
import csv
import glob
import numpy as np
import torch



class Backend():
    """The backend of the visualization program
    """
    def __init__(self):
        """Init all the data
        """
        self.types = {'02691156':'plane', '03001627':'chair', '03636649':'lamp', '04256520':'sofa', '04379243':'table'}


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
        kebab = 0


        
a = Backend()
a.load_data()