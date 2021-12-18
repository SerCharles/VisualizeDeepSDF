import os 
import csv
import random
import json
from math import *
import glob
import numpy as np
from scipy.spatial.distance import cdist
import torch
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns
from lapjv import lapjv


class Backend():
    """The backend of the visualization program
    """
    def __init__(self):
        """Init all the data
        """
        np.random.seed(1453)
        self.types_name = ['plane', 'chair', 'lamp', 'sofa', 'table']
        self.types_id = ['02691156', '03001627', '03636649', '04256520', '04379243']
        self.types = {'02691156':'plane', '03001627':'chair', '03636649':'lamp', '04256520':'sofa', '04379243':'table'}
        self.resolution = 200
        self.grid_size = 40
        self.load_data()

    def load_data(self):
        """Load the code and chamfer distance
        """
        self.code_base_dir = '/home/shenguanlin/dazuoye/results/Codes/ShapeNetV2'
        self.cd_dir = '/home/shenguanlin/dazuoye/evaluation/chamfer.csv'
        self.codes = []
        self.chamfer_distances = []
        self.names = []
        self.labels = []
        name_index_map = {}
        i = 0
        #load the code
        for type in self.types.keys():
            code_base_dir_type = os.path.join(self.code_base_dir, type)
            names = sorted(glob.glob(os.path.join(code_base_dir_type, '*.pth')))
            for name in names:
                image_name = name.split(os.sep)[-1][:-4]
                code = torch.load(name, map_location=torch.device('cpu')).detach().cpu().numpy().reshape(1, 256)
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
        with open(self.cd_dir, 'r', encoding="utf-8-sig") as csvfile:
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


    def pca(self):
        """PCA process of the data
        """
        pca = PCA(n_components=2)
        result = pca.fit_transform(self.codes)
        min_x = np.min(result[:, 0])
        max_x = np.max(result[:, 0])
        min_y = np.min(result[:, 1])
        max_y = np.max(result[:, 1])
        show_result_x = (result[:, 0] - min_x) / (max_x - min_x)
        show_result_y = (result[:, 1] - min_y) / (max_y - min_y)
        self.pca_results = np.stack((show_result_x, show_result_y), axis=1)

        #test
        colors = ['red', 'blue', 'yellow', 'green', 'purple']
        for i in range(5):
            color = colors[i]
            mask = (self.labels == i)
            selected_result_x = self.pca_results[:, 0][mask]
            selected_result_y = self.pca_results[:, 1][mask]
            plt.scatter(selected_result_x, selected_result_y, c=color)

        plt.show()
        plt.savefig('/home/shenguanlin/results/pca.png')
        plt.clf()
        plt.cla()
        plt.close()

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
        plt.savefig('/home/shenguanlin/results/tsne.png')
        plt.clf()
        plt.cla()
        plt.close()

    def get_grid(self):
        """Get the grid information
        """
        grid = np.dstack(np.meshgrid(np.linspace(0, 1, self.grid_size), np.linspace(0, 1, self.grid_size))).reshape(-1, 2)
        dummy_instances = np.random.random((self.grid_size ** 2 - self.n, 2)).astype(np.float32)
        full_places = np.concatenate((self.tsne_results, dummy_instances), axis=0) #1600 * 2
        cost = cdist(full_places, grid, "sqeuclidean").astype(np.float32)
        cost *= 100000 / cost.max()
        row_index, col_index, _ = lapjv(cost, verbose=True, force_doubles=True)
        grid_index_y = (row_index // 40)[:self.n]
        grid_index_x = (row_index % 40)[:self.n]
        self.grid_index = np.stack((grid_index_x, grid_index_y), axis=1)
        self.grid_item_id = col_index

        show_index = self.grid_index + 0.5
        colors = ['red', 'blue', 'yellow', 'green', 'purple']
        for i in range(5):
            color = colors[i]
            mask = (self.labels == i)
            selected_result_x = show_index[:, 0][mask]
            selected_result_y = show_index[:, 1][mask]
            plt.scatter(selected_result_x, selected_result_y, c=color)
        plt.show()
        plt.savefig('/home/shenguanlin/results/grid.png')
        plt.clf()
        plt.cla()
        plt.close()

    def get_heatmap_tsne(self):
        """Get the heatmap based on tsne data
        """
        point_places = self.tsne_results * self.resolution
        grid_x, grid_y = np.meshgrid(np.arange(0, self.resolution), np.arange(0, self.resolution))
        grid_x = (grid_x + 0.5).astype(np.float32)
        grid_y = (grid_y + 0.5).astype(np.float32)

        self.tsne_densitys = []
        for i in range(5):
            #calculate the sigma in the gauss kernel
            mask = (self.labels == i)
            n = int(np.sum(mask))
            xs = point_places[:, 0][mask]
            ys = point_places[:, 1][mask]
            iqr = np.quantile(xs, 0.75) - np.quantile(xs, 0.25)
            h = 1.06 * min(np.std(xs), iqr / 1.34) * (n ** -0.2)
            h2 = h * h

            grid_x_places = grid_x.reshape(self.resolution, self.resolution, 1).repeat(n, axis=2) 
            grid_y_places = grid_y.reshape(self.resolution, self.resolution, 1).repeat(n, axis=2) 
            x_places = xs.reshape(1, n).repeat(self.resolution ** 2, axis=0).reshape(self.resolution, self.resolution, n)
            y_places = ys.reshape(1, n).repeat(self.resolution ** 2, axis=0).reshape(self.resolution, self.resolution, n)
            dist = np.sqrt((grid_x_places - x_places) ** 2 + (grid_y_places - y_places) ** 2)
            gaussian_dist = np.exp(-(dist / h) * (dist / h) / 2) / 2.5066
            density = np.sum(gaussian_dist, axis=2) / n / h2
            max_density = np.max(density)
            density = density / max_density 
            self.tsne_densitys.append(density)
            
            #test
            show_density = density[::-1, :]
            ax = sns.heatmap(show_density)
            plt.show()
            plt.savefig('/home/shenguanlin/results/heatmap_tsne_' + self.types_name[i] + '.png')
            ax.clear()
            plt.clf()
            plt.cla()
            plt.close()

    def get_heatmap_grid(self):
        """Get the heatmap based on the grid data
        """
        point_places = self.tsne_results * self.resolution
        self.grid_densitys = []
        for i in range(5):
            #calculate the sigma in the gauss kernel
            indice = np.arange(0, self.n)
            mask = (self.labels == i)
            selected_indice = indice[mask]
            n = int(np.sum(mask))
            xs = point_places[:, 0][mask]
            ys = point_places[:, 1][mask]
            places = np.stack((xs, ys), axis=1)
            iqr = np.quantile(xs, 0.75) - np.quantile(xs, 0.25)
            h = 1.06 * min(np.std(xs), iqr / 1.34) * (n ** -0.2)
            h2 = h * h

            dist = cdist(places, places, "sqeuclidean").astype(np.float32) #n * n
            gaussian_dist = np.exp(-(dist / h) * (dist / h) / 2) / 2.5066
            density = np.sum(gaussian_dist, axis=1) / n / h2 #n
            max_density = np.max(density)
            density = density / max_density #n
            expanded_density = np.zeros((self.grid_size ** 2))
            expanded_density[selected_indice] = density

            grid_density = expanded_density[self.grid_item_id]
            grid_density = grid_density.reshape(self.grid_size, self.grid_size)
            self.grid_densitys.append(grid_density)
            
            #test
            show_density = grid_density[::-1, :]
            ax = sns.heatmap(show_density)
            plt.show()
            plt.savefig('/home/shenguanlin/results/heatmap_grid_' + self.types_name[i] + '.png')
            ax.clear()
            plt.clf()
            plt.cla()
            plt.close()


    def get_json_result_tsne(self):
        """Get the json result of tsne
        """
        result = {}
        data = []
        for i in range(self.n):
            the_data = {}
            the_data['id'] = i
            the_data['name'] = self.names[i]
            the_data['class'] = self.types_name[self.labels[i]]
            the_data['x'] = float(self.tsne_results[i, 0])
            the_data['y'] = float(self.tsne_results[i, 1])
            type_id = self.types_id[self.labels[i]]
            the_data['reconImg'] = os.path.join('picture', 'pred', type_id, self.names[i] + '.png')
            the_data['gtImg'] = os.path.join('picture', 'gt', type_id, self.names[i] + '.png')
            the_data['chamferDist'] = float(self.chamfer_distances[i])
            data.append(the_data)
        result['data'] = data
        
        heatmap = {}
        heatmap['resolution'] = self.resolution
        densitys = []
        for i in range(5):
            density = {}
            type_name = self.types_name[i]
            data = self.tsne_densitys[i].reshape(self.resolution ** 2).tolist()
            density['class'] = type_name
            density['data'] = data 
            densitys.append(density)
        heatmap['density'] = densitys
        result['heatmap'] = heatmap

        json_result = json.dumps(result)
        with open('/home/shenguanlin/results/tsne_result.json', 'w') as f:
            f.write(json_result)

    def get_json_result_grid(self):
        """Get the json result of grid
        """
        result = {}
        data = []
        for i in range(self.n):
            the_data = {}
            the_data['id'] = i
            the_data['name'] = self.names[i]
            the_data['class'] = self.types_name[self.labels[i]]
            the_data['x'] = (float(self.grid_index[i, 0]) + 0.5) / self.grid_size
            the_data['y'] = (float(self.grid_index[i, 1]) + 0.5) / self.grid_size
            type_id = self.types_id[self.labels[i]]
            the_data['reconImg'] = os.path.join('picture', 'pred', type_id, self.names[i] + '.png')
            the_data['gtImg'] = os.path.join('picture', 'gt', type_id, self.names[i] + '.png')
            the_data['chamferDist'] = float(self.chamfer_distances[i])
            data.append(the_data)
        result['data'] = data
        
        heatmap = {}
        heatmap['resolution'] = self.resolution
        densitys = []
        for i in range(5):
            density = {}
            type_name = self.types_name[i]
            data = self.grid_densitys[i].reshape(self.grid_size ** 2).tolist()
            density['class'] = type_name
            density['data'] = data 
            densitys.append(density)
        heatmap['density'] = densitys
        result['heatmap'] = heatmap

        json_result = json.dumps(result)
        with open('/home/shenguanlin/results/grid_result.json', 'w') as f:
            f.write(json_result)

if __name__ == "__main__":
    a = Backend()
    a.tsne()
    a.get_grid()
    a.get_heatmap_tsne()
    a.get_heatmap_grid()
    a.get_json_result_tsne()
    a.get_json_result_grid()
