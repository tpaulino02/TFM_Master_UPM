import luigi
from luigi.contrib.esindex import CopyToIndex
from soneti_tasks.SenpyAnalysis import SenpyAnalysis
from soneti_tasks.GSICrawlerScraper import GSICrawlerScraper
from soneti_tasks.CopyToFuseki import CopyToFuseki

from tasks.scrapy import retrieveDataFromGSICrawler
from tasks.ideology import annotateIdeology
from tasks.language import detectLanguage
from tasks.preprocess import preprocessText
from tasks.geo import annotateGeolocation
from tasks.sentiment import sentimentAnalysis
from tasks.fuseki import removeNonSemanticFields, sendDataToFuseki

import json
import jsonlines
from elasticsearch.helpers import bulk
import os
#import tweepy
from snscrape.modules import twitter




###############
# SCRAPY TASK #
###############

class ScrapyTask(GSICrawlerScraper):

    source = luigi.Parameter()
    gsicrawler_params = luigi.DictParameter('{}')
    before = luigi.Parameter()
    after = luigi.Parameter()
    host = os.environ['GSICRAWLER_URL']

    def run(self):
        """
        Run analysis task 
        """
        with self.output().open('w') as outfile:
            writer = jsonlines.Writer(outfile)

            tweet_list = []
            tweet_list_brick = []

            u = twitter.TwitterSearchScraper("🧱")
            for tweet in u.get_items():
                if (len(tweet_list) < 100000):
                    tweet_list.append(tweet)
                else:
                    break
            for tweet in tweet_list:
                if (tweet.lang != 'it'):
                    continue
                else:   
                    mytweet = {}    
                    mytweet["@type"] =  ["schema:BlogPosting", ]
                    mytweet["@id"] = id(tweet.id)
                    mytweet["schema:about"] = 'mattonisti-user'
                    mytweet["schema:search"] = 'mattonisti-user'
                    mytweet["schema:articleBody"] = tweet.content
                    mytweet["schema:headline"] = tweet.content
                    mytweet["schema:creator"] = tweet.user.username
                    mytweet["schema:author"] = 'twitter'
                    mytweet["schema:inLanguage"] = tweet.lang
                
                    if tweet.hashtags is None:
                        mytweet["schema:keywords"] = []
                        mytweet["schema:keywords"].append('mattonisti-user')
                    else:
                        mytweet["schema:keywords"] = tweet.hashtags
                        mytweet["schema:keywords"].append('mattonisti-user')
                    mytweet["schema:datePublished"] = tweet.date.strftime('%Y-%m-%dT%H:%M:%SZ')
                    
                    if tweet.place:
                        mytweet["schema:locationCreated"] = tweet.place.fullName

                    if tweet.coordinates:
                        mytweet['location'] = { 
                            'lat': tweet.coordinates.latitude,
                            'lon': tweet.coordinates.longitude
                        }

                    mytweet["year"] = tweet.date.strftime('%Y')
                
                    
                    tweet_list_brick.append(mytweet)

            writer.write_all(tweet_list_brick)
            

    def output(self):
        return luigi.LocalTarget(path='/tmp/participation_scrapy_{}.json'.format(hash(str(self.to_str_params()))))


############################
# IDEOLOGY ANNOTATION TASK #
############################

class IdeologyAnnotationTask(luigi.Task):

    source = luigi.Parameter()
    gsicrawler_params = luigi.DictParameter('{}')
    before = luigi.Parameter()
    after = luigi.Parameter()
    host = os.environ['GSICRAWLER_URL']

    def requires(self):
        return ScrapyTask(
            self.source,
            self.gsicrawler_params,
            self.before,
            self.after
        )

    def run(self):
        """
        Run analysis task 
        """
        with self.input().open('r') as infile:
            with self.output().open('w') as outfile:
                
                writer = jsonlines.Writer(outfile)
                reader = jsonlines.Reader(infile)

                for i, line in enumerate(reader):

                    # Annotate ideology and narrative for Twitter
                    data = annotateIdeology(line)
                    if data is None:
                        continue
                    # Displays a progress bar in the scheduler UI
                    self.set_status_message("Progress: %d" % i)

                    # Write data to Luigi Target
                    writer.write(data)

    def output(self):
        return luigi.LocalTarget(path='/tmp/participation_ideology_{}.json'.format(hash(str(self.to_str_params()))))


###########################
# LANGUAGE DETECTION TASK #
###########################

