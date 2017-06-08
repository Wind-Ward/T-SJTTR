# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
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
        self.lineno_list=[]
        self.slice_number=[]
        self.slice_TSC_list=[]


    def addRestVideoComment(self):

        lineno=[]
        self.slice_number.append(len(self.lines))
        slice_TSC = []
        while (len(self.lines) != 0):

            copy_vocabulary = copy.copy(self.vocabulary)
            slice_TSC.append(self.lines[0]["text"])
            for item in self.lines[0]["text"]:

                if item in copy_vocabulary:
                    copy_vocabulary[item] += 1
            self.C.append(copy_vocabulary.values())
            lineno.append(self.lines[0]["lineno"])
            self.lines.pop(0)
            copy_vocabulary = copy.copy(self.vocabulary)

        self.slice_TSC_list.append(slice_TSC)
        print "C size: %d " % len(self.C)
        self.lineno_list.append(lineno)
        self.store_lineno_list()
        self.store_slice_number(self.slice_number)
        self.print_line()



    def print_line(self):
        with open("data/var/slice_TST.txt", 'w') as f:
            with open("data/1993410.txt", 'r') as f2:
                lines = f2.readlines()
                for i, item in enumerate(self.lineno_list):
                    f.write("time slice:" + str(i) + "\n")
                    for item2 in item:
                        f.write(lines[int(item2) - 1] + "\n")
                    f.write("\n")





    def initializeC(self,timeInterval):
        self.lines,timeLength,self.vocabulary=BulletScreen().run()
        preTime=0
        lastTime=preTime+timeInterval
        number=0
        for index in xrange(int(timeLength/timeInterval)):
            lineno=[]
            slice_TSC=[]
            while(len(self.lines)!=0):

                copy_vocabulary = copy.copy(self.vocabulary)
                if self.lines[0]["time"] <=lastTime:
                    slice_TSC.append(self.lines[0]["text"])
                    for item in self.lines[0]["text"]:
                        if item in copy_vocabulary:
                            copy_vocabulary[item]+=1
                    self.C.append(copy_vocabulary.values())
                    number += 1
                    lineno.append(self.lines[0]["lineno"])
                    self.lines.pop(0)
                else:
                    preTime=lastTime
                    lastTime=preTime+timeInterval
                    print "C size: %d " % len(self.C)
                    self.lineno_list.append(lineno)
                    lineno = []
                    self.slice_number.append(number)
                    self.slice_TSC_list.append(slice_TSC)
                    slice_TSC=[]
                    number = 0
                    break

        self.addRestVideoComment()

        print self.lineno_list
        return self.C



    def caculateCwith_TFIDF(self,timeInterval):
        C=self.initializeC(timeInterval)
        _C_matrix=np.array(C,dtype=float)
        row_sum=np.sum(_C_matrix,axis=1)
        column_sum=np.sum(_C_matrix,axis=0)
        row_number=_C_matrix.shape[0]
        column_number=_C_matrix.shape[1]


        #caculate tf
        tf_matrix=np.array([item/row_sum[i] for i,item in enumerate(_C_matrix)])

        #caculate idf
        temp = []
        for j in xrange(column_number):
            sum=0
            for i in xrange(row_number):
                if _C_matrix[i][j]!=0:
                    sum+=1
            temp.append(sum)
        idf=np.log(row_number/(1+np.array(temp)))

        #caculate tfidf
        tfidf=tf_matrix*idf


        time_slice=self.grab_slice_number()
        C_matrix_list=[]
        _tf_idf=list(tfidf)
        print time_slice
        print len(_tf_idf)
        print len(_tf_idf[0])
        for item in time_slice:
            C_matrix_list.append(np.array(_tf_idf[:item]).T)
            _tf_idf.pop(item)


        self.storeCaculatedTFIDF(C_matrix_list)

    def store_lineno_list(self):
        fw = open("data/var/lineno_list", "wb")
        pickle.dump(self.lineno_list,fw)
        fw.close()

    def storeCaculatedTFIDF(self,C_list):
        fw = open("data/var/C_list_tfidf", "wb")
        pickle.dump(C_list, fw)
        fw.close()

    def grab_slice_number(self):
        fr = open("data/var/slice_number", "rb")
        slice_number = pickle.load(fr)
        fr.close()
        return slice_number


    def store_slice_number(self, slice_number):
        print(len(slice_number))
        fw = open("data/var/slice_number", "wb")
        pickle.dump(slice_number, fw)
        fw.close()




if __name__=="__main__":
    timeInterval=300
    i=Initialize_C_Matrix()
    i.caculateCwith_TFIDF(timeInterval)
