# -*- coding: utf-8 -*-
import numpy as np
from ReadBulletScreen import BulletScreen
from collections import OrderedDict
import uniout
import copy
try:
    import cPickle as pickle
except ImportError:
    import pickle
class Initialize_C_Matrix(object):
    def __init__(self):

        self.vocabulary={}
        self.C=[]
        self.C_list=[]
        self.lines=[]

    def addRestVideoComment(self):
        self.C=[]
        while (len(self.lines) != 0):
            copy_vocabulary = copy.copy(self.vocabulary)
            for item in self.lines[0]["text"]:
                if item in copy_vocabulary:
                    copy_vocabulary[item] += 1
            self.C.append(copy_vocabulary.values())
            self.lines.pop(0)
            copy_vocabulary = copy.copy(self.vocabulary)
        print "C size: %d " % len(self.C)
        self.C_list.append(self.C)


    def initializeC(self,timeInterval):
        self.lines,timeLength,self.vocabulary=BulletScreen().run()
        preTime=0
        lastTime=preTime+timeInterval
        for index in xrange(int(timeLength/timeInterval)):
            while(len(self.lines)!=0):
                copy_vocabulary = copy.copy(self.vocabulary)
                if self.lines[0]["time"] <=lastTime:
                    for item in self.lines[0]["text"]:
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
        print "size of C_list: " +str(len(self.C_list))
        print "size of C_list[0]: " + str(len(self.C_list[0]))
        print "size of C_list[0][3]: " + str(len(self.C_list[0][3]))
        print self.C_list[0][12]
        self.store()
        return self.C_list

    def caculateCwith_TFIDF(self):
        C_list=self.grab()
        C_list2=[]
        for index,C_matrix in enumerate(C_list):
            _C_matrix=np.array(C_matrix,dtype=float)
            row_sum=[np.sum(item) for item in _C_matrix]
            _column_sum=[]
            row_num=_C_matrix.shape[0]
            column_num=_C_matrix.shape[1]
            for j in xrange(column_num):
                not_zero=0
                for i in xrange(row_num):
                    if _C_matrix[i][j]!=0:
                        not_zero+=1
                # caveat
                # there is the case that not_zero==0,it will cause numerator divide by zero  (item/row_sum[i])
                if not_zero == 0:
                    not_zero+=1
                _column_sum.append(not_zero)
            column_sum=np.array(_column_sum)
            C_matrix2=[]
            for i,item in enumerate(_C_matrix):
                C_matrix2.append(item/row_sum[i]*np.log(1+row_num/column_sum))
            C_list2.append(C_matrix2)
        print "C_tfidf"
        print list(C_list2[0][12])
        self.storeCaculatedTFIDF(C_list2)




    def store(self):
        fw = open("data/var/C_list", "wb")
        pickle.dump(self.C_list,fw)
        fw.close()

    def storeCaculatedTFIDF(self,C_list):
        fw = open("data/var/C_list_tfidf", "wb")
        pickle.dump(C_list, fw)
        fw.close()

    def grab(self):
        fr = open("data/var/C_list","rb")
        vocabList = pickle.load(fr)
        fr.close()
        return vocabList

if __name__=="__main__":
    #timeInterval=1000
    #Initialize_C_Matrix().initializeC(timeInterval)
    Initialize_C_Matrix().caculateCwith_TFIDF()
