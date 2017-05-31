# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import numpy as np
from ReadBulletScreen import BulletScreen
import ldaModel
import uniout
import copy
import os
try:
    import cPickle as pickle
except ImportError:
    import pickle
class Initialize_T_matrix(object):
    def __init__(self):
        self.lines = []

    def addRestVideoComment(self,index,dictory):

        with open(dictory + "_" + str(index), 'w') as f:
            while (len(self.lines) != 0):
                for item in self.lines[0]["text"]:
                        f.write(item + " ")
                f.write("\n")
                self.lines.pop(0)

    def initializeC(self,timeInterval,dictory="data/LDA_ProcessWithT/"):
        self.lines,timeLength=self.grab()
        preTime=0
        lastTime=preTime+timeInterval
        for index in xrange(int(timeLength/timeInterval)):
            with open(dictory+"_"+str(index), 'w') as f:
                while(len(self.lines)!=0):
                    if self.lines[0]["time"] <=lastTime:
                        for item in self.lines[0]["text"]:
                            f.write(item+" ")
                        f.write("\n")
                        self.lines.pop(0)
                    else:
                        preTime=lastTime
                        lastTime=preTime+timeInterval
                        break

        self.addRestVideoComment(index+1,dictory)


    def grab(self):
        fr = open("data/var/lines","rb")
        dict = pickle.load(fr)
        fr.close()
        return dict["lines"],dict["timelength"]


    def calculateTwithLDA(self,dirname="/Users/yinfeng/PycharmProjects/BulletScreen/SJTTR/data/LDA_ProcessWithT"):
        T_list=[]
        for file in os.listdir(dirname):
            abs_path = os.path.join(dirname, file)
            T_list.append(ldaModel.run2(abs_path))
        self.store(T_list)

    def store(self, T_list):
        fw = open("data/var/T_list", "wb")
        pickle.dump(T_list, fw)
        fw.close()






if __name__=="__main__":
    timeInterval = 1000
    #Initialize_T_matrix().initializeC(timeInterval)
    Initialize_T_matrix().calculateTwithLDA()

