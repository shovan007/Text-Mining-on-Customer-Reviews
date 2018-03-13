import io
import template
import numpy as np
from wordcloud import WordCloud


def wordcloud_qt(dataframe, dataframereview):
    id_list = []
    for index, rows in dataframe.iterrows():
        id_list.append(rows["product_id"])
    text = template.get_filtered_reviews(dataframereview, id_list)
    wordcloud = WordCloud(max_font_size=40, background_color="white").generate(text)
    image_io = io.BytesIO()
    wordcloud.to_image().save(image_io, 'PNG')
    return image_io.getvalue()


def wordcloud_keyword(dataframe):
    words = []
    for index, cols in dataframe.iterrows():
        if cols['Description'] is not None:
            words.append(cols['Description'].strip())
    text = ' '.join(words)
    wordcloud = WordCloud(max_font_size=40, background_color="white").generate(text)
    image_io = io.BytesIO()
    wordcloud.to_image().save(image_io, 'PNG')
    return image_io.getvalue()


def wordcloud_people(s_min, s_max, dataframe, dataframereview):
    id_list = []
    for index, rows in dataframe.iterrows():
        id_list.append(rows["product_id"])

    filtered_reviews = dataframereview[dataframereview['product_id'].isin(id_list)]

    words = []
    for index, cols in filtered_reviews.iterrows():
        spol = cols['Sentiments Polarity']
        if spol >= s_min and spol <= s_max or s_min == s_max:
            if cols['Reviewer Name'] is not None:
                words.append(cols['Reviewer Name'].strip())
    text = ' '.join(words)
    wordcloud = WordCloud(max_font_size=40, background_color="white").generate(text)
    image_io = io.BytesIO()
    wordcloud.to_image().save(image_io, 'PNG')
    return image_io.getvalue()


def histogram_qt(s_min, s_max, dataframe, dataframereview):
    import matplotlib.pyplot as plt

    id_list = []
    for index, rows in dataframe.iterrows():
        id_list.append(rows["product_id"])

    filtered_reviews = dataframereview[dataframereview['product_id'].isin(id_list)]

    positive = 0
    negative = 0
    neutral = 0
    for d, cols in filtered_reviews.iterrows():
        value = cols['Sentiments Polarity']
        if value >= s_min and value <= s_max or s_min == s_max:
            if value > 0.2 and value <= 1.0:
                positive += 1
            elif value < -0.2 and value >= -1.0:
                negative += 1
            else:
                neutral += 1

    objects = ('Negative', 'Neutral', 'Positive')
    y_pos = np.arange(len(objects))
    polarities = [negative, neutral, positive]
    plt.bar(y_pos, polarities, align='center', alpha=0.5, color='red')
    plt.xticks(y_pos, objects)
    image_io = io.BytesIO()
    plt.savefig(image_io, format='png')
    plt.clf()
    return image_io.getvalue()
