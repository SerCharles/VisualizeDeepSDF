import os 
import csv
import json
from math import *
import glob
import numpy as np
import torch
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import seaborn as sns


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

    def tsne_mean_shape(self):
        """TSNE the mean shape
        """
        tsne = TSNE(n_components=2)
        mean_codes = []
        for i in range(5):
            mask = (self.labels == i)
            selected_code = self.codes[mask]
            mean_code = np.mean(selected_code, axis=0)
            mean_codes.append(mean_code)
        mean_codes = np.stack(mean_codes, axis=0)
        kebab_codes = np.concatenate((self.codes, mean_codes), axis=0)
        result = tsne.fit_transform(kebab_codes)
        min_x = np.min(result[:, 0])
        max_x = np.max(result[:, 0])
        min_y = np.min(result[:, 1])
        max_y = np.max(result[:, 1])
        show_result_x = (result[:, 0] - min_x) / (max_x - min_x)
        show_result_y = (result[:, 1] - min_y) / (max_y - min_y)
        self.tsne_results = np.stack((show_result_x, show_result_y), axis=1)
        colors = ['red', 'blue', 'yellow', 'green', 'purple']
        for i in range(5):
            color = colors[i]
            mask = (self.labels == i)
            selected_result_x = self.tsne_results[:1000, 0][mask]
            selected_result_y = self.tsne_results[:1000, 1][mask]
            plt.scatter(selected_result_x, selected_result_y, c='black')
            mean_result_x = show_result_x[self.n + i]
            mean_result_y = show_result_y[self.n + i]
            plt.scatter(mean_result_x, mean_result_y, c=color)
        plt.show()
        plt.savefig('/home/shenguanlin/kebab.png')

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
            selected_result_x = self.tsne_results[:, 0][mask]
            selected_result_y = self.tsne_results[:, 1][mask]
            plt.scatter(selected_result_x, selected_result_y, c=color)

        plt.show()
        plt.savefig('/home/shenguanlin/test.png')
        
    
    def get_heatmap(self):
        """Get the heatmap
        """
        point_places = self.tsne_results * self.resolution
        point_weight = self.chamfer_distances
        mean_cd = np.mean(point_weight)
        point_weight = point_weight / mean_cd
        grid_x, grid_y = np.meshgrid(np.arange(0, self.resolution), np.arange(0, self.resolution))
        grid_x = (grid_x + 0.5).astype(np.float32)
        grid_y = (grid_y + 0.5).astype(np.float32)


        for i in range(5):
            #calculate the sigma in the gauss kernel
            mask = (self.labels == i)
            n = int(np.sum(mask))
            xs = point_places[:, 0][mask]
            ys = point_places[:, 1][mask]
            weights = point_weight[mask]
            iqr = np.quantile(xs, 0.75) - np.quantile(xs, 0.25)
            h = 1.06 * min(np.std(xs), iqr / 1.34) * (n ** -0.2)
            h2 = h * h

            grid_x_places = grid_x.reshape(self.resolution, self.resolution, 1).repeat(n, axis=2) 
            grid_y_places = grid_y.reshape(self.resolution, self.resolution, 1).repeat(n, axis=2) 
            x_places = xs.reshape(1, n).repeat(self.resolution ** 2, axis=0).reshape(self.resolution, self.resolution, n)
            y_places = ys.reshape(1, n).repeat(self.resolution ** 2, axis=0).reshape(self.resolution, self.resolution, n)
            grid_weight = weights.reshape(1, n).repeat(self.resolution ** 2, axis=0).reshape(self.resolution, self.resolution, n)
            dist = np.sqrt((grid_x_places - x_places) ** 2 + (grid_y_places - y_places) ** 2)
            gaussian_dist = np.exp(-(dist / h) * (dist / h) / 2) / 2.5066
            weight_gaussian_dist = gaussian_dist * grid_weight
            density = np.sum(weight_gaussian_dist, axis=2) / np.sum(weights) / h2
            max_density = np.max(density)
            density = density / max_density 
            density = density[::-1, :]
            ax = sns.heatmap(density)
            plt.show()
            plt.savefig('/home/shenguanlin/heatmap_' + str(i) + '.png')
            ax.clear()
            plt.clf()
            plt.cla()
            plt.close()

            


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
a.get_heatmap()
a.get_json_result()