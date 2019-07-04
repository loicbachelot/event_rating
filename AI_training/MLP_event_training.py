import numpy as np
from sklearn.neural_network import MLPClassifier
import matplotlib.pyplot as plt
import random
from sklearn.externals import joblib


hidden_layer_sizes_param = [
    (20,10),
    (15, 5),
    (18,),
    (20, 10, 5)
]

print("loading data")
train_inputs = np.loadtxt("dataset/train_inputs_events.txt")
print("training inputs loaded")
train_labels = np.loadtxt("dataset/train_labels_events.txt")
print("training labels loaded")
test_inputs = np.loadtxt("dataset/test_inputs_events.txt")
print("testing inputs loaded")
test_labels = np.loadtxt("dataset/test_labels_events.txt")
print("testing labels loaded")

counter = 0

for i in hidden_layer_sizes_param :
    counter+=1
    mlp = MLPClassifier(hidden_layer_sizes=i)
    mlp.fit(train_inputs, train_labels)
    score_train = mlp.score(train_inputs, train_labels)
    score_test = mlp.score(test_inputs, test_labels)
    print("train_score = " + str(score_train))
    print("test_score = " + str(score_test))
    joblib.dump(mlp, "AI/mlp_events_"+str(counter)+".pkl")
