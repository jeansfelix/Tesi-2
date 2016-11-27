from hist_feature_test import *

import numpy as np
from sklearn import svm
from sklearn.metrics import accuracy_score




# randomizing positions

np.random.seed(42)
np.random.shuffle(X)

np.random.seed(42)
np.random.shuffle(y)





# creating the classifier
clf = svm.SVC()

# trainning the classifier with 9000 examples
clf.fit(X[:9000], y[:9000])


# verifying the accuracy for the model
predicted = clf.predict(X[9000:])
print accuracy_score(predicted, y[9000:])
