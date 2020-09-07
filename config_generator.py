import itertools
from random import shuffle, randint
import math
import yaml
from tqdm import tqdm
import os
RANDOM = [None,]
CONF = dict()
BIND = dict()




server_capacity = [3,2,2]


BIND['loss_type'] = [
    ('WWGAN',{}),
    ('WGAN',{}),
    ('rsgan',{'temp_scale':[1.]}),
]
CONF['temperature'] = [1,5,10,50,100,500,1000,5000]
CONF['temp_scale'] = [1., 0.5, 0.1, 0.05, 0.01]

constraints = dict()
for k,d in BIND.items():
    CONF[k]=[]
    constraints[k]=[]
    for v, c in d:
        CONF[k].append(v)
        constraints[k].append(c)

def get_name(D):
    format_string = "{}__{}_{}"
    keys = ['loss_type','temperature','temp_scale']
    return format_string.format(*[D[k] for k in keys])

def is_valid(D):
    for k,v in constraints.items():
        # print(CONF,D)
        for key, value in v[CONF[k].index(D[list(CONF.keys()).index(k)])].items():
            if D[list(CONF.keys()).index(key)] not in value:
                return False
    return True

try:
    import shutil
    shutil.rmtree('conf')
except:
    pass

L = list(CONF.values())
L = list(filter(is_valid, itertools.product(*L)))

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
            D['name']=get_name(D)
            with open('conf/{}/{}.yml'.format(server, idx), 'w') as outfile:
                yaml.dump(D, outfile)
            idx+=1
            pbar.update(1)
        start = idx