class LanguageDetectionTask(luigi.Task):

    ideology = luigi.Parameter()
    source = luigi.Parameter()
    gsicrawler_params = luigi.DictParameter('{}')
    before = luigi.Parameter()
    after = luigi.Parameter()

    def output(self):
        return luigi.LocalTarget(path='/tmp/participation_lang_detection_{}.json'.format(hash(str(self.to_str_params()))))

    def requires(self):

        # Annotate ideology if specified by the command
        if self.ideology:
            return IdeologyAnnotationTask(
                self.source,
                self.gsicrawler_params,
                self.before,
                self.after
            )
        else:
            return ScrapyTask(
                self.source,
                self.gsicrawler_params,
                self.before,
                self.after
            )

    def run(self):
        with self.input().open('r') as infile:
            with self.output().open('w') as outfile:

                writer = jsonlines.Writer(outfile)
                reader = jsonlines.Reader(infile)

                for i, line in enumerate(reader):

                    # Detect language using NLTK    
                    data = detectLanguage(line)

                    # Displays a progress bar in the scheduler UI
                    self.set_status_message("Progress: %d" % i)

                    # Write data to Luigi Target
                    if data is not None:
                        writer.write(data)


######################
# PREPROCESSING TASK #
######################

class PreprocessingTask(luigi.Task):

    ideology = luigi.Parameter()
    source = luigi.Parameter()
    gsicrawler_params = luigi.DictParameter('{}')
    before = luigi.Parameter()
    after = luigi.Parameter()

    def output(self):
        return luigi.LocalTarget(path='/tmp/participation_preprocess_{}.json'.format(hash(str(self.to_str_params()))))
    def requires(self):
        return LanguageDetectionTask(
            self.ideology,
            self.source,
            self.gsicrawler_params,
            self.before,
            self.after
        )

    def run(self):
        with self.input().open('r') as infile:
            with self.output().open('w') as outfile:

                writer = jsonlines.Writer(outfile)
                reader = jsonlines.Reader(infile)

                for i, line in enumerate(reader):
                
                    # Uses different preprocessor depending on the source
                    data = preprocessText(line, self.source)

                    # Displays a progress bar in the scheduler UI
                    self.set_status_message("Progress: %d" % i)

                    # Write data to Luigi Target
                    writer.write(data)



########################
# GEO ANNOTATIONS TASK #
########################

class GeoTask(luigi.Task):

    ideology = luigi.Parameter()
    geo = luigi.Parameter()
    source = luigi.Parameter()
    gsicrawler_params = luigi.DictParameter('{}')
    before = luigi.Parameter()
    after = luigi.Parameter()

    def requires(self):
        return PreprocessingTask(
            self.ideology,
            self.source,
            self.gsicrawler_params,
            self.before,
            self.after
        )
        
    def run(self):
        """
        Run analysis task 
        """
        with self.input().open('r') as infile:
            with self.output().open('w') as outfile:

                writer = jsonlines.Writer(outfile)
                reader = jsonlines.Reader(infile)

                for i, line in enumerate(reader):

                    # Annotate geolocation
                    data = annotateGeolocation(line)

                    # Displays a progress bar in the scheduler UI
                    self.set_status_message("Progress: %d" % i)

                    # Write data to Luigi Target
                    writer.write(data)


    def output(self):
        return luigi.LocalTarget(path='/tmp/participation_geo_{}.json'.format(hash(str(self.to_str_params()))))

######################
# LIWC ANALYSIS TASK #
######################

class LIWCTask(SenpyAnalysis):

    algorithm = luigi.Parameter()
    ideology = luigi.Parameter()
    geo = luigi.Parameter()
    source = luigi.Parameter()
    gsicrawler_params = luigi.DictParameter('{}')
    before = luigi.Parameter()
    after = luigi.Parameter()
    host = os.environ['SENPY_URL']

    def requires(self):

        # Annotate geolocalization if specified by the command
        if self.geo:
            return GeoTask(
                self.ideology,
                self.geo,
                self.source,
                self.gsicrawler_params,
                self.before,
                self.after
            )
        else:
            return PreprocessingTask(
                self.ideology,
                self.source,
                self.gsicrawler_params,
                self.before,
                self.after
            )

    def run(self):
        """
        Run analysis task 
        """
        with self.input().open('r') as infile:
            with self.output().open('w') as outfile:

                writer = jsonlines.Writer(outfile)
                reader = jsonlines.Reader(infile)

                for i, line in enumerate(reader):
                
                    # Sentiment analysis with Senpy
                    data = sentimentAnalysis(line, self.host, self.algorithm, {
                        'apiKey': self.apiKey,
                        'algo': self.algorithm,
                        "i": line["schema:articleBody"]
                    })

                    # Displays a progress bar in the scheduler UI
                    self.set_status_message("Progress: %d" % i)

                    # Write data to Luigi Target
                    writer.write(data)


    def output(self):
        return luigi.LocalTarget(path='/tmp/participation_liwc_{}.json'.format(hash(str(self.to_str_params()))))


######################
# MFT ANALYSIS TASK #
######################

