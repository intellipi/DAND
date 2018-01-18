#!/usr/bin/python

import cPickle as pickle
import numpy as np
import pprint

from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data

from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_selection import SelectKBest
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline

from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import RandomForestClassifier


### Load the dictionary containing the dataset

with open("final_project_dataset.pkl", "r") as data_file:
    my_dataset = pickle.load(data_file)



print "Number of people in the dataset (data points): ",len(my_dataset)
print "Number of original features in the dataset: ",len(my_dataset.values()[1])
print "List of original features: "
pprint.pprint(my_dataset.values()[1])


### Task 1: Select what features you'll use.
### features_list is a list of strings, each of which is a feature name.
### The first feature must be "poi".

'''
The features will be ranked, tested and selected in a further step.
For now, all features except for email_address will be loaded: a total of 20 out of 21 (including the 'poi' variable). 
'''

my_features = ['poi',
                 'salary',
                 'bonus',
                 'deferral_payments',
                 'total_payments',
                 'exercised_stock_options',
                 'restricted_stock',
                 'restricted_stock_deferred',
                 'total_stock_value',
                 'director_fees',
                 'deferred_income',
                 'long_term_incentive',
                 'loan_advances',
                 'expenses',
                 'other',
                 'to_messages',
                 'from_this_person_to_poi',
                 'from_messages',
                 'from_poi_to_this_person',
                 'shared_receipt_with_poi'
                ]





### POI/Non-POI:
poi = 0
npoi = 0
for i in my_dataset.values():
    if i['poi'] == 1:
        poi += 1
    if i['poi'] == 0:
        npoi += 1

print "Allocation across classes (POI/non-POI): "
print "Total POI: ", poi
print "Total non POI: ", npoi




### Task 2: Remove outliers

'''
Among Enron people in the dataset, two are clearly not persons and need to be removed.
One person in the dataset has no data (all features are zeroes), which must be removed.
'''

my_dataset.pop('TOTAL', 0) # not a person
my_dataset.pop('THE TRAVEL AGENCY IN THE PARK', 0) # not a person
my_dataset.pop('LOCKHART EUGENE E', 0) # has no data 


'''
We should also avoid bias due to missing information ('NaN') concentrated in POIs.
For example, if all POIs have 'NaN' for a specific feature, the algorithm may
conclude that "every time a feature is missing, the person is a POI". 

We should test if it happens for any of our features and drop them from our analysis.
'''

total_poi = 0
total_values = 0

for k in my_dataset:
    
    n = my_dataset[k]['poi']
    total_poi = total_poi + n
    total_values +=1

for i in my_features:
    
    NaN_value = 0  # how many values in a feature are NaN?
    NaN_poi = 0    # of those NaN values, how many are associated to a POI?
    
    for k in my_dataset:
        
        poi = my_dataset[k]['poi']
        value = my_dataset[k][i]
        
        if value == 'NaN':
            NaN_value += 1
            if poi:
                NaN_poi += 1
        else:
            next
            
    # If all POIs (which are few) are associated to NaN values in a feature, 
    # it's not advisable to use the feature, because the model can be biased.

    if NaN_poi == total_poi: # If all POIs are NaN       
        print "removed feature: ", i, "---> NaN features: ", NaN_value, "---> NaN POIs", NaN_poi
        my_features.remove(i)



### Task 3: Create new feature(s)

'''
Extra feature 1: ratio of messages sent to POI / messages sent to any person
Extra feature 2: ratio of messages received from POI / messages received from any person
'''

for i in my_dataset.values():
    i['to_poi_ratio'] = 0
    i['from_poi_ratio'] = 0
 
    if float(i['to_messages']) > 0:
        i['to_poi_ratio'] = float(i['from_this_person_to_poi'])/float(i['to_messages'])
        
    if float(i['from_messages']) > 0:
        i['from_poi_ratio'] = float(i['from_poi_to_this_person'])/float(i['from_messages'])
    
