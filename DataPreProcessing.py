# -*- coding: utf-8 -*-
import numpy as np
from ReadBulletScreen import BulletScreen
from collections import OrderedDict
import uniout
import copy
class DataPreProcessing(object):
    def __init__(self):

        self.vocabulary={}
        self.C=[]
        self.C_list=[]
        self.lines=[]

    def addRestVideoComment(self):
        self.C=[]
        while (len(self.lines) != 0):
            for item in self.lines[0]["text"]:
                copy_vocabulary = copy.copy(self.vocabulary)
                if item in copy_vocabulary:
                    copy_vocabulary[item] += 1
            self.C.append(copy_vocabulary.values())
            self.lines.pop(0)
        print "C size: %d " % len(self.C)
        self.C_list.append(self.C)


    def initializeC(self,timeInterval):
        self.lines,timeLength,self.vocabulary=BulletScreen().run()
        preTime=0
        lastTime=preTime+timeInterval
        docSet=[]
        for index in xrange(int(timeLength/timeInterval)):
            doc =[]
            docSet.append(doc)
            while(len(self.lines)!=0):
                if self.lines[0]["time"] <=lastTime:
                    for item in self.lines[0]["text"]:
                        copy_vocabulary=copy.copy(self.vocabulary)
                        if item in copy_vocabulary:
                            copy_vocabulary[item]+=1
                    self.C.append(copy_vocabulary.values())
                    self.lines.pop(0)
                else:
                    preTime=lastTime
                    lastTime=preTime+timeInterval
                    self.C_list.append(self.C)
                    print "C size: %d " % len(self.C)
                    self.C=[]
                    break

        self.addRestVideoComment()
        print "length of C_list: %d" % len(self.C_list)
        return self.C_list


    def caculateCwith_TFIDF(self):





if __name__=="__main__":
    timeInterval=1000
    DataPreProcessing().initializeC(timeInterval)