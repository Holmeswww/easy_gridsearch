PATTERN = "#####"


class Worker_Base:

    def __init__(self, gpu_id, que, done_list, terminal, id, logging, best_val, info):
        from utils import Writer
        self.gpu_id=gpu_id
        self.que = que
        self.done_list = done_list
        self.terminal = terminal
        self.id = id
        self.cmdprefix = ""
        self.log = logging
        self.best_val = best_val
        self.writer = Writer(terminal, 2 + self.id * 2)
        self.parent_id = info['parent_id']
    
    def print(self,*args):
        with self.terminal.location(0, 1 + self.id * 2):
            print(self.terminal.clear_eol, end = "")
            print(self.cmdprefix+" |", *args, end = "")
    
    def print_progress(self,prog):
        if int(prog.split("/")[0])==0:
            from tqdm import tqdm
            self.Pbar = tqdm(total = int(prog.split("/")[1]), file = self.writer)
            self.current_progress = 0
        elif int(prog.split("/")[0]) == int(prog.split("/")[1]):
            if self.Pbar is not None:
                self.Pbar.close()
                self.Pbar=None
        else:
            self.Pbar.update(int(prog.split("/")[0])-self.current_progress)
            self.current_progress=int(prog.split("/")[0])

    def get_hook(self,command):
        # Returns a process hook.
        import os
        from subprocess import Popen, PIPE, STDOUT

        subprocess_env = os.environ.copy()
        subprocess_env["CUDA_VISIBLE_DEVICES"] = str(self.gpu_id)
        process = Popen(command, shell=True, stdout=PIPE, stderr=STDOUT, env=subprocess_env)
        self.log.info(command)
        return process
    
    def set_prefix(self, string):
        self.cmdprefix = string

    def log_error(self, process, line):
        buff = [line]
        while True:
            line = process.stdout.readline()
            if not line:
                self.log.debug("\n".join(buff))
                return
            buff.append(line.decode('utf-8').rstrip())

    def execute(self, command):
        import re
        process = self.get_hook(command)
        while True:
            line = process.stdout.readline()
            if not line:
                break
            line = line.decode('utf-8').rstrip()
            m = re.search(PATTERN+'.*'+PATTERN, line)
            if not m is None:
                string = (m.group(0)[len(PATTERN):-len(PATTERN)]).split("$")
                caption = string[2]
                progress = string[1]
                if string[3].strip() != "":
                    value = float(string[3])
                    self.best_val.update(value, caption)
                else:
                    self.print(caption)
                    if progress!="":
                        self.print_progress(progress)
            if line.find("Traceback (most recent") >= 0:
                self.print("Errored")
                self.log_error(process, line)
                return None

        return True
        # if (exitCode == 0):
        #     return True
        # else:
        #     return None


class Worker(Worker_Base):
    def __init__(self,gpu_id,que,done_list,terminal,id,logging, best_val, overrides, model_dir, model_file, output_dir, snapshot_dir, tb_dir, info):
        super().__init__(gpu_id,que,done_list,terminal,id,logging, best_val, info)
        self.model_dir = model_dir
        self.model_file = model_file
        self.output_dir = output_dir
        self.snapshot_dir = snapshot_dir
        self.tb_dir = tb_dir
        self.overrides=overrides
        self.print("Worker for GPU:", gpu_id,"INITIATED")

    def work(self):
        self.print("Worker for GPU:", self.gpu_id,"LAUNCHED")
        import os, yaml, time
        while(True):                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
            item = self.que.randpop()
            if item is None:
                self.print("Worker for GPU:", self.gpu_id,"Waiting")
                time.sleep(120)
                continue
            name, root = item
            self.set_prefix("GPU:{} running {}".format(self.gpu_id,name))
            d = yaml.load(open(os.path.join(root,"{}.yml".format(name))), Loader=yaml.FullLoader) # self.readyaml(os.path.join(root,f))
            if not os.path.exists(os.path.join(self.output_dir, name)):
                os.makedirs(os.path.join(self.output_dir, name))
            d.update(self.overrides)
            with open(os.path.join(self.output_dir, name, "conf.yml"),"w") as fd:
                fd.write(yaml.dump(d, default_flow_style=False))
            if not os.path.exists(os.path.join(self.output_dir,name)):
                os.makedirs(os.path.join(self.output_dir,name))

            cmd = ' '.join(["cd", self.model_dir, ";", "python", self.model_file, "--id={}".format(name)])
            cmd += " --output_dir=\"{}\"".format(os.path.join(self.output_dir,name))
            cmd += " --snapshot_dir=\"{}\"".format(self.snapshot_dir)
            cmd += " --tb_dir=\"{}\"".format(self.tb_dir)
            cmd += " --parent_id={}".format(self.parent_id)
            
            self.execute(cmd)
            self.done_list.append(name)