#!/usr/bin/env python
# coding: utf-8

# # Problem 1

# In[1]:


# referred from https://towardsdatascience.com/ml-from-scratch-decision-tree-c6444102436a

#https://towardsdatascience.com/ml-from-scratch-decision-tree-c6444102436a

#https://machinelearningmastery.com/implement-decision-tree-algorithm-scratch-python/


# In[2]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import collections
from collections import Counter
from sklearn.model_selection import train_test_split
from sklearn import tree
from sklearn.preprocessing import LabelEncoder


# In[3]:


dataset = {
    "Age": [24,53,23,25,32,52,22,43,52,48],
    "Salary ($)": [40000,52000,25000,77000,48000,110000,38000,44000,27000,65000],
    "College degree": ['yes','no','no','yes','yes','yes','yes','no','no','yes']
}


# In[4]:


df = pd.DataFrame(dataset)


# In[5]:


df = df.replace({'College degree': {'yes':1,'no':0}})


# In[6]:


plt.scatter(df.iloc[:,0],df.iloc[:,1],c=df.iloc[:,2])
plt.show()


# In[7]:


class DecisionTree():
    def __init__(self, feature_index=None, threshold=None, left=None, right=None, info_gain=None, value=None):
         ## initialise the tree 
        
        # for decision node
        self.feature_index = feature_index
        self.threshold = threshold
        self.left = left
        self.right = right
        self.info_gain = info_gain
        
        # for leaf node
        self.value = value


# In[8]:


class DecisionTreeScratch():
    def __init__(self, minimum_split_samples=2, maximum_depth_tree=2):
        # initialise the multi variate tree
        
        self.root = None
        
        # stopping conditions
        self.minimum_split_samples = minimum_split_samples
        self.maximum_depth_tree = maximum_depth_tree
        
    def construct_tree_node(self, df, curr_depth=0):
        # recursive function to build the tree
        
        data, target = df[:,:-1], df[:,-1]
        sample, feat = np.shape(data)
        
        # split until stopping conditions are met
        if sample>=self.minimum_split_samples and curr_depth<=self.maximum_depth_tree:
            # find the best split
            split_best = self.split_best(df, sample, feat)
            # check if information gain is positive
            if split_best["info_gain"]>0:
                # recur left
                left_subtree = self.construct_tree_node(split_best["df_left"], curr_depth+1)
                # recur right
                right_subtree = self.construct_tree_node(split_best["df_right"], curr_depth+1)
                # return decision node
                return DecisionTree(split_best["feature_index"], split_best["threshold"], 
                            left_subtree, right_subtree, split_best["info_gain"])
        
        # compute leaf node
        leafval = self.find_leaf_val(target)
        # return leaf node
        return DecisionTree(value=leafval)
    
    def split_best(self, df, sample, feat):
        # function to get the best split to left and right nodes
        
        # dictionary to store the best split
        split_best = {}
        mig = -float("inf")
        
        # loop over all the features
        for feature_index in range(feat):
            feature_values = df[:, feature_index]
            possible_thresholds = np.unique(feature_values)
            # loop over all the feature values present in the data
            for i in possible_thresholds:
                # get current split
                df_left, df_right = self.split(df, feature_index, i)
                # check if childs are not null
                if len(df_left)>0 and len(df_right)>0:
                    y, left_y, right_y = df[:, -1], df_left[:, -1], df_right[:, -1]
                    # compute information gain
                    curr_info_gain = self.find_if(y, left_y, right_y, "gini")
                    # update the best split if needed
                    if curr_info_gain>mig:
                        split_best["feature_index"] = feature_index
                        split_best["threshold"] = i
                        split_best["df_left"] = df_left
                        split_best["df_right"] = df_right
                        split_best["info_gain"] = curr_info_gain
                        mig = curr_info_gain
                        
        # return best split
        return split_best
    
    def split(self, df, feature_index, threshold):
        # function to split data into its children
        
        df_left = np.array([row for row in df if row[feature_index]<=threshold])
        df_right = np.array([row for row in df if row[feature_index]>threshold])
        return df_left, df_right
    
    def find_if(self, parent, left, right, mode="entropy"):
        # function to find information 
        
        weight_left = len(left) / len(parent)
        weight_right = len(right) / len(parent)
        if mode=="gini":
            gain = self.find_gini(parent) - (weight_left*self.find_gini(left) + weight_right*self.find_gini(right))
        else:
            gain = self.entropy(parent) - (weight_left*self.entropy(left) + weight_right*self.entropy(right))
        return gain
    
    def entropy(self, y):
        # function to calculate the entropy
        
        class_labels = np.unique(y)
        entropy = 0
        for cls in class_labels:
            p_cls = len(y[y == cls]) / len(y)
            entropy += -p_cls * np.log2(p_cls)
        return entropy
    
    def find_gini(self, target):
        #function to calculate the gini index
        
        label = np.unique(target)
        g = 0
        for i in label:
            q = len(target[target == i]) / len(target)
            g += q**2
        return 1 - g
    
    def find_leaf_val(self, target):
        # function to find the leaf node values
        
        target = list(target)
        return max(target, key=target.count)
    
    def display(self, decision=None, diff=" "):
        # function to display the tree completely
        
        if not decision:
            decision = self.root

        if decision.value is not None:
            print(decision.value)

        else:
            print("Feature Index"+str(decision.feature_index), "<=", decision.threshold)
            print('Information gain : {}'.format(decision.info_gain))
            print("%sleft child:" % (diff), end="")
            self.display(decision.left, diff + diff)
            print("%sright child:" % (diff), end="")
            self.display(decision.right, diff + diff)
    
    def fit(self, data, target):
        # function to train the model, exaxctly similar to the inbuilt function
        
        df = np.concatenate((data, target), axis=1)
        self.root = self.construct_tree_node(df)
    
    def prediction(self, val):
        #predicting new data 
        
        p = [self.pred(v, self.root) for v in val]
        return p
    
    def pred(self, val, decision):
        # predicting a single data
        
        if decision.value!=None: 
            return decision.value
        value = val[decision.feature_index]
        if value<=decision.threshold:
            return self.pred(val, decision.left)
        else:
            return self.pred(val, decision.right)


