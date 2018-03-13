#!/usr/bin/env python2.7
#-*- coding: utf-8 -*-

import os
import sys
import template
import template_qt
import gridfs
import traceback
from PyQt5 import QtGui, QtWidgets
from PyQt5 import uic
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

MONGO_DBNAME = 'saved_results'
FORMS_FILES = ['gui.ui', 'saved_results.ui']

for form_file in FORMS_FILES:
    py_form_filename = 'ui_%s.py' % form_file.replace('.ui', '')
    py_form_filepath = os.path.join('forms', py_form_filename)
    ui_form_filepath = os.path.join('forms', form_file)
    if not os.path.exists(py_form_filepath) or \
       os.path.getctime(py_form_filepath) < os.path.getctime(ui_form_filepath):
        with open(py_form_filepath, 'w+') as py_form_file:
            print 'Compiling UI %s' % form_file
            uic.compileUi(ui_form_filepath, py_form_file)

from forms.ui_gui import Ui_MainWindow
from forms.ui_saved_results import Ui_SavedResults


class SavedResults(QtWidgets.QDialog):
    def __init__(self):
        super(SavedResults, self).__init__()
        self.ui = Ui_SavedResults()
        self.ui.setupUi(self)
        self.selected_item = None
        self.db = MongoClient()[MONGO_DBNAME]
        self.ui.results.itemActivated.connect(self.return_item)

    @classmethod
    def show_results(Class):
        dlg = Class()
        for r in dlg.db.results.find({}):
            item = QtWidgets.QTreeWidgetItem()
            item._item = r
            item.setText(0, r.get('saved_at', '').isoformat())
            item.setText(1, '{0}-{1}'.format(r.get('price_min', 0), r.get('price_max', 0)))
            item.setText(2, r.get('product', ''))
            item.setText(3, r.get('brand', ''))
            dlg.ui.results.addTopLevelItem(item)
        dlg.ui.results.resizeColumnToContents(0)
        dlg.ui.results.resizeColumnToContents(1)
        dlg.ui.results.resizeColumnToContents(2)
        dlg.ui.results.resizeColumnToContents(3)
        if dlg.exec_() == SavedResults.Accepted:
            if dlg.selected_item is not None:
                return dlg.selected_item._item

    def return_item(self, item, column):
        self.selected_item = item
        self.accept()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.price_min.setValidator(QtGui.QIntValidator())
        self.ui.price_max.setValidator(QtGui.QIntValidator())
        self.ui.submit.clicked.connect(self.submit)
        self.ui.search_by_keyword.clicked.connect(self.search_by_keyword)
        self.ui.show_people.clicked.connect(self.show_people)
        self.ui.save_results.clicked.connect(self.save_results)
        self.ui.show_results.clicked.connect(self.show_results)
        self.ui.filter_product.currentIndexChanged.connect(self.update_brands)
        self.ui.quit.clicked.connect(self.close)
        self.show()
        self.load_data()

    def get_filtered_metadata(self, preprocessed=False):
        price_min = int(self.ui.price_min.text())
        price_max = int(self.ui.price_max.text())
        filtered = self.metadata_df
        if preprocessed:
            filtered = self.preprocessed_metadata
        filtered = template.filter_by_price(filtered, price_min, price_max)
        filtered = template.filter_by_brand(filtered, self.ui.filter_brand.currentText())
        filtered = template.filter_by_productname(filtered, self.ui.filter_product.currentText())
        #print(filtered)
        return filtered

    def submit(self):
        try:
            self.ui.wordcloud.clear()
            self.ui.histogram.clear()

            self.set_message('Filtering data...')
            filtered = self.get_filtered_metadata()

            #print(filtered)
            self.set_message('Building wordcloud...')
            self.wordcloud_data = template_qt.wordcloud_qt(dataframe=filtered, dataframereview=self.review_df)
            image = QtGui.QImage()
            image.loadFromData(self.wordcloud_data)
            self.ui.wordcloud.setImage(image)

            self.set_message('Building histogram...')
            s_min, s_max = self.get_sentiments()
            self.histogram_data = template_qt.histogram_qt(s_min, s_max, dataframe=filtered, dataframereview=self.review_df)
            image = QtGui.QImage()
            image.loadFromData(self.histogram_data)
            self.ui.histogram.setImage(image)

            self.set_message('Done', color='green')
            self.ui.save_results.setEnabled(True)
        except Exception as e:
            self.set_message('Error: %s' % str(e), color='red')

    def search_by_keyword(self):
        try:
            keyword = self.ui.filter_keyword.text()
            if len(keyword):
                self.ui.histogram.clear()
                filtered = self.get_filtered_metadata(preprocessed=True)
                image_data = template_qt.wordcloud_keyword(filtered)
                image = QtGui.QImage()
                image.loadFromData(image_data)
                self.ui.histogram.setImage(image)
                self.set_message('Done', color='green')
        except Exception as e:
            traceback.print_exc()
            self.set_message('Error: %s' % str(e), color='red')

    def show_people(self):
        try:
            filtered = self.get_filtered_metadata()
            s_min, s_max = self.get_sentiments()
            self.histogram_data = template_qt.wordcloud_people(s_min, s_max, dataframe=filtered, dataframereview=self.review_df)
            image = QtGui.QImage()
            image.loadFromData(self.histogram_data)
            self.ui.histogram.setImage(image)
            self.set_message('Done', color='green')
        except Exception as e:
            self.set_message('Error: %s' % str(e), color='red')

    def save_results(self):
        db = MongoClient()[MONGO_DBNAME]
        fs = gridfs.GridFS(db, collection='images')
        wordcloud_file_id = fs.put(self.wordcloud_data)
        histogram_file_id = fs.put(self.histogram_data)
        s_min, s_max = self.get_sentiments()
        db.results.insert({
            'saved_at': datetime.now(),
            'price_min': int(self.ui.price_min.text()),
            'price_max': int(self.ui.price_max.text()),
            'brand': self.ui.filter_brand.currentText(),
            'product': self.ui.filter_product.currentText(),
            'keyword': self.ui.filter_keyword.text(),
            'sentiment_min': s_min,
            'sentiment_max': s_max,
            'wordcloud_file': wordcloud_file_id,
            'histogram_file': histogram_file_id,
            })
        QtWidgets.QMessageBox.information(self, "Saved", "Current results was saved to database.")

    def show_results(self):
        item = SavedResults.show_results()
        if item:
            db = MongoClient()[MONGO_DBNAME]
            fs = gridfs.GridFS(db, collection='images')
            self.ui.price_min.setText(str(item.get('price_min', '0')))
            self.ui.price_max.setText(str(item.get('price_max', '0')))
            self.ui.filter_brand.setCurrentText(str(item.get('brand', '')))
            self.ui.filter_product.setCurrentText(str(item.get('product', '')))
            self.ui.filter_keyword.setText(str(item.get('keyword', '')))
            self.ui.sentiment_min.setText(str(item.get('sentiment_min', '0.0')))
            self.ui.sentiment_max.setText(str(item.get('sentiment_max', '0.0')))

            wordcloud_file = fs.get(item.get('wordcloud_file'))
            image = QtGui.QImage()
            image.loadFromData(wordcloud_file.read())
            self.ui.wordcloud.setImage(image)

            histogram_file = fs.get(item.get('histogram_file'))
            image = QtGui.QImage()
            image.loadFromData(histogram_file.read())
            self.ui.histogram.setImage(image)

    def load_data(self):
        self.set_message('Loading data...', color='red')
        QtWidgets.QApplication.sendPostedEvents()
        QtWidgets.QApplication.processEvents()
        self.metadata_df = template.read_metadata(template.metadata_filename)
        self.preprocessed_metadata = template.preprocess_metadata(self.metadata_df)
        self.review_df = template.read_preprocess_review(template.review_filename)
        self.set_message('Data is loaded', color='green')
        # self.ui.filter_product.addItems([''] + template.musical_instruments)
        self.ui.filter_product.addItem('')
        for item in sorted(list(self.preprocessed_metadata['Description'].unique())):
            self.ui.filter_product.addItem(str(item))
        self.update_brands()

    def update_brands(self):
        metadata = self.preprocessed_metadata
        product = self.ui.filter_product.currentText()
        if len(product.strip()):
            metadata = metadata[metadata['Description'].str.contains(product, na=False)]
        self.ui.filter_brand.clear()
        self.ui.filter_brand.addItem('')
        for item in sorted(list(metadata['Manufacturer'].unique())):
            self.ui.filter_brand.addItem(str(item))

    def set_message(self, msg, color=None):
        if color:
            self.ui.message.setText('''<font color="{0}">{1}</font>'''.format(color, msg))
        else:
            self.ui.message.setText(msg)
        QtWidgets.QApplication.sendPostedEvents()
        QtWidgets.QApplication.processEvents()

    def get_sentiments(self):
        s_min = 0.0
        s_max = 0.0
        try:
            s_min = float(self.ui.sentiment_min.text())
            s_max = float(self.ui.sentiment_max.text())
        except Exception:
            pass
        return s_min, s_max


class Appliction(QtWidgets.QApplication):
    def __init__(self):
        super(Appliction, self).__init__(sys.argv)
        self.mainWindow = MainWindow()


def main():
    app = Appliction()
    app.exec_()

if __name__ == "__main__":
    main()
