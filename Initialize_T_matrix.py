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
        self.slice_number=[]

    def addRestVideoComment(self,dictory):
        with open(dictory +"_comment.txt", 'a') as f:
            self.slice_number.append(len(self.lines))
            while (len(self.lines) != 0):
                for item in self.lines[0]["text"]:
                        f.write(item + " ")
                f.write("\n")
                self.lines.pop(0)


    def initializeT(self,timeInterval,dictory="data/LDA_ProcessWithT/"):
        self.lines,timeLength=self.grab()
        print "lines size: %d" % len(self.lines)
        preTime=0
        lastTime=preTime+timeInterval
        number=0
        with open(dictory + "_comment.txt", 'w') as f:
            for index in xrange(int(timeLength/timeInterval)):
                while(len(self.lines)!=0):
                    if self.lines[0]["time"] <=lastTime:
                        number+=1
                        for item in self.lines[0]["text"]:
                            f.write(item+" ")
                        f.write("\n")
                        self.lines.pop(0)
                    else:
                        preTime=lastTime
                        lastTime=preTime+timeInterval
                        self.slice_number.append(number)
                        number=0
                        break

        self.addRestVideoComment(dictory)
        self.store_slice_number(self.slice_number)


    def calculateTwithLDA(self,dirname="data/LDA_ProcessWithT/"):
        self.slice_number=self.grab_slice_number()
        print self.slice_number
        theta=list(ldaModel.run2(dirname+"_comment.txt"))
        T_list=[]

        for item in self.slice_number:
            T_list.append(theta[:item])
            theta.pop(item)
        self.store(T_list)
        for item in T_list:
           print len(item)
        print "T_list size: %d" % len(T_list)

    def store_slice_number(self, slice_number):
        print(len(slice_number))
        fw = open("data/var/slice_number", "wb")
        pickle.dump(slice_number, fw)
        fw.close()

    def grab_slice_number(self):
        fr = open("data/var/slice_number", "rb")
        slice_number = pickle.load(fr)
        fr.close()
        return slice_number

    def grab(self):
        fr = open("data/var/lines", "rb")
        dict = pickle.load(fr)
        fr.close()
        return dict["lines"], dict["timelength"]

    def store(self, T_list):
        fw = open("data/var/T_list", "wb")
        temp=[]
        for item in T_list:
            temp.append(np.array(item).T)
        pickle.dump(temp, fw)
        # print(temp[0].shape)
        # print(type(temp[0]))
        fw.close()




if __name__=="__main__":
    timeInterval = 100
    t=Initialize_T_matrix()
    #t.initializeT(timeInterval)
    t.calculateTwithLDA()
    #Initialize_T_matrix().calculateTwithLDA()