# In[9]:


data = df.iloc[:,:-1].values
target = df.iloc[:,-1].values.reshape(-1,1)


# In[10]:


X_train, X_test, y_train, y_test = train_test_split(data , target, test_size=0.3, random_state=42)


# In[11]:


dtc = DecisionTreeScratch(minimum_split_samples=2, maximum_depth_tree=3)
dtc.fit(X_train,y_train)
dtc.display()


# ![WhatsApp%20Image%202022-12-09%20at%2011.36.31%20PM.jpeg](attachment:WhatsApp%20Image%202022-12-09%20at%2011.36.31%20PM.jpeg)

# ![download%20%281%29.jfif](attachment:download%20%281%29.jfif)

# In[ ]:





# # Problem 2

# In[12]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn import tree
from sklearn.preprocessing import LabelEncoder
import collections
from collections import Counter


# In[13]:


from sklearn.metrics import accuracy_score,precision_score,recall_score
from sklearn.base import clone
from sklearn.model_selection import StratifiedKFold,cross_validate
from sklearn.tree import DecisionTreeClassifier


# # Dataset 1

# In[14]:


d1=pd.read_csv('letter-recognition.data')


# In[15]:


d1.head()


# In[16]:


d1.columns=['capital letters','x-box(h)','y-box(v)','width','height','pixels','x-bar','y-bar','x*xbar(variance)','y*ybar(variance)','xybar(correlation)','(x*x*y)bar','(y*y)bar','x-edge(lr)','xegvy(corr wid y)','y-edge(tb)','yegvx(corr with x)']


# In[17]:


d1 = d1[(d1['capital letters'] == 'C') | (d1['capital letters'] == 'G')]


# In[18]:


d1.head()


# In[19]:


d1.shape


# In[20]:


d1['capital letters'] = d1['capital letters'].replace(to_replace = ['C','G'], value=[1,0])
d1.head()


# In[30]:


X=d1.drop('capital letters',axis=1)
X
X=X.values
X


# In[31]:


y=d1['capital letters']
y


# In[32]:


from sklearn.model_selection import StratifiedKFold,cross_validate
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score,precision_score,recall_score
from sklearn.base import clone


# In[33]:


from sklearn.model_selection import train_test_split