my_features.extend(['to_poi_ratio', 'from_poi_ratio'])


### Extract features and labels from dataset for local testing
data = featureFormat(my_dataset, my_features, sort_keys = True)
labels, features = targetFeatureSplit(data)

# Scale features
scaler = MinMaxScaler()
features = scaler.fit_transform(features)

# K-best features
k_best = SelectKBest(k='all')
k_best.fit(features, labels)

# Rank all features in descending order, except for the first feature ("POI")
results_list = zip(my_features[1:], k_best.scores_) 
results_list = sorted(results_list, key=lambda x: x[1], reverse=True)

print "Features ordered from best to worst (K-Best):\n"
pprint.pprint(results_list)


###########################################################
########### SELECT BEST PARAMETERS TO BE DUMPED ###########
###########################################################

### Task 4: Try a varity of classifiers
### Please name your classifier clf for easy export below.
### Note that if you want to do PCA or other multi-stage operations,
### you'll need to use Pipelines. For more info:
### http://scikit-learn.org/stable/modules/pipeline.html


### Task 5: Tune your classifier to achieve better than .3 precision and recall 
### using our testing script. Check the tester.py script in the final project
### folder for details on the evaluation method, especially the test_classifier
### function. Because of the small size of the dataset, the script uses
### stratified shuffle split cross validation. For more info: 
### http://scikit-learn.org/stable/modules/generated/sklearn.cross_validation.StratifiedShuffleSplit.html

'''
Tasks 4 & 5 will be run together, by using Pipeline and GridSearchCV.
- Pipeline garantees to run all the steps in sequence over the same data sample. 
- GridSearchCV is a way of systematically working through multiple combinations of parameter tunes, cross-validating 
    as it goes to determine which tune gives the best performance. 

- Feature scaling was done as a step in Pipeline. The method used was 'MinMaxScaler'. 
  It transforms all features to range between 0 and 1. 
- K-Best was done as a step in Pipeline. It's a way of evaluating the optimal number of features at the same time as model parameters.
'''

def best_params(classifier, parameters, my_dataset=my_dataset, my_features=my_features, pca=False, scoring='f1',\
                verbose=True, random_state=42):

    data = featureFormat(my_dataset, my_features, sort_keys = True)
    labels, features = targetFeatureSplit(data)  
    

    features_train, features_test, labels_train, labels_test = \
        train_test_split(features, labels, test_size=0.2, random_state=random_state)  

        
    ### Pipeline
    if pca==True: # PCA step enabled
        pipe = Pipeline(steps=[('scaling', MinMaxScaler()), ("PCA", PCA(random_state=random_state)),\
                               ("k_best", SelectKBest()), ("classifier", classifier)])
    else:
        pipe = Pipeline(steps=[('scaling', MinMaxScaler()),("k_best", SelectKBest()),("classifier", classifier)])
    
    
    ### GridSearchCV
    gs = GridSearchCV(pipe, parameters, scoring=scoring, n_jobs=-1, verbose=verbose)
    gs.fit(features_train, labels_train)
    pred = gs.predict(features_test)  

    clf = gs.best_estimator_
    
    from tester import test_classifier
    test_classifier(clf, my_dataset, my_features, folds=1000)
    


    
    
###########################################################
##################### MODEL SELECTION #####################
###########################################################


# Naive Bayes
clf_nb = GaussianNB()
params_grid_nb = {
    'k_best__k': [4, 5, 6, 7, 8, 9, 10]
}

# Decision Tree
clf_dtc = DecisionTreeClassifier()
params_grid_dtc = {
    'k_best__k': [4, 6, 8, 10],
    'classifier__criterion': ["entropy", "gini"],
    'classifier__min_samples_leaf': [2, 4, 6],
    'classifier__min_samples_split': [2, 4, 6]
}


