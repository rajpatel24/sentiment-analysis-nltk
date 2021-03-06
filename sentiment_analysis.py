import random
import re, string

from nltk import FreqDist, word_tokenize
from nltk.tag import pos_tag
from nltk.corpus import twitter_samples
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords

from nltk import classify
from nltk import NaiveBayesClassifier


# removing the noise (hyperlinks, @, punctuation & special characters) and normalizing the data
def remove_noise(tweet_tokens, stop_words=()):
    cleaned_tokens = []

    for token, tag in pos_tag(tweet_tokens):
        token = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|'\
                       '(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', token)

        token = re.sub("(@[A-Za-z0-9_]+)", "", token)

        if tag.startswith("NN"):
            pos = 'n'
        elif tag.startswith('VB'):
            pos = 'v'
        else:
            pos = 'a'

        lemmatizer = WordNetLemmatizer()
        token = lemmatizer.lemmatize(token, pos)

        if len(token) > 0 and token not in string.punctuation and token.lower() not in stop_words:
            cleaned_tokens.append(token.lower())
    return cleaned_tokens


# join the tweet tokens
def get_all_words(cleaned_tokens_list):
    for tokens in cleaned_tokens_list:
        for token in tokens:
            yield token


# convert the tweets from a list of cleaned tokens to dictionaries with keys as the tokens and True as values
def get_tweets_for_model(cleaned_tokens_list):
    for tweet_tokens in cleaned_tokens_list:
        yield dict([token, True] for token in tweet_tokens)


def sentiment_analysis():
    """
    Main logic for sentiment analysis
    """
    stop_words = stopwords.words('english')

    positive_tweet_tokens = twitter_samples.tokenized("positive_tweets.json")
    negative_tweet_tokens = twitter_samples.tokenized("negative_tweets.json")

    positive_cleaned_tokens_list = []
    negative_cleaned_tokens_list = []

    for tokens in positive_tweet_tokens:
        positive_cleaned_tokens_list.append(remove_noise(tokens, stop_words))

    for tokens in negative_tweet_tokens:
        negative_cleaned_tokens_list.append(remove_noise(tokens, stop_words))

    all_pos_words = get_all_words(positive_cleaned_tokens_list)

    freq_dist_pos = FreqDist(all_pos_words)

    positive_tokens_for_model = get_tweets_for_model(positive_cleaned_tokens_list)
    negative_tokens_for_model = get_tweets_for_model(negative_cleaned_tokens_list)

    positive_dataset = [(tweet_dict, "Positive") for tweet_dict in positive_tokens_for_model]
    negative_dataset = [(tweet_dict, "Negative") for tweet_dict in negative_tokens_for_model]

    dataset = positive_dataset + negative_dataset

    random.shuffle(dataset)

    train_data = dataset[:7000]
    test_data = dataset[7000:]

    classifier = NaiveBayesClassifier.train(train_data)

    print("\n\n> Accuracy is:", classify.accuracy(classifier, test_data)*100)

    # ------------------------------------ Sample Data Prediction ----------------------------------

    sample_tweet1 = "I ordered just once from TerribleCo, they screwed up, never used the app again."
    sample_tokens = remove_noise(word_tokenize(sample_tweet1))
    print("\n\n> Result 1: ", classifier.classify(dict([token, True] for token in sample_tokens)))

    sample_tweet2 = 'Congrats #SportStar on your 7th best goal from last season winning goal of the year :) #Baller #Topbin #oneofmanyworldies'
    sample_tokens = remove_noise(word_tokenize(sample_tweet2))
    print("\n\n> Result 2: ", classifier.classify(dict([token, True] for token in sample_tokens)))


if __name__ == '__main__':
    sentiment_analysis()
