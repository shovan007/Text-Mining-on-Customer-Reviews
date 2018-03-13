#!/usr/bin/env python2.7
#-*- coding: utf-8 -*-

import ast
# import json
import pandas as pd
import re
from wordcloud import WordCloud
from nltk.corpus import stopwords
from textblob import TextBlob
import numpy as np
import matplotlib.pyplot as plt

metadata_filename = 'C:\Users\Shovan\Desktop\Dissertation_New\Datasets\\metadata_musical_parent.json'
review_filename = 'C:\Users\Shovan\Desktop\Dissertation_New\Datasets\\reviews_musical_parent.json'

musical_instruments = ['Guitar', 'Electric Guitar', 'Piano', 'Microphone', 'Drum',
                       'Violin', 'Mixer', 'Ukulele', 'Saxophone', 'Trumpet',
                       'Acoustic Guitar', 'Accordion', 'Cello', 'Clarinet',
                       'Flute', 'Bass Guitar', 'Classical Guitar', 'Xylophone',
                       'Harmonica', 'Trombone', 'Oboe', 'Cajon', 'Banjo', 'Mandolin',
                       'Bassoon', 'Viola', 'Double Bass', 'Synthesizer', 'Bagpipes',
                       'Harp', 'Tuba', 'Ocarina', 'Bell', 'Theremin', 'Bongo',
                       'Tambourine', 'Sitar', 'Lute', 'Marimba', 'Melodica',
                       'Lyre', 'Oud', 'Hang', 'Keyboard']


def read_metadata(filename=""):
    f = open(filename)
    metadata = []
    amazon_md_df = pd.DataFrame()
    for row in f.readlines():
        metadata.append(ast.literal_eval(row))

    amazon_md_df['product_id'] = map(lambda data: data.get('asin', ''), metadata)
    amazon_md_df['Description'] = map(lambda data: data.get('title', ''), metadata)
    amazon_md_df['Price'] = map(lambda data: data.get('price', ''), metadata)
    amazon_md_df['Manufacturer'] = map(lambda data: data.get('brand', ''), metadata)
    return amazon_md_df


def preprocess_metadata(amazon_md_df):

    for i in amazon_md_df.columns:
        amazon_md_df[i][amazon_md_df[i].apply(lambda i: True if re.search('^\s*$', str(i)) else False)]=float('nan')

    amazon_md_df_updated = pd.DataFrame()
    amazon_md_df_updated = amazon_md_df.dropna(how='any')

    # print amazon_md_df_updated

    music_instruments_set = set(musical_instruments + [''])
    music_instruments_set = map(str.lower, music_instruments_set)

    empty_list = []

    for index, rows in amazon_md_df_updated.iterrows():
        empty_set = set([])
        newline = rows['Description'].lower().split()

        for word in newline:
            if word.endswith('s'):
                # Replace with Snowball Stemmer
                new_word = re.sub('s$|es$', '', word)
                empty_list.append(new_word)
            else:
                empty_list.append(word)

        # print empty_list
        new_string = ' '.join(word for word in empty_list)
        amazon_md_df_updated.set_value(index, 'Description', new_string)

        updated_newline = new_string.split()
        abc = set(music_instruments_set).intersection(updated_newline)

        empty_set = abc.intersection(music_instruments_set)
        empty_list = list(empty_set)

        if len(empty_list) == 0:
            amazon_md_df_updated.set_value(index, 'Description', None)
        else:
            amazon_md_df_updated.set_value(index, 'Description', empty_list[0])

    return amazon_md_df_updated


def read_preprocess_review(filename=""):
    g = open(filename)
    amazon_review_df = pd.DataFrame()
    review_data = []
    for line in g.readlines():
        review_data.append(ast.literal_eval(line))

    amazon_review_df['product_id'] = map(lambda data: data.get('asin', ''), review_data)
    amazon_review_df['Reveiwer ID'] = map(lambda data: data.get('reviewerID', ''), review_data)
    amazon_review_df['Reviewer Comments'] = map(lambda data: data.get('reviewText', ''), review_data)
    amazon_review_df['Overall Rating'] = map(lambda data: data.get('overall', ''), review_data)
    amazon_review_df['Overall Summary'] = map(lambda data: data.get('summary', ''), review_data)
    amazon_review_df['Reviewer Name'] = map(lambda data: data.get('reviewerName', ''), review_data)
    
    sentiments_list = []
    for d, rows in amazon_review_df.iterrows():
        row = rows['Reviewer Comments']
        testimonial = TextBlob(row)
        sentiment_polarity = testimonial.sentiment.polarity
        sentiments_list.append(sentiment_polarity)

    # print sentiments_list

    amazon_review_df['Sentiments Polarity'] = pd.DataFrame({'Sentiments Polarity': sentiments_list})

    # print amazon_review_df
    return amazon_review_df


