import numpy as np
from sklearn import svm
import matplotlib.pyplot as plt
import random
from sklearn.externals import joblib
import time

print("loading data")
train_inputs = np.loadtxt("dataset/train_inputs2.txt")
print("training inputs loaded")
train_labels = np.loadtxt("dataset/train_labels2.txt")
print("training labels loaded")
test_inputs = np.loadtxt("dataset/test_inputs2.txt")
print("testing inputs loaded")
test_labels = np.loadtxt("dataset/test_labels2.txt")
print("testing labels loaded")


print("Creating MLP")
clf = joblib.load("AI/mlp_events_4_v2.pkl")

print("Testing MLP on training data\n\n")
begin = time.time()
results = clf.predict(train_inputs)
end = time.time()

t = end - begin

counter = 0.
for i in range(len(results)) :
    if results[i] == train_labels[i] :
        counter = counter + 1
    if results[i] == 1:
        print("event detected")

precision = (counter / float(len(train_inputs))) * 100

print("precision on training data : " + str(precision) + "%")
print("Average prediction time : "  + str(t / len(train_inputs)) + "s")

print("Testing MLP on test data\n\n")
begin = time.time()
results = clf.predict(test_inputs)
end = time.time()

t = end - begin

counter = 0.
for i in range(len(results)) :
    if results[i] == test_labels[i] :
        counter = counter + 1
    if results[i] == 1:
        print("event detected")

precision = (counter / float(len(test_inputs))) * 100

print("precision on test data : " + str(precision) + "%")
print("Average prediction time : "  + str(t / len(test_inputs)) + "s")