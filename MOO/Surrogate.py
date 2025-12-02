"""
libraries sklearns, torch, optuna ...

load data
Split into 80-20 train-test using stratification (for classification)
k-fold cross validation or leave one out cross validation 
Normalise or ---standardise----


40 classifiers of sckiti-learn library. Thus, the remaining 23 classifiers have been used in the framework.
"""

from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.inspection import DecisionBoundaryDisplay
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier