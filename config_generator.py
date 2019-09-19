import itertools
from random import shuffle, randint
import math
import yaml
from tqdm import tqdm
import os
RANDOM = [None,]
CONF = dict()




server_capacity = [3,2,2]


CONF['Diters'] = [1,3,5,10,15]
CONF['SEED'] = RANDOM
CONF['ImageSize'] = [32,]
CONF['Dset'] = ['cifar10',]
CONF['DataRoot'] = ['/DataSet/',]
CONF['BS'] = [64,32,16]
CONF['niter'] = [210,]
CONF['nz'] = [64,100,128,200,256]
CONF['LAMBDA'] = [5,10,20,30]
CONF['PPO_iters'] = [1, 5, 10]
CONF['max_grad_norm'] = [0.3, 0.5, 1.]
CONF['clip_param'] = [0.1, 0.2, 0.3]
CONF['G_SIZE'] = [32, 64, 128, 200]
CONF['D_SCALE'] = [1.0, 1.5, 2.0]
CONF['LR'] = [1e-4, 2e-4, 1e-3, 1e-2]
CONF['beta1'] = [0, 0.5, 0.9, 0.95, 0.99]
CONF['beta2'] = [0, 0.5, 0.9, 0.95, 0.99, 0.995, 0.999]
CONF['checkpoints'] = [[(0.5/21, 4.0), (1/21, 6.5), (3/21, 7.0), (5/21, 7.4), (9/21, 7.6), (12/21, 7.8), (15/21, 7.9), (20/21, 8.0)],]

try:
    import shutil
    shutil.rmtree('conf')
except:
    pass

L = list(CONF.values())
L = list(itertools.product(*L))
shuffle(L)

print("Splitting {} jobs".format(len(L)))

tot = sum(server_capacity)
start = 0
idx = 0
with tqdm(total = len(L)) as pbar:
    for server, capacity in enumerate(server_capacity):
        os.makedirs('conf/{}'.format(server))
        while(idx < start+math.ceil(len(L)*capacity/tot)  and idx < len(L)):
            D = dict()
            for i, key in enumerate(list(CONF.keys())):
                if L[idx][i] is None:
                    D[key] = randint(0, 1000000)
                else:
                    D[key] = L[idx][i]
            with open('conf/{}/{}.yml'.format(server, idx), 'w') as outfile:
                yaml.dump(D, outfile)
            idx+=1
            pbar.update(1)
        start = idx