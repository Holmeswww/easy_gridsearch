import itertools
from random import shuffle, randint
import math
import yaml
from tqdm import tqdm
import os
RANDOM = [None,]
CONF = dict()




server_capacity = [1,]


CONF['Dset'] = ['cifar10',]
CONF['DataRoot'] = ['/DataSet/',]
CONF['BS'] = [32, 64]
CONF['niter'] = [125000]
CONF['WWGAN'] = [True, False]
CONF['lr'] = [1e-3, 1e-4, 1e-5]
CONF['beta1'] = [0.0, 0.5, 0.8, 0.9, 0.95, 0.99, 0.999]
CONF['beta2'] = [0.0, 0.5, 0.8, 0.9, 0.95, 0.99, 0.999]

try:
    import shutil
    shutil.rmtree('dcgan_conf')
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
        os.makedirs('dcgan_conf/{}'.format(server))
        while(idx < start+math.ceil(len(L)*capacity/tot)  and idx < len(L)):
            D = dict()
            for i, key in enumerate(list(CONF.keys())):
                if L[idx][i] is None:
                    D[key] = randint(0, 1000000)
                else:
                    D[key] = L[idx][i]
            with open('dcgan_conf/{}/{}.yml'.format(server, idx), 'w') as outfile:
                yaml.dump(D, outfile)
            idx+=1
            pbar.update(1)
        start = idx