X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.6686,random_state=0)


# ## Bagging

# In[34]:


class BaggedTreeClassifier(object):
    def __init__(self,nd=100):
        self.nd = nd
        self.bag_mod = []
        self.errors_train=[]
    def __del__(self):
        del self.nd
        del self.bag_mod
    def sample_bootstraps(self,data):
        o_dict   = {}
        uni_val_cnt = 0
        data_len = data.shape[0]
        ptr = [i for i in range(data_len)]
        for b in range(self.nd):
            bootstrap_ptr = np.random.choice(ptr,replace=True,size=data_len)
            bootstrap_samp = data[bootstrap_ptr,:]
            uni_val_cnt = uni_val_cnt + len(set(bootstrap_ptr))
            otb = list(set(ptr) - set(bootstrap_ptr))
            after_output = np.array([])
            if otb:
                after_output = data[otb,:]
            o_dict['boot_'+str(b)] = {'boot':bootstrap_samp,'test':after_output}
        return(o_dict)
    def get_params(self, deep = False):
        return {'nd':self.nd}
  
    def fit(self,X_train,y_train,all_metrices=False,depth=False):
        self.errors_train= []
        t_data = np.concatenate((X_train,y_train.values.reshape(-1,1)),axis=1)
        strap_dict = self.sample_bootstraps(t_data)
        accur = np.array([])
        precision = np.array([])
        recall_acc = np.array([])
        if depth:
            cls = DecisionTreeClassifier(class_weight='balanced',max_depth = 1)
        else:
            cls = DecisionTreeClassifier(class_weight='balanced',max_depth = 6)
        for b in strap_dict:
            model = clone(cls)
            model.fit(strap_dict[b]['boot'][:,:-1],strap_dict[b]['boot'][:,-1].reshape(-1, 1))
            self.bag_mod.append(model)
            if strap_dict[b]['test'].size:
                y_prediction  = model.predict(strap_dict[b]['test'][:,:-1])
                acc = accuracy_score(strap_dict[b]['test'][:,-1],y_prediction)
                pre = precision_score(strap_dict[b]['test'][:,-1],y_prediction,average='micro')   
                rec = recall_score(strap_dict[b]['test'][:,-1],y_prediction,average='micro')
                accur = np.concatenate((accur,acc.flatten()))
                self.errors_train.append(acc)
                precision = np.concatenate((precision,pre.flatten()))
                recall_acc = np.concatenate((recall_acc,rec.flatten()))
        if all_metrices:
            print("Std error(accuracy): %.2f" % np.std(accur))
            print("Std error(precision): %.2f" % np.std(precision))
            print("Std error(recall): %.2f" % np.std(recall_acc))

    def predict(self,X):
        predictions = []
        for m in self.bag_mod:
            y_prediction = m.predict(X)
            predictions.append(y_prediction.reshape(-1,1))
        ypred = np.round(np.mean(np.concatenate(predictions,axis=1),axis=1)).astype(int)
        return(ypred)


# In[35]:


from sklearn.model_selection import train_test_split
X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.6686,random_state=0)


# In[36]:


##depth at 1
clf = BaggedTreeClassifier()
clf.fit(X,y,all_metrices=True,depth=True)


# In[37]:


M_scores = ['accuracy','precision','recall']
Scores = cross_validate(clf,X,y,cv=StratifiedKFold(10),scoring=M_scores)
print('Mean Accuracy: %.2f' % np.mean(Scores['test_accuracy']))
print('Mean Precision: %.2f' % np.mean(Scores['test_precision']))
print('Mean Recall: %.2f' % np.mean(Scores['test_recall']))


# In[38]:


##depth at 7
clf = BaggedTreeClassifier()
clf.fit(X,y,all_metrices=True,depth=False)


# In[39]:


M_scores = ['accuracy','precision','recall']
Scores = cross_validate(clf,X,y,cv=StratifiedKFold(10),scoring=M_scores)
print('Mean Accuracy: %.2f' % np.mean(Scores['test_accuracy']))
print('Mean Precision: %.2f' % np.mean(Scores['test_precision']))
print('Mean Recall: %.2f' % np.mean(Scores['test_recall']))


# In[40]:


