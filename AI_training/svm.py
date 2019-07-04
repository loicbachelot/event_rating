import numpy as np
from sklearn import svm
import matplotlib.pyplot as plt
import random
from sklearn.externals import joblib

print("loading data")
train_inputs = np.loadtxt("dataset/train_inputs.txt")
print("training inputs loaded")
train_labels = np.loadtxt("dataset/train_labels.txt")
print("training labels loaded")
test_inputs = np.loadtxt("dataset/test_inputs.txt")
print("testing inputs loaded")
test_labels = np.loadtxt("dataset/test_labels.txt")
print("testing labels loaded")


print("Creating Multiclass SVM")
clf = svm.SVR(kernel='linear', verbose=True)
print("Training SVM")
clf.fit(train_inputs, train_labels)

joblib.dump(clf, "svc_iter_infinite.pkl")
print("Testing SVM")
mean_accuracy_train = clf.score(train_inputs, train_labels)
mean_accuracy_test = clf.score(test_inputs, test_labels)

print("Mean accuracy on training data : " + str(mean_accuracy_train))
print("Mean accuracy on test data : " + str(mean_accuracy_test))
