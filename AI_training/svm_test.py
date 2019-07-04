import numpy as np
from sklearn import svm
import matplotlib.pyplot as plt
import random
from sklearn.externals import joblib
import time

print("loading data")
train_inputs = np.loadtxt("train_inputs.txt")
print("training inputs loaded")
train_labels = np.loadtxt("train_labels.txt")
print("training labels loaded")
test_inputs = np.loadtxt("test_inputs.txt")
print("testing inputs loaded")
test_labels = np.loadtxt("test_labels.txt")
print("testing labels loaded")


print("Creating Multiclass SVM")
clf = joblib.load("svc_iter_infinite.pkl")

print("Testing SVM on training data")
begin = time.time()
results = clf.predict(train_inputs)
end = time.time()

t = end - begin

counter = 0.
for i in range(len(results)) :
    if results[i] == train_labels[i] :
        counter = counter + 1

precision = (counter / float(len(train_inputs))) * 100

print("precision on training data : " + str(precision) + "%")
print("Average prediction time : "  + str(t / len(train_inputs)) + "s")

print("Testing SVM on test data")
begin = time.time()
results = clf.predict(test_inputs);
end = time.time()

t = end - begin

counter = 0.
for i in range(len(results)) :
    if results[i] == test_labels[i] :
        counter = counter + 1

precision = (counter / float(len(test_inputs))) * 100

print("precision on test data : " + str(precision) + "%")
print("Average prediction time : "  + str(t / len(test_inputs)) + "s")
