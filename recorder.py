import socket
import time

_TOKEN = "da25f78835beee476f53ec553b4af208"

class ParentJob:
    def __init__(self, name="parameter search"):
        try:
            x = requests.get('https://mine.yuewu.ml/api/', verify=False)
            url = 'https://mine.yuewu.ml/api/new_parent/'
            myobj = {'token': _TOKEN, 'name':name, 'hostname':socket.gethostname()}
            return_dict = json.loads(requests.post(url, data = myobj, verify=False).text)
            if not return_dict['success']:
                return False
            self.id = return_dict['id']
            return True
        except:
            return False
    
    def __init__(self, name="parameter search", retry = 10):
        count = 1
        while(not self._init(name)):
            if count>=retry:
                self.success = False
                return
            count+=1
            time.sleep(5)
        self.success = True

class Job:
    def _init(self, parent_id=None, name="parameter search"):
        try:
            x = requests.get('https://mine.yuewu.ml/api/', verify=False)
            url = 'https://mine.yuewu.ml/api/new_job/'
            if parent_id is None:
                myobj = {'token': _TOKEN, 'name':name, 'hostname':socket.gethostname()}
            else:
                myobj = {'token': _TOKEN, 'name':name, 'hostname':socket.gethostname(), 'parent': parent_id}
            return_dict = json.loads(requests.post(url, data = myobj, verify=False).text)
            if not return_dict['success']:
                return False
            self.id = return_dict['id']
            self.parent_id = return_dict['parent']
            return True
        except:
            return False
    
    def __init__(self, parent_id=None, name="parameter search", retry = 10):
        count = 1
        while(not self._init(parent_id, name)):
            if count>=retry:
                self.success = False
                return
            count+=1
            time.sleep(5)
        self.success = True
    
    def _submit(self, metrics):
        try:
            url = 'https://mine.yuewu.ml/api/submit_long/'
            myobj = {'token': _TOKEN, 'metrics':json.dumps(metrics),"job_id":self.id}
            return_dict = json.loads(requests.post(url, data = myobj, verify=False).text)
            if return_dict['success']:
                return True
        except:
            return False
        return False
    
    def submit(self, metrics, retry=5):
        count = 1
        while(not self._submit(metrics)):
            if count>=retry:
                return False
            count+=1
            time.sleep(5)
        return True