def filter_by_brand(preprocessed_metadata, brandname):
    if len(brandname):
        filtered_by_brand = preprocessed_metadata[preprocessed_metadata['Manufacturer'].str.contains(brandname, case=False)]
        return filtered_by_brand
    else:
        return preprocessed_metadata


def filter_by_price(preprocessed_metadata, minprice, maxprice):
    if minprice != maxprice:
        filtered_by_price = preprocessed_metadata[preprocessed_metadata['Price'].between(minprice, maxprice, inclusive=True)]
        return filtered_by_price
    else:
        return preprocessed_metadata


def filter_by_productname(preprocessed_metadata, productname):
    if len(productname):
        filtered_by_productname = preprocessed_metadata[preprocessed_metadata['Description'].str.contains(productname, na=False, case=False)]
        return filtered_by_productname
    else:
        return preprocessed_metadata


def filter_by_keyword(metadata, review_data, keyword):
    if len(keyword):
        review_ids = review_data[review_data['Reviewer Comments'].str.contains(keyword)]['product_id']
        filtered = metadata[metadata['product_id'].isin(review_ids)]
        return filtered
    else:
        return metadata


def remove_stopwords(text):
    text = re.sub('\W+', ' ', text)
    text = re.sub('\s+\S\s+', ' ', text)
    text = re.sub(' +', ' ', text)
    words = text.split(" ")
    processed_words = ' '.join([word for word in words if word not in (stopwords.words('english'))])
    # print processed_words
    return processed_words


def get_filtered_reviews(df, id_list):
    filtered_reviews = df[df['product_id'].isin(id_list)]
    # filter_count = filtered_reviews.shape[0]
    reviews = []
    rating = 0
    for index, rows in filtered_reviews.iterrows():
        reviews.append(rows['Reviewer Comments'].lower())
        rating += rows['Overall Rating']

    # print "Total number of reviews of the instrument",len(reviews)
    # print "Average of all the overall ratings",rating/filter_count

    total_reviews = ' '.join(reviews)

    music_instruments_list = musical_instruments + ['']
    music_instruments_list = map(str.lower, music_instruments_list)

    for word in music_instruments_list:
        # print word
        if word in total_reviews:
            total_reviews = re.sub(word, '', total_reviews)

    # print total_reviews,"total_reviews"
    total_reviews = remove_stopwords(total_reviews)
    # print total_reviews, "stopwords"
    return total_reviews


def wordcloud(dataframe, dataframereview):
    id_list = []
    for index, rows in dataframe.iterrows():
        id_list.append(rows["product_id"])
    # print(id_list)
    text = get_filtered_reviews(dataframereview, id_list)
    # print(text)
    # Generate a word cloud image
    wordcloud = WordCloud(background_color="white").generate(text)

    # Display the generated image:
    # the matplotlib way:

    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.savefig('image2.png')

    # lower max_font_size
    wordcloud = WordCloud(max_font_size=40, background_color="white").generate(text)
    plt.figure()
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.savefig('image1.png')
    plt.show()


def main():
    brandname = ""
    minprice = 0
    maxprice = 0
    productname = "guitar"
    metadata_df = read_metadata(metadata_filename)
    review_df = read_preprocess_review(review_filename)
    preprocessed_metadata = preprocess_metadata(metadata_df)
    brand_filter = filter_by_brand(preprocessed_metadata, brandname)
    price_filter = filter_by_price(brand_filter, minprice, maxprice)
    productname_filter = filter_by_productname(price_filter, productname)

    # wordcloud(dataframe=brand_filter, dataframereview=review_df)
    # wordcloud(dataframe=price_filter, dataframereview=review_df)
    wordcloud(dataframe=productname_filter, dataframereview=review_df)


if __name__ == '__main__':
    main()
