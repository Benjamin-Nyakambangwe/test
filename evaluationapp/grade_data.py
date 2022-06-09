from pickle import load
import re
from nltk.stem.snowball import SnowballStemmer
from tensorflow import keras
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Dense, Flatten, LSTM, Conv1D, MaxPooling1D, Dropout, Activation, Bidirectional, Concatenate
from keras.layers.embeddings import Embedding
from tensorflow.python.keras import utils
from tensorflow.keras import Input
from sklearn.preprocessing import OneHotEncoder, LabelEncoder, StandardScaler, MinMaxScaler
from sklearn.ensemble import RandomForestClassifier, StackingClassifier, AdaBoostClassifier, VotingClassifier, GradientBoostingClassifier
from sklearn.model_selection import cross_validate, cross_val_predict, KFold, StratifiedKFold, train_test_split, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import Lasso, ElasticNet, LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, plot_confusion_matrix
# import matplotlib.pyplot as plt
import seaborn as sns
import string
import numpy as np
import pandas as pd
from category_encoders import TargetEncoder, LeaveOneOutEncoder
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')


df = pd.read_excel("evaluationapp/job_evaluation_system/Test_data 2.xlsx")


# Predict classes
def clean_text(text):
    '''
    This function cleans text by removing punctuation and stopwords, converting to lowercase, substituting some words and stemming.
    '''

    # Remove puncuation if any left
    text = text.translate(string.punctuation)

    # Convert words to lower case and split them
    text = text.lower().split()

    # Remove stop words
    stops = set(stopwords.words("english"))
    text = [w for w in text if not w in stops and len(w) >= 3]

    text = " ".join(text)
    # Clean the text
    text = re.sub(r"[^A-Za-z0-9^,!.\/'+-=]", " ", text)
    text = re.sub(r"what's", "what is ", text)
    text = re.sub(r"\'s", " ", text)
    text = re.sub(r"\'ve", " have ", text)
    text = re.sub(r"n't", " not ", text)
    text = re.sub(r"i'm", "i am ", text)
    text = re.sub(r"\'re", " are ", text)
    text = re.sub(r"\'d", " would ", text)
    text = re.sub(r"\'ll", " will ", text)
    text = re.sub(r",", " ", text)
    text = re.sub(r"\.", " ", text)
    text = re.sub(r"!", " ! ", text)
    text = re.sub(r"\/", " ", text)
    text = re.sub(r"\^", " ^ ", text)
    text = re.sub(r"\+", " + ", text)
    text = re.sub(r"\-", " - ", text)
    text = re.sub(r"\=", " = ", text)
    text = re.sub(r"'", " ", text)
    text = re.sub(r"(\d+)(k)", r"\g<1>000", text)
    text = re.sub(r":", " : ", text)
    text = re.sub(r" e g ", " eg ", text)
    text = re.sub(r" b g ", " bg ", text)
    text = re.sub(r" u s ", " american ", text)
    text = re.sub(r"\0s", "0", text)
    text = re.sub(r" 9 11 ", "911", text)
    text = re.sub(r"e - mail", "email", text)
    text = re.sub(r"j k", "jk", text)
    text = re.sub(r"\s{2,}", " ", text)

    # Stemming
    text = text.split()
    stemmer = SnowballStemmer('english')
    stemmed_words = [stemmer.stem(word) for word in text]
    text = " ".join(stemmed_words)
    return text


# Load model and encoders
# load_model('model')
saved_le = load(open('evaluationapp/job_evaluation_system/le.pkl', 'rb'))
saved_ohe = load(open('evaluationapp/job_evaluation_system/ohe.pkl', 'rb'))
saved_tokenizer = load(
    open('evaluationapp/job_evaluation_system/tokenizer.pkl', 'rb'))
saved_model = keras.models.load_model(
    'evaluationapp/job_evaluation_system/my_model')
# saved_model = load(open('model.pkl', 'rb'))


# #Example input
# purpose = "To clean and wrangle data and give actionable insights"
# main_duties = "collect data, clean data, create graphs and visualizations, report findings"
# planning_required = "what data to cllect, which methods to use for analysis, which tools to use for cleaning and analysis"
# min_prof_qualifications = "none"
# technical_competence_required = "python programming"
# key_decisions = "data collection"
# academic_qualifications = "Bachelor's degree"
# experience_in_years = 2


def start_grade(purpose, main_duties, planning_required, min_prof_qualifications, technical_competence_required, key_decisions, academic_qualifications, experience_in_years):

    # Preprocess input, start with text columns
    input_text = str(purpose) + " " + str(main_duties) + " " + str(planning_required) + " " + str(min_prof_qualifications) + \
        " " + str(technical_competence_required) + " " + str(key_decisions)
    text_features = pd.DataFrame(
        input_text, columns=["Description"], index=[0])

    text_features = clean_text(str(text_features))

    # preprocessing for word embeddings
    text_sequences = saved_tokenizer.texts_to_sequences(
        pd.Series(text_features))
    final_text = pad_sequences(text_sequences, maxlen=50)

    # preprocess qualifications and experience
    qualifications_and_experience = {'Grouped academic qualifications': str(academic_qualifications),
                                     'Min Experience In Months': experience_in_years*12}

    qualifications_and_experience = pd.DataFrame(
        qualifications_and_experience, index=[0])
    qualifications_and_experience = qualifications_and_experience.replace(
        '[^\w\s]', ' ', regex=True)
    qualifications_and_experience['Grouped academic qualifications'] = saved_le.transform(
        qualifications_and_experience['Grouped academic qualifications'])

    # Predict
    prediction = saved_model.predict(
        [final_text, qualifications_and_experience])
    grade = saved_ohe.inverse_transform(prediction)

    # Load model and encoders
    saved_subgrades_model = load(
        open('evaluationapp/job_evaluation_system/subgrade_model.pkl', 'rb'))
    saved_encoder = load(
        open('evaluationapp/job_evaluation_system/encoder.pkl', 'rb'))
    saved_train_experience = load(
        open('evaluationapp/job_evaluation_system/train_experience.pkl', 'rb'))
    saved_mean = load(
        open('evaluationapp/job_evaluation_system/mean.pkl', 'rb'))
    saved_std = load(open('evaluationapp/job_evaluation_system/std.pkl', 'rb'))

    subgrades_input = pd.DataFrame({'Grouped academic qualifications': academic_qualifications,
                                    'Min Experience In Months': experience_in_years}, index=[0])

    # preprocess for subgrades model
    preprocessed_input = preprocess_test(
        subgrades_input, saved_encoder, saved_train_experience, saved_mean, saved_std)

    # predict
    subgrade = saved_subgrades_model.predict(preprocessed_input)

    # Combining Grade and Subgrades
    result = str(grade[0][0]) + str(subgrade[0])
    return result


# Predicting Subgrades
def preprocess_test(df_test, encoder, exp_train, mean, std):
    # test (created scaling values (mean, std) and encoder based on train in preprocess_train, so now apply these to test)
    exp_test = df_test['Min Experience In Months'].values
    exp_test = exp_test.reshape(-1, 1)
    df_test['Min Experience In Months'] = (
        exp_test-exp_train.mean())/exp_train.std()

    q_test = df_test['Grouped academic qualifications']
    transf_test_df = encoder.transform(q_test)
    transf_te = transf_test_df['Grouped academic qualifications'].values
    transf_test_df['Grouped academic qualifications'] = (transf_te-mean)/std
    df_test = df_test.drop(['Grouped academic qualifications'], axis=1)

    test_result = pd.concat([transf_test_df, df_test], axis=1)

    return test_result
