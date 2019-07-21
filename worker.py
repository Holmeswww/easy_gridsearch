PATTERN = "#####"


class Worker_Base:

    def __init__(self, gpu_id, que, done_list, terminal, id, logging):
        self.gpu_id=gpu_id
        self.que = que
        self.done_list = done_list
        self.terminal = terminal
        self.id = id
        self.cmdprefix = ""
        self.log = logging
    
    def print(self,*args):
        with self.terminal.location(0, 1 + self.id * 2):
            print(self.terminal.clear_eol, end = "")
            print(self.cmdprefix+" |", *args, end = "")

    def get_hook(self,command):
        # Returns a process hook.
        import os
        from subprocess import Popen, PIPE, STDOUT

        subprocess_env = os.environ.copy()
        subprocess_env["CUDA_VISIBLE_DEVICES"] = str(self.gpu_id)
        process = Popen(command, shell=True, stdout=PIPE, stderr=STDOUT, env=subprocess_env)
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
            buff.append(line.rstrip())

    def execute(self, command):
        import re
        process = self.get_hook(command)
        while True:
            line = process.stdout.readline()
            if not line:
                break
            line = line.rstrip()
            m = re.search(PATTERN+'.*'+PATTERN, line)
            if not m is None:
                string = (m.group(0)[len(PATTERN):-len(PATTERN)]).split("$")
                caption = string[2]
                progress = string[1]
                self.print(caption)
            if line.find("Traceback (most recent") >= 0:
                self.print("Errored")
                self.log_error(process, line)
                return None

        if (exitCode == 0):
            return True
        else:
            return None


class Worker(Worker_Base):
    def __init__(self,gpu_id,que,done_list,terminal,id,logging,model_dir,output_dir,snapshot_dir):
        super().__init__(gpu_id,que,done_list,terminal,id,logging)
        self.model_dir = model_dir
        self.output_dir = output_dir
        self.snapshot_dir = snapshot_dir
        self.print("Worker for GPU:", gpu_id,"INITIATED")

  def work(self):
      self.print("Worker for GPU:", gpu_id,"LAUNCHED")
      import os
      while(True):                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
          name = self.que.randpop()
          if name is None:
              time.sleep(120)
              continue
          self.set_prefix("Running {}".format(name))

          if not os.path.exists(os.path.join(self.output_dir,name)):
              os.makedirs(os.path.join(self.output_dir,name))
          
          if not os.path.exists(os.path.join(self.snapshot_dir,name)):
              os.makedirs(os.path.join(self.snapshot_dir,name))

          cmd = ' '.join(["cd", self.model_dir, ";", "python", "main.py", "--config={}.yaml".format(name)])
          cmd += " --output_dir=\"{}\"".format(os.path.join(self.output_dir,name))
          cmd += " --snapshot_dir=\"{}\"".format(os.path.join(self.snapshot_dir,name))
          

          self.execute(cmd)
          self.done_list.append(name)