import datetime
import json
import os
import sys
import shutil
import time

from tqdm import tqdm
def app_path():
    """Returns the base application path."""
    if hasattr(sys, 'frozen'):
        # Handles PyInstaller
        return os.path.dirname(sys.executable)  #使用pyinstaller打包后的exe目录
    return os.path.dirname(__file__)                 #没打包前的py目录

def readFile(path,content={}):
    if '.json' in path:
        if not os.path.exists(path):
            with open(path,'w',encoding='utf-8') as fp:
                json.dump(content,fp,ensure_ascii=False)
        with open(path,'r',encoding='utf-8') as fp:
            content = json.loads(fp.read())
    else:
        if not os.path.exists(path):
            with open(path,'w',encoding='utf-8') as fp:
                fp.write('{}'.format(content))
        with open(path,'r',encoding='utf-8') as fp:
            content = fp.read()
    return content

def getCreateTime(path)->str:
    return str(datetime.datetime.fromtimestamp(os.path.getctime(path))).replace(':',"-").replace(' ','-')

def renameTime(basedir,filename,rename=""):
    if '.' in filename:
        exp=filename[filename.rfind('.'):]
    else:
        exp=''
    resource=os.path.join(basedir,filename)
    if rename=="":
        target=os.path.join(basedir,getCreateTime(resource)+exp)
    else:
        target=os.path.join(basedir,rename)
    os.rename(resource,target)

def getTimeStamp(datetime='2020-4-06 00:00'):
    if datetime=='':
        return 0
    s_t = time.strptime(datetime, "%Y-%m-%d %H:%M")  # 返回元祖
    mkt = time.mktime(s_t)
    # print(mkt)
    return mkt

def getFileTime(resource)->float:
    mtime = os.path.getmtime(resource) #修改时间
    # print(mtime)
    # mtime_string = datetime.datetime.fromtimestamp(int(mtime))
    return mtime

def operate(resource='',target='',op='copy',timename=0,oldDate='2020-4-06 00:00',newDate='2021-4-06 00:00',minLayer=1,maxLayer=999,layer=0,targetLayer=1,filterList=[]):
    layer+=1
    # print(resource,layer)
    basedir_r=resource
    basedir_t=target
    try:
        if layer==1:
            loopListdir=tqdm(os.listdir(resource),"检阅中")
        else:
            loopListdir=os.listdir(resource)
    except OSError as res:
        print(res)
        return
    for dirs in loopListdir:
        resource=os.path.join(basedir_r,dirs)
        #小于目标层保持源目录，不小于移动至指定目录
        if layer<targetLayer:
            target=os.path.join(basedir_t,dirs)
        # if layer==1:
        #     print(resource)
        is_dir=os.path.isdir(resource)
        #从最小层操作到最大层，如果=就操作过1层了
        if is_dir and layer<maxLayer:
            operate(resource,target,op,timename,oldDate,newDate,minLayer,maxLayer,layer,targetLayer,filterList=filterList)
        else:
            #小于层数不操作，大于层数不在递归，此处不可能处理最大层以上文件
            if layer<minLayer:
                continue
            #过滤表空代表不过滤，true代表文件夹,不在列表不操作跳过
            if not filterList:
                pass
            #如果目录过滤，不在考虑后缀
            elif is_dir in filterList:
                pass
            #否则过滤其他后缀文件并排除目录
            elif resource.split('.')[-1:][0] not in filterList or is_dir:
                continue
            # print(layer,resource)
            oldTime=getTimeStamp(oldDate)
            newTime=getTimeStamp(newDate)
            fileTime=getFileTime(resource)
            if fileTime>newTime or fileTime<oldTime:
                continue
            # print(resource,layer)
            # print(oldTime,newTime,fileTime,op)
            try:
                if op=='move':
                    # try:
                    # shutil.move(resource,target+'/'+dirs[3:])
                    shutil.move(resource,target)
                    # except shutil.Error as res:
                    #     print(res)
                elif op=='copy':
                    shutil.copy2(resource,target)
                else:
                    os.remove(resource)
                    return
                if timename==1:
                    renameTime(target,dirs)
            except OSError as res:
                print(res)
            # time.sleep(2)
            
def isExist(path:str,op=1):
    # if '.' in path:
    #     path=path[:path.rfind('.')]
    print(path)
    if not os.path.exists(path):
        if op==1 and os.path.isdir(path):
            os.makedirs(path)
        return False
    else:
        return True
def inputText(resource,target,op=3):
    if op==3 or op==1:
        resource=input('请输入源路径:')
    elif op==3 or op==2:
        target=input('请输入目的路径:')
    else:
        if op!=4:
            return
    if not isExist(resource,0):
        inputText(resource,target,1)
    if not isExist(target):
        inputText(resource,target,2)
    return resource,target
if __name__=='__main__':
    configPath=app_path()+'/config.json'
    if not isExist(configPath):
        configDict={"resource":"","target":"","oldDate":"2000-3-02 00:00","newDate":"3000-3-02 15:00",
                    "op":"copy","timename":0,"minLayer":1,"maxLayer":999,"targetLayer":0,"filterList":[]}
        with open(configPath,"w",encoding="utf-8") as fp:
            fp.write(json.dumps(configDict,ensure_ascii=False)) 
    with open(configPath,"r",encoding="utf-8") as fp:
        configDict=json.loads(fp.read())
    resource=configDict["resource"]
    target=configDict["target"]
    op=configDict["op"]
    # resource=r'F:\Group2'
    # target=r'F:\Group'
    inputText(resource,target,4)
    print(configDict["oldDate"],configDict["newDate"],configDict["timename"],configDict['minLayer'],configDict['maxLayer'])
    operate(resource,target,op,configDict["timename"],configDict["oldDate"],configDict["newDate"],
          configDict['minLayer'],configDict['maxLayer'],0,configDict["targetLayer"],configDict["filterList"])
    