plt.figure(figsize=(8,6))
plt.plot(clf.errors_train)
plt.title('Accuracy')
plt.xlabel('Stump')
plt.show()


# ## AdaBoost

# In[41]:


def compute_error(y, y_pred, indi_w):
    a=np.not_equal(y, y_pred)
    return (sum(indi_w * (a).astype(int)))/sum(indi_w)

def compute_alpha(error):
    return np.log((1 - error) / error)

def update_weights(indi_w, alpha, y, y_pred):
    return indi_w * np.exp(alpha * (np.not_equal(y, y_pred)).astype(int))

class AdaBoost:
    
    def __init__(self):
        self.alphas = []
        self.G_M = []
        self.T = None
        self.errors_train = []
        self.pred_err = []

    def fit(self, X, y, T = 100,all_metrices=False):
        
        self.alphas = [] 
        self.errors_train = []
        self.T = T
        
        for m in range(0, T):
            
            if m == 0:
                indi_w = np.ones(len(y)) * 1 / len(y)  # At m = 0, weights are all the same and equal to 1 / N
            else:
                indi_w = update_weights(indi_w, d, y, y_pred)
            
            G_m = DecisionTreeClassifier(max_depth = 5)  
            G_m.fit(X, y, sample_weight = indi_w)
            y_pred = G_m.predict(X)
            
            self.G_M.append(G_m) 
            
            com_err = compute_error(y, y_pred, indi_w)
            self.errors_train.append(com_err)

            d = compute_alpha(com_err)
            self.alphas.append(d)
            
            if m%100==0:
                print(f"{m}th iteration;error:{com_err}")
        assert len(self.G_M) == len(self.alphas)
        
    def predict(self, X):
        w_predictions = pd.DataFrame(index = range(len(X)), columns = range(self.T)) 

        for m in range(self.T):
            y_pred_m = self.G_M[m].predict(X) * self.alphas[m]
            w_predictions.iloc[:,m] = y_pred_m
        y_pred = (1 * np.sign(w_predictions.T.sum())).astype(int)

        return y_pred
    def error_rates(self, X, y):
        self.pred_err = []
        for m in range(self.T):
            y_hat_m = self.G_M[m].predict(X)          
            com_err = compute_error(y = y, y_pred = y_hat_m, indi_w = np.ones(len(y)))
            self.pred_err.append(com_err)


# In[42]:


A_B = AdaBoost()
A_B.fit(X_train, y_train, T = 400)
y_pred = A_B.predict(X_test)
y_pred
#print('Total error rate :', round(compute_error(y_test, y_pred, np.ones(len(y_test))), 4))


# In[43]:


from sklearn.metrics import accuracy_score
accuracy_score(y_test, y_pred)


# In[44]:


plt.figure(figsize=(8,6))
plt.plot(A_B.errors_train)
plt.hlines(0.5, 0, 400, colors = 'red', linestyles='dashed')
plt.title('Training error rates by stump')
plt.xlabel('Stump')
plt.show()


# In[45]:


A_B.error_rates(X_test, y_test)
plt.figure(figsize=(8,6))
plt.plot(A_B.pred_err)
plt.hlines(0.5, 0, 400, colors = 'red', linestyles='dashed')
plt.title('Out-of-sample error rates by stump')
plt.xlabel('Stump')
plt.show()


# For Bagging
# 
# for max_depth=1: 
# Mean Accuracy: 0.77
# Mean Precision: 0.81
# Mean Recall: 0.71
# 
# for max_depth=6:
# Mean Accuracy: 0.96
# Mean Precision: 0.98
# Mean Recall: 0.93
# 
# for max_depth=7:
# Mean Accuracy: 0.96
# Mean Precision: 0.98
# Mean Recall: 0.94

# For Boosting
# 
# for max_depth=1: accuracy is 0.5034
# 
#  
#  for max_depth=6: accuracy is 0.5034

# # Dataset 2

# In[46]:


d2 = pd.read_csv('german.data',sep=' ',header=None)
d2.head()


# In[47]:


d2.columns = ['status(checking acc)','Duration(month)', 'Credit Hist','Purpose','Credit Amt','Savings acc/bonds', 'Employment', 'Installment rate(% disposable income)', 'Personal status and sex', 'Other debtors or guarantors', 'Present residence since', 'Property', 'Age in years', 'Other installment plans', 'Housing', 'Number of existing credits at this bank', 'Job', 'Number of people being liable to provide maintenance for', 'Telephone', 'foreign worker','Target']


# In[48]:


d2.drop(columns=['status(checking acc)','Purpose','Personal status and sex','Present residence since','Telephone', 'foreign worker'],axis=1,inplace=True)


# In[49]:


d2.head()


# In[50]:


d2_final = pd.get_dummies(data=d2, columns=['Duration(month)', 'Credit Hist','Savings acc/bonds', 'Employment','Other debtors or guarantors', 'Property','Other installment plans', 'Housing','Job'])


# In[51]:


d2_final.head()


# In[52]:


x1=d2_final.drop('Target',axis=1)
x1=x1.values
x1


# In[53]:


y1=d2_final['Target']
y1


# In[54]:


from sklearn.model_selection import train_test_split

X_train,X_test,y_train,y_test=train_test_split(x1,y1,test_size=0.5998,random_state=
0)


# In[55]:


X_train.shape


# In[56]:


X_test.shape


# In[57]:


from sklearn.tree import DecisionTreeClassifier
classifier=DecisionTreeClassifier(max_depth=2)
model=classifier.fit(X_train,y_train)
y_pred=model.predict(X_test)
y_pred


# In[58]:


from sklearn.metrics import accuracy_score
accuracy_score(y_test, y_pred)


# In[59]:


clf = BaggedTreeClassifier()
clf.fit(x1,y1,all_metrices=True,depth=True)


# In[60]:


M_scores = ['accuracy','precision','recall']
Scores= cross_validate(clf,x1,y1,cv=StratifiedKFold(10),scoring=M_scores)
print('Mean Accuracy: %.2f' % np.mean(Scores['test_accuracy']))
print('Mean Precision: %.2f' % np.mean(Scores['test_precision']))
print('Mean Recall: %.2f' % np.mean(Scores['test_recall']))


# In[61]:


plt.figure(figsize=(8,6))
plt.plot(clf.errors_train)
plt.title('Accuracy')
plt.xlabel('Stump')
plt.show()


# For Bagging
# 
# for max_depth=1: Mean Accuracy: 0.54 Mean Precision: 0.79 Mean Recall: 0.46
# 
# for max_depth=6: Mean Accuracy: 0.66 Mean Precision: 0.80 Mean Recall: 0.69
# 
# for max_depth=7: Mean Accuracy: 0.67 Mean Precision: 0.80 Mean Recall: 0.71

# In[62]:


A_B = AdaBoost()
A_B.fit(X_train, y_train, T = 400)
y_pred = A_B.predict(X_test)
y_pred


# In[63]:


from sklearn.metrics import accuracy_score
accuracy_score(y_test, y_pred)


# In[64]:


plt.figure(figsize=(8,6))
plt.plot(A_B.errors_train)
plt.hlines(0.5, 0, 400, colors = 'red', linestyles='dashed')
plt.title('Training error rates by stump')
plt.xlabel('Stump')
plt.show()


# In[65]:


A_B.error_rates(X_test, y_test)
plt.figure(figsize=(8,6))
plt.plot(A_B.pred_err)
plt.hlines(0.5, 0, 400, colors = 'red', linestyles='dashed')
plt.title('Out-of-sample error rates by stump')
plt.xlabel('Stump')
plt.show()


# for max_depth=1: accuracy=0.705 for max_depth=6: accuracy= 0.705

# # Dataset 3

# In[66]:


d3 = pd.read_csv('spambase.data',header=None)
d3.head()


# In[67]:


d3.columns = ['make','address', 'all','3d','our','over', 'remove', 'internet', 'order', 'mail', 'receive', 'will', 'people', 'report','addresses', 'Free', 'Business', 'Email', 'you', 'credit', 'your','font','000','money','hp','hpl','george','650','lab','labs','telnet','857','data','415','85','technology','1999','parts','pm','direct','cs','meeting','original','project','re','edu','table','conference',';:','(;','[:','!:','$:','#:','len(average)','len(longest)','len(total)','Target']


# In[68]:


d3.head()


# In[69]:


d3['mail'].head()


# In[70]:


x3=d3.drop('Target',axis=1)
x3


