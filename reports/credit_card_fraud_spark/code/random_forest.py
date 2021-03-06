import sys
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.mllib.linalg import Vectors
import pandas as pd
import csv
from pyspark.ml.classification import LogisticRegression
from pyspark.mllib.classification import LogisticRegressionWithLBFGS, LogisticRegressionModel
from pyspark.mllib.evaluation import BinaryClassificationMetrics
from pyspark.mllib.regression import LabeledPoint
from pyspark.mllib.util import MLUtils
from pyspark.mllib.regression import LabeledPoint, LinearRegressionWithSGD, LinearRegressionModel
from pyspark.mllib.evaluation import MulticlassMetrics
from pyspark.mllib.tree import DecisionTree, DecisionTreeModel
from pyspark.mllib.util import MLUtils
#Run in pyspark, results are printed

# Remove the first line from the csv file
def clean(x):
    if (x[29] != "Amount"):
        return x

#Turn the data into a labeled point using 30 dimensions
def normalize(x):
    return LabeledPoint(float(x[30]), [float(x[0]), float(x[29])/ 25691.16, float(x[1])/2.45492999121 ,  float(x[2])/22.0577289905 , float(x[3])/9.38255843282 , float(x[4])/16.8753440336  , float(x[5])/34.8016658767 , float(x[6])/73.301625546 , float(x[7])/120.589493945 , float(x[8])/20.0072083651  ,float(x[9])/15.5949946071 ,float(x[10])/23.7451361206545 , float(x[11])/12.018913181619899  , float(x[12])/7.8483920756445995 , float(x[13])/7.1268829585937592 , float(x[14])/10.526766051784699 , float(x[15])/8.8777415977427694  ,float(x[16])/17.315111517627802 , float(x[17])/9.2535262504728504 , float(x[18])/5.0410691854118399  , float(x[19])/5.5919714273355803 , float(x[20])/39.420904248219898 , float(x[21])/27.202839157315399 , float(x[22])/10.503090089945401  ,float(x[23])/22.528411689774899, float(x[24])/4.5845491368981701 , float(x[25])/7.5195886787091597  , float(x[26])/3.5173456116237998 , float(x[27])/31.612198106136304 ,   float(x[28])/33.847807818883098 ])

# Load and parse the data
rdd = sc.textFile("creditcard.csv")
data = rdd.mapPartitions(lambda x: csv.reader(x))
data = data.map( lambda x: clean(x) )
data = data.filter(lambda x: x != None)
data = data.map(normalize)
data= sc.parallelize(data.collect())

def pr(arr):
    rocAvg = 0
    prAvg = 0
    print("\tArea Under ROC\t\tArea Under PR")
    for i in arr:
        print("\t" + i)
        a = i.split('\t')
        rocAvg += float(a[0])
        prAvg += float(a[1])
    print("AVG\t" + str(rocAvg/len(arr)) + "\t" + str(prAvg/len(arr)))

training, test = data.randomSplit([0.8, 0.2])
training.cache()
#this is the stuff you need to run many times
results = []
for i in range(5):
    # Run training algorithm to build the model
    model = RandomForest.trainClassifier(training, numClasses=2, categoricalFeaturesInfo={},
                                        numTrees=15, featureSubsetStrategy="auto",
                                        impurity='gini', maxDepth=5, maxBins=50)    # Compute raw scores on the test set
    predictions = model.predict(test.map(lambda x: x.features))
    labelsAndPredictions = test.map(lambda lp: lp.label).zip(predictions)    # Instantiate metrics object
    metrics = BinaryClassificationMetrics(labelsAndPredictions)
    # Area under ROC curve and precision-recall curve
    results.append(str(metrics.areaUnderROC) + "\t" + str(metrics.areaUnderPR))