# Adaboost
clf_ada = AdaBoostClassifier()
params_grid_ada = {
    'k_best__k': [4, 6, 8, 10],
    'classifier__n_estimators': [40, 50, 60],
    'classifier__learning_rate': [.6, .8, 1, 1.2, 1.5]
}


# Random Forest
clf_rf = RandomForestClassifier()
params_grid_rf = {
    'k_best__k': [4, 6, 8, 10],
    'classifier__criterion': ["entropy", "gini"],
    'classifier__min_samples_split': [2, 4, 6],
    'classifier__min_samples_leaf': [1, 2, 4],
    'classifier__n_estimators': [5, 10, 20]
}    


##################################
# Grid search all classifiers
# Return the best results in each
##################################

'''
Best scoring method: F1 

"f1 score can be interpreted as a weighted average of the precision and recall, 
where an F1 score reaches its best value at 1 and worst at 0."
'''

select_scoring = ['f1']
select_pca = [False, True]

for i in select_scoring:
    for k in select_pca: 
    
        print "NAIVE BAYES:"
        print "PCA: ", k
        print "Scoring: ", i
        print ''
        best_params(clf_nb, params_grid_nb, pca=k, scoring=i)
       
        print "DECISION TREE:"
        print "PCA: ", k
        print "Scoring: ", i
        print ''
        best_params(clf_dtc, params_grid_dtc, pca=k, scoring=i)
        
        print "ADABOOST:"
        print "PCA: ", k
        print "Scoring: ", i
        print ''
        best_params(clf_ada, params_grid_ada, pca=k, scoring=i)
        
        print "RANDOM FOREST:"
        print "PCA: ", k
        print "Scoring: ", i
        print ''
        best_params(clf_rf, params_grid_rf, pca=k, scoring=i)


'''

 BEST RESULTS FOR EACH CLASSIFIER:  

|**Classifier**   	        |**PCA (Y/N)** 	|**Accuracy**   	|**Precision**   	|**Recall**   	|**f1**   	|
|---	                    |---	        |---	            |---	            |---	        |---
|Gaussian NB   	            |No   	        |0.847  	        |0.412   	        |0.329          |0.366   	|
|Decision Tree              |No   	        |0.840   	        |0.340  	        |0.215 	        |0.263   	|
|Adaboost   	            |No   	        |0.824   	        |0.294   	        |0.227 	        |0.256   	|
|Random Forest 	            |No   	        |0.849   	        |0.372   	        |0.188          |0.250   	|
|.....      	            |..... 	        |.....   	        |.....   	        |.....          |.....   	|
|Gaussian NB   	            |Yes   	        |0.812  	        |0.312   	        |0.343          |0.327   	|
|Decision Tree              |Yes   	        |0.810   	        |0.275  	        |0.258 	        |0.266   	|
|Adaboost   	            |Yes   	        |0.820   	        |0.291   	        |0.245 	        |0.266  	|
|Random Forest 	            |Yes   	        |0.837   	        |0.331   	        |0.218          |0.263   	|
***

Conclusions:
- Gaussian NB was the best classifier for the problem in hand, the only to pass the minimum bar of 0.3 for both precision and recall.
- PCA preprocessing didn't influence the results significantly.
'''

###########################################################
####################### FINAL DUMP ########################
###########################################################




### Task 6: Dump your classifier, dataset, and features_list so anyone can
### check your results. You do not need to change anything below, but make sure
### that the version of poi_id.py that you submit can be run on its own and
### generates the necessary .pkl files for validating your results.


### Selected classifier: Gaussian Naive Bayes

scaling = MinMaxScaler(copy=True, feature_range=(0, 1))
kbest = SelectKBest(k=4)
classifier = GaussianNB(priors=None)


clf = Pipeline(steps=[('scaling', scaling), ('k_best', kbest), ('classifier', classifier)])
    
dump_classifier_and_data(clf, my_dataset, my_features)


