import itertools
from random import shuffle, randint
import math
import yaml
from tqdm import tqdm
import os
RANDOM = [None,]
CONF = dict()




server_capacity = [1,]


CONF['Diters'] = [5]
CONF['SEED'] = [None, None, None, None, None]#RANDOM
CONF['ImageSize'] = [32,]
CONF['Dset'] = ['cifar10',]
CONF['DataRoot'] = ['/DataSet/',]
CONF['BS'] = [32]
CONF['niter'] = [500,]
CONF['nz'] = [128]
CONF['LAMBDA'] = [5]
CONF['LAMBDA2'] = [2]
CONF['Factor_M'] = [0]
CONF['PPO_iters'] = [5]
CONF['max_grad_norm'] = [0.5]
CONF['clip_param'] = [0.4]
CONF['G_SIZE'] = [256]
CONF['D_SCALE'] = [1.3]
CONF['LR'] = [1.5e-4]
CONF['beta1'] = [0.95]
CONF['beta2'] = [0.5]
CONF['checkpoints'] = [[(0.5/21, 1.0),],] #(1/21, 6.5), (3/21, 7.0), (5/21, 7.4), (9/21, 7.6), (12/21, 7.8), (15/21, 7.9), (20/21, 8.0)],]

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