# In[71]:


y3=d3['Target']
y3


# In[72]:


from sklearn.model_selection import train_test_split

X_train,X_test,y_train,y_test=train_test_split(x3,y3,test_size=0.7826,random_state=
0)


# In[73]:


X_train.shape


# In[74]:


X_test.shape


# In[75]:


from sklearn.tree import DecisionTreeClassifier
classifier=DecisionTreeClassifier(max_depth=2)
model=classifier.fit(X_train,y_train)
y_pred=model.predict(X_test)
y_pred


# In[76]:


#for depth=1
clf = BaggedTreeClassifier()
clf.fit(x3,y3,all_metrices=True,depth=True)


# In[77]:


M_scores = ['accuracy','precision','recall']
Scores = cross_validate(clf,x1,y1,cv=StratifiedKFold(10),scoring=M_scores)
print('Mean Accuracy: %.2f' % np.mean(Scores['test_accuracy']))
print('Mean Precision: %.2f' % np.mean(Scores['test_precision']))
print('Mean Recall: %.2f' % np.mean(Scores['test_recall']))


# For Bagging
# 
# for max_depth=1: Mean Accuracy: 0.55 Mean Precision: 0.80 Mean Recall: 0.48
# 
# for max_depth=6: Mean Accuracy: 0.66 Mean Precision: 0.81 Mean Recall: 0.67
# 
# for max_depth=7: Mean Accuracy: 0.68 Mean Precision: 0.80 Mean Recall: 0.71

# In[78]:


A_B = AdaBoost()
A_B.fit(X_train, y_train, T = 400)
y_pred = A_B.predict(X_test)
y_pred


# In[79]:


from sklearn.metrics import accuracy_score
accuracy_score(y_test, y_pred)


# In[80]:


plt.figure(figsize=(8,6))
plt.plot(clf.errors_train)
plt.title('Accuracy')
plt.xlabel('Stump')
plt.show()


# For Boosting
# 
# for max_depth=1: accuracy =0.400 for max_depth=10: accuracy= 0.4059

# In[81]:


A_B.error_rates(X_test, y_test)
plt.figure(figsize=(8,6))
plt.plot(A_B.pred_err)
plt.hlines(0.5, 0, 400, colors = 'red', linestyles='dashed')
plt.title('Out-of-sample error rates by stump')
plt.xlabel('Stump')
plt.show()


# In[82]:


A_B.error_rates(X_test, y_test)
plt.figure(figsize=(8,6))
plt.plot(A_B.pred_err)
plt.hlines(0.5, 0, 400, colors = 'red', linestyles='dashed')
plt.title('Out-of-sample error rates by stump')
plt.xlabel('Stump')
plt.show()


# # References
https://medium.com/@derilraju/implementing-adaboost-classifier-from-scratch-in-python-84e1a8bd2999

https://machinelearningmastery.com/adaboost-ensemble-in-python/

https://insidelearningmachines.com/build-a-bagging-classifier-in-python/
# # Report

# The experiments consisted of predicting the models with bagging and boosting methods. The experiments were also made on the max_depth=1(shallow trees  or decision stumps or depth=1) and when max_depth=6,7(deep trees or depth with 6 or 7).
# 
# The performance also increases with the addition of more trees say 100.
# 
# 
# Bagging for the three dataset:
# Bagging for the letter recognition dataset did well with accuracy of 0.96 for deep trees from accuracy of 0.77 for decision stumps.
# Bagging for german dataset 0.67 for deep trees from 0.54 for shallaw trees.
# bagging for spambase dataset 0.68 for deep trees from 0.55 for decision stumps.
# Thus, the bagging function did great on the dataset of letter recognition with 96% accuracy.
# 
# Adaboost for the three dataset:
# for letter recognition , it was 0.5034 same for both the type of trees.
# for german dataset, it was 0.705 for both the deep and shallow trees
# for spambase dataset it was 0.4059 for max_depth=10 and 0.400 for max_depth=1.
# Thus, the adaboost dataset did well on the german dataset with accuracy of 70%.
# 
# 
# The error rate of the classifiers decrease when the number of weak learners increase. The performance of the trees increase with the addition of more trees(accuracy increases with 100 trees,400 trees,etc.)

# In[ ]:




