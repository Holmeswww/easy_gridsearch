import argparse
import multiprocessing,threading
import logging
import time
import os, sys
from blessings import Terminal
import torch
from time import localtime, strftime
from utils import display_time, SafeList, EWriter, SafeValue
import signal
from tqdm import tqdm
import pickle
from worker import Worker
# import yaml
READ_INTERVAL = 1200


class Master:

    def __init__(self, q, bestScore, done_list, term, start_time, opt):
        self.done_list=done_list
        self.terminal = term
        self.start_time = start_time
        self.opt = opt
        self.writer = EWriter(term)
        self.loaded = []
        self.height = term.height
        self.width = term.width
        self.bestScore = bestScore
        self.q = q

        if not os.path.exists(self.opt.output_dir):
            os.makedirs(self.opt.output_dir)
        if not os.path.exists(self.opt.snapshot_dir):
            os.makedirs(self.opt.snapshot_dir)
        if not os.path.exists(self.opt.tb_dir):
            os.makedirs(self.opt.tb_dir)

        if os.path.exists(os.path.join(self.opt.output_dir,"done_list.pkl")):
            with open(os.path.join(self.opt.output_dir,"done_list.pkl"), "rb") as fp:
                self.done_list.list=pickle.load(fp)

        if os.path.exists(os.path.join(self.opt.output_dir,"best_score.pkl")):
            with open(os.path.join(self.opt.output_dir,"best_score.pkl"), "rb") as fp:
                self.bestScore.val=pickle.load(fp)

    def print(self, s):
        if self.height!=self.terminal.height or self.width!=self.terminal.width:
            self.height = self.terminal.height
            self.width = self.terminal.width
            print(self.terminal.clear)
        stat_string = "Que size: {} | Done size: {}".format(len(self.q.list), len(self.done_list.list))
        timestring = "Uptime: " + display_time(time.time() - self.start_time)
        timestring += " | Avg job time: {}".format("inf" if len(self.done_list.list)==0 else display_time((time.time() - self.start_time)//len(self.done_list.list)))
        with self.terminal.location(0, self.terminal.height - 1):
            print(self.terminal.clear_eol, end = "")
            print(timestring + " | " + stat_string + " | " + str(s), end = "")
            sys.stdout.flush()

    def dbgprint(self, *s):
        with self.terminal.location(0, self.terminal.height - 3):
            print(self.terminal.clear_eol, end = "")
            print(*s, end = "")
            sys.stdout.flush()

    def run(self):
        self.print('Master thread initiated.')
        while(True):
            time.sleep(1)
            self.print(self.bestScore.get())

    def signal_handler(self, sig, frame):
        self.print('Exiting... Saving progress...')
        if len(self.done_list.list)>0:
            with open(os.path.join(self.opt.output_dir,"done_list.pkl"), "wb") as fp:
                pickle.dump(self.done_list.list,fp)
        with open(os.path.join(self.opt.output_dir,"best_score.pkl"), "wb") as fp:
            pickle.dump(self.bestScore.val,fp)
        os._exit(0)

class Reader:

    def __init__(self, que, done_list, term, start_time, opt):
        self.q=que
        self.done_list=done_list
        self.terminal = term
        self.start_time = start_time
        self.ISread=False
        self.opt = opt
        self.writer = EWriter(term)
        self.loaded = []
        self.height = term.height
        self.width = term.width

    def print(self, s):
        with self.terminal.location(0, self.terminal.height - 3):
            print(self.terminal.clear_eol, end = "")
            print(str(s), end = "")
            sys.stdout.flush()

    def dbgprint(self, *s):
        with self.terminal.location(0, self.terminal.height - 4):
            print(self.terminal.clear_eol, end = "")
            print(*s, end = "")
            sys.stdout.flush()

    def run(self):
        self.print('Reader thread initiated. Scanning for jobs...')
        self.read()
        c = 0
        while(True):
            time.sleep(1)
            c+=1
            self.print('Time until next scan: {} s'.format(READ_INTERVAL-c))
            if c==READ_INTERVAL:
                self.print('Scanning for new jobs.')
                self.read()
                c = 0
    
    def read(self):
        import re
        for root, subFolders, files in list(os.walk(self.opt.command_dir)):
            if len(files) >= 1:
                for f in tqdm(files, file = self.writer):
                    if not re.search('.*\.yml$',f):
                        continue
                    name = f[:-4]
                    if name in self.loaded or name in self.done_list.list:
                        continue
                    self.q.append((name, root))
                    self.loaded.append(name)
                    self.ISread = True

        # print(term.move(0,0)+term.move_up)

    # def readyaml(self, path):
    #     import yaml
    #     dy = yaml.load(path)
    #     d = {}
    #     if "parents" in dy:
    #         for p in dy['parents']:
    #             dp = self.readyaml(os.path.join(self.opt.command_dir, "parents", p+".yml"))
    #             d.update(dp)
    #     d.update(dy)
    #     return d


if __name__ == '__main__':

    # print('Press Ctrl+C')
    # signal.pause()

    term = Terminal()
    print(term.enter_fullscreen)
    print(term.clear)

    parser = argparse.ArgumentParser()
    parser.add_argument('--gpu', type=str, default=None,
                        help='GPUs to use.')
    parser.add_argument('--threads', type=int, default=1,
                        help='threads_per_GPU')
    parser.add_argument('--model_dir', type=str, required=True,
                        help='directory of model to run (main.py)')
    parser.add_argument('--command_dir', type=str, required=True,
                        help='directory of commands')
    # parser.add_argument('--snapshot_dir', type=str, default="./viz",
    #                     help='A snapshot directory for direct visualization')
    parser.add_argument('--output_dir', type=str, default=".",
                        help='Output directory')
    parser.add_argument('--timestamp', type=str, default=None,
                        help='timestamp to resume')
    parser.add_argument('--fresh', type=int, default=0,
                        help='start fresh')

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(message)s',
                        filename='./trainer.log',
                        filemode='w')
    opt = parser.parse_args()


    print(term.move(0,0) + "Welcome to easy_gridsearch! I'm able to see {} GPUs and {} CPUs.".format(torch.cuda.device_count(), multiprocessing.cpu_count()))

    while(not os.path.exists(opt.command_dir)):
        with term.location(0, term.height - 1):
            print(term.clear_eol, end = "")
            print("waiting for command folder to be created..", end = "")
            sys.stdout.flush()
        time.sleep(10)
    
    if os.path.exists("overrides.yml"):
        import yaml
        overrides = yaml.load(open("overrides.yml"), Loader=yaml.FullLoader)
    else:
        overrides = dict()

    # time.sleep(3)
    if opt.timestamp is None:
        T = time.time()
        timestring = strftime("%Y_%m_%d_%H_%M_%S", localtime(T))
    else:
        T = time.strptime(opt.timestamp, "%Y_%m_%d_%H_%M_%S")
        timestring = opt.timestamp
    timestring = "grid_search_"+timestring

    opt.snapshot_dir = os.path.join(opt.output_dir, timestring, "snap")
    opt.tb_dir = os.path.join(opt.output_dir, timestring, "TensorBoard")
    opt.output_dir = os.path.join(opt.output_dir, timestring, "out")

    if opt.gpu is None:
        opt.gpu = [str(i) for i in range(torch.cuda.device_count())]
    else:
        opt.gpu = opt.gpu.split(',')
    gpu_job_list=[gpu_ID for x in range(opt.threads) for gpu_ID in opt.gpu]
    num_workers = min(multiprocessing.cpu_count(), len(gpu_job_list))

    q = SafeList()
    done = SafeList()
    val = SafeValue(0, lambda x, y: x>=y)
    master=Master(q, val, done, term, T, opt)
    signal.signal(signal.SIGINT, master.signal_handler)
    reader=Reader(q, done, term, T, opt)
    # signal.signal(signal.SIGINT, reader.signal_handler)

    master_thread=threading.Thread(target=(lambda: master.run()))
    master_thread.start()
    reader_thread=threading.Thread(target=(lambda: reader.run()))
    reader_thread.start()

    while(not reader.ISread):
        time.sleep(1)

    abs_model = os.path.abspath(opt.model_dir)
    abs_snap = os.path.abspath(opt.snapshot_dir)
    abs_tb = os.path.abspath(opt.tb_dir)
    abs_out = os.path.abspath(opt.output_dir)

    workers = []
    for i in range(num_workers):
        workers.append(Worker(gpu_job_list[i], q, done, term, i, logging, val, overrides, abs_model, abs_out, abs_snap, abs_tb))

    for worker in workers:
        worker_work= lambda: worker.work()
        t = threading.Thread(target=(worker_work))
        t.start()