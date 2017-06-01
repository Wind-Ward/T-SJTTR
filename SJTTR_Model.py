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


def grab_C_list():
        fr = open("data/var/C_list_tfidf", "rb")
        C_list = pickle.load(fr)
        #print C_list[0].shape
        fr.close()
        return C_list

def grab_T_list():
        fr = open("data/var/T_list", "rb")
        T_list = pickle.load(fr)
        fr.close()
        return T_list

def grab_lineno_list():
    fr = open("data/var/lineno_list", "rb")
    lineno_list = pickle.load(fr)
    fr.close()
    return lineno_list


def distance(M,N):
    return np.linalg.norm(M - N)

class SJTTR(object):

    def __init__(self,rho=0.5,gamma=0.8,l_ambda=200,m=3,w=1):
        self.C_list=grab_C_list()

        #print self.C_list[0].shape
        self.T_list=grab_T_list()
        self.lineno_list=grab_lineno_list()
        self.rho=rho
        self.gamma=gamma
        self.Lambda=l_ambda
        self.K=len(self.T_list)
        self.m=m
        self.w=w
        self.X_list=[]



    def initialize_A_B_beta(self,N_old,N_new):
        old_A_k=np.full((N_old,N_old),10)
        old_B_k=np.full((N_old,N_old),10)
        old_beta_k=np.ones(N_new)
        return old_A_k,old_B_k,old_beta_k

    def _beta_k(self,old_A_k,old_B_k,theta_k):
        return np.sqrt((self.rho*np.sum(old_A_k**2,axis=0)+(1-self.rho)*np.sum(old_B_k**2,axis=0))/\
                                (self.Lambda*theta_k))

    def _A_k(self,k,new_beta_k,old_A_k):
        if k==0:
            #print "C_list["+str(k)+"].shape:"+str(self.C_list[k].shape)
            temp=np.dot(self.C_list[k].T,self.C_list[k])
            #print "temp.shape:"+str(temp.shape)
            #print "old_A_k"+str(old_A_k.shape)
            #print "new_beta_k"+str(len(new_beta_k))
            temp2=(np.dot(old_A_k,temp)+np.dot(old_A_k,np.linalg.inv(np.diag(new_beta_k))))
            print old_A_k
            print old_A_k.shape
            #print old_A_k
            return temp/temp2*old_A_k
        else:
            temp = np.dot(self.C_list[k].T,self.C_hat)
            return temp / (np.dot(old_A_k, temp) + np.dot(old_A_k, np.linalg.inv(np.diag(new_beta_k)))) * old_A_k


    def _B_k(self,k,new_beta_k,old_B_k):
        if k == 0:
            temp = np.dot(self.T_list[k].T,self.T_list[k])
            return temp /(np.dot(old_B_k,temp) + np.dot(old_B_k, np.linalg.inv(np.diag(new_beta_k)))) * old_B_k
        else:
            temp = np.dot(self.T_list[k].T,self.T_hat)
            return temp / (np.dot(old_B_k, temp) + np.dot(old_B_k, np.linalg.inv(np.diag(new_beta_k)))) * old_B_k


    def _augumented_C_and_T(self,k):
        rp_comment=[item[1] for item in sorted([(item,i) for i,item in enumerate(self.new_beta_k)],\
                                    key=lambda x:x[0],reverse=True)[:self.m]]
        self.X_list.append(rp_comment)
        C_hat=[]
        C_hat.append(self.C_list[k])
        C_hat.append([self.C_list[k-1][item] for item in rp_comment])

        T_hat=[]
        T_hat.append(self.T_list[k])
        T_hat.append([self.T_list[k-1][item] for item in rp_comment])
        return C_hat,T_hat


    def _theta(self, k, N_old, N_new):
        if (k == 0):
            return np.ones(N_old)
        else:
            return np.ones(N_new)


    def _calc_last_comment(self):
        rp_comment = [item[1] for item in sorted([(item, i) for i, item in enumerate(self.new_beta_k)], \
                                                 key=lambda x: x[0], reverse=True)[:self.m]]
        self.X_list.append(rp_comment)


    def display_representative_comment(self):
        with open("data/representative", 'w') as f:
            for i,item in enumerate(self.X_list):
                for item2 in enumerate(item):
                    f.write(self.lineno_list[i][item2])
                f.write("\n")

    def estimation(self):
        index=0
        for k in xrange(self.K):
            if k==0:
                N_old=self.C_list[k].shape[1]
                self.old_A_k,self.old_B_k,self.old_beta_k=self.initialize_A_B_beta(N_old,N_old)
                self.theta_k = self._theta(k, N_old, N_old)
                while True:
                    self.new_beta_k=self._beta_k(self.old_A_k,self.old_B_k,self.theta_k)
                    print "%d beta_k: %d" % (k,index)

                    # print self.new_beta_k
                    # print len(self.new_beta_k)
                    while True:
                        self.new_A_k=self._A_k(k,self.new_beta_k,self.old_A_k)
                        dis=distance(self.old_A_k,self.new_A_k)
                        print "%d A dis: %f" % (k,dis)
                        if dis<=1:
                            break
                        else:
                            self.old_A_k=self.new_A_k
                        index+=1
                        print " %d A loop: %d" % (k,index)

                    while True:
                        self.new_B_k = self._B_k(k, self.new_beta_k, self.old_B_k)
                        dis=distance(self.old_B_k, self.new_B_k)
                        print "%d A dis: %f" % (k, dis)
                        if  dis<= 1:
                            break
                        else:
                            self.old_B_k = self.new_B_k
                        index+=1
                        print "%d B loop: %d" % (k,index)

                    dis=distance(self.old_beta_k,self.new_beta_k)
                    print "%d A dis: %f" % (k, dis)
                    if dis<=1:
                        break
                    else:
                        self.old_beta_k=self.new_beta_k
                        index+=1
                        print "index: %d" % index


            else:
                self.C_hat,self.T_hat=_augumented_C_and_T(k)
                N_old = self.C_list[k].shape[1]
                N_new=N_old+self.m
                self.old_A_k, self.old_B_k, self.old_beta_k =self.initialize_A_B_beta(N_old,N_new)
                self.theta_k = self._theta(k, N_old, N_new)
                print "%d beta_k: %d" % (k, index)

                while True:
                    self.new_beta_k = self._beta_k(self.old_A_k, self.old_B_k,self.theta_k)
                    print "%d beta_k: %d" % (k, index)
                    print self.new_beta_k
                    while True:
                        self.new_A_k = self._A_k(k, self.new_beta_k, self.old_A_k)
                        dis=distance(self.old_A_k, self.new_A_k)
                        print "%d A dis: %f" % (k, dis)
                        if dis <= 1:
                            break
                        else:
                            self.old_A_k = self.new_A_k
                        index += 1
                        print " %d A loop: %d" % (k, index)

                    while True:
                        self.new_B_k = self._B_k(k, self.new_beta_k, self.old_B_k)
                        dis=distance(self.old_B_k, self.new_B_k)
                        print "%d A dis: %f" % (k, dis)
                        if dis <= 1:
                            break
                        else:
                            self.old_B_k = self.new_B_k
                        index += 1
                        print " %d beta loop: %d" % (k, index)
                    dis=distance(self.old_beta_k, self.new_beta_k)
                    print "%d A dis: %f" % (k, dis)
                    if  dis<= 1:
                        break
                    else:
                        self.old_beta_k=self.new_beta_k
                        index += 1
                        print " %d beta loop: %d" % (k, index)


        self._calc_last_comment()
        self.display_representative_comment()

if __name__=="__main__":
    SJTTR().estimation()