class SentimentAnalysisTask(SenpyAnalysis):

    algorithms = luigi.ListParameter()
    ideology = luigi.Parameter()
    geo = luigi.Parameter()
    source = luigi.Parameter()
    gsicrawler_params = luigi.DictParameter('{}')
    before = luigi.Parameter()
    after = luigi.Parameter()
    host = os.environ['SENPY_URL']

    def requires(self):

        if len(self.algorithms) > 1:
            return SentimentAnalysisTask(
                self.algorithms[:-1],
                self.ideology,
                self.geo,
                self.source,
                self.gsicrawler_params,
                self.before,
                self.after
            )
        else:
            # Annotate geolocalization if specified by the command
            if self.geo:
                return GeoTask(
                    self.ideology,
                    self.geo,
                    self.source,
                    self.gsicrawler_params,
                    self.before,
                    self.after
                )
            else:
                return PreprocessingTask(
                    self.ideology,
                    self.source,
                    self.gsicrawler_params,
                    self.before,
                    self.after
                )

    def run(self):
        """
        Run analysis task 
        """
        with self.input().open('r') as infile:
            with self.output().open('w') as outfile:
                
                writer = jsonlines.Writer(outfile)
                reader = jsonlines.Reader(infile)

                for i, line in enumerate(reader):
                
                    # Sentiment analysis with Senpy
                    data = sentimentAnalysis(line, self.host, self.algorithms[-1], {
                        'apiKey': self.apiKey,
                        'algo': self.algorithms[-1],
                        "i": line["schema:articleBody"]
                    })

                    # Displays a progress bar in the scheduler UI
                    self.set_status_message("Progress: %d" % i)

                    # Write data to Luigi Target
                    writer.write(data)

    def output(self):
        return luigi.LocalTarget(path='/tmp/participation_mft_{}.json'.format(hash(str(self.to_str_params()))))


###############
# FUSEKI TASK #
###############

class FusekiTask(CopyToFuseki):
    
    algorithms = luigi.ListParameter()
    ideology = luigi.Parameter()
    geo = luigi.Parameter()
    source = luigi.Parameter()
    gsicrawler_params = luigi.DictParameter('{}')
    before = luigi.Parameter()
    after = luigi.Parameter()
    host = os.environ['FUSEKI_URL']
    port = os.environ['FUSEKI_PORT']

    def requires(self):
        return SentimentAnalysisTask(
            self.algorithms,
            self.ideology,
            self.geo,
            self.source,
            self.gsicrawler_params,
            self.before,
            self.after
        )
        
    def output(self):
        return luigi.LocalTarget(path='/tmp/participation_n3_{}.json'.format(hash(str(self.to_str_params()))))

    def run(self):
        """
        Run indexing to Fuseki task 
        """
        with self.input().open('r') as infile:
            with self.output().open('w') as outfile:

                writer = jsonlines.Writer(outfile)
                reader = jsonlines.Reader(infile)

                data = []
                for i, line in enumerate(reader):
                
                    # Only send semantically annotated fields to Fuseki
                    data.append(removeNonSemanticFields(line))

                    # Displays a progress bar in the scheduler UI
                    self.set_status_message("Progress: %d" % i)

                self.set_status_message("JSON created")
                
                sendDataToFuseki(json.dumps(data), self.host, self.port, self.dataset)

                self.set_status_message("Data sent to fuseki")
                writer.write(data)


######################
# ELASTICSEARCH TASK #
######################

class ElasticsearchTask(CopyToIndex):
    
    doc_type = luigi.Parameter(default='_doc')
    index = luigi.Parameter(default='participation')
    algorithms = luigi.ListParameter()
    ideology = luigi.Parameter()
    geo = luigi.Parameter()
    source = luigi.Parameter()
    gsicrawler_params = luigi.DictParameter('{}')
    before = luigi.Parameter()
    after = luigi.Parameter()
    host = os.environ['ES_URL']
    port = os.environ['ES_PORT']
    http_auth = (os.environ['ES_USER'],os.environ['ES_PASSWORD'])
    timeout = 100

    def requires(self):
        return SentimentAnalysisTask(
            self.algorithms,
            self.ideology,
            self.geo,
            self.source,
            self.gsicrawler_params,
            self.before,
            self.after
        )



class StoreTask(luigi.Task):

    doc_type = luigi.Parameter(default='_doc')
    index = luigi.Parameter(default='participation')
    algorithms = luigi.ListParameter()
    ideology = luigi.BoolParameter()
    geo = luigi.BoolParameter()
    source = luigi.Parameter()
    gsicrawler_params = luigi.DictParameter('{}')
    before = luigi.Parameter(None)
    after = luigi.Parameter(None)


    def requires(self):
        yield FusekiTask(
            self.algorithms,
            self.ideology,
            self.geo,
            self.source,
            self.gsicrawler_params,
            self.before,
            self.after
        )
        yield ElasticsearchTask(
            self.doc_type,
            self.index,
            self.algorithms,
            self.ideology,
            self.geo,
            self.source,
            self.gsicrawler_params,
            self.before,
            self.after
        )
