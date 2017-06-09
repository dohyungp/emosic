from konlpy.tag import Twitter

from pyspark import keyword_only
from pyspark.ml import Transformer
from pyspark.ml.param.shared import HasInputCol, HasOutputCol, Param
from pyspark.sql.functions import udf
from pyspark.sql.types import ArrayType, StringType


class KonlpTokenizer(Transformer, HasInputCol, HasOutputCol):

    @keyword_only
    def __init__(self, inputCol=None, outputCol=None, stopwords=None):
        super(KonlpTokenizer, self).__init__()
        self.stopwords = Param(self, "stopwords", "")
        self._setDefault(stopwords=set())
        kwargs = self.__init__._input_kwargs
        self.setParams(**kwargs)

    @keyword_only
    def setParams(self, inputCol=None, outputCol=None, stopwords=None):
        kwargs = self.setParams._input_kwargs
        return self._set(**kwargs)

    def setStopwords(self, value):
        self._paramMap[self.stopwords] = value
        return self

    def getStopwords(self):
        return self.getOrDefault(self.stopwords)

    def _transform(self, dataset):
        # stopwords = self.getStopwords()

        def f(s):
            twitter = Twitter()
            tokens = twitter.pos(s)
            stopwords = ["Noun", "Verb", "Adjective", "Foreign"]
            return [t[0] for t in tokens if t[1] in stopwords and len(t[0]) > 1]

        t = ArrayType(StringType())
        out_col = self.getOutputCol()
        in_col = dataset[self.getInputCol()]
        return dataset.withColumn(out_col, udf(f, t)(in_col))