import os
from flask import Flask,request,render_template
import pandas as pd
from nltk.corpus import stopwords
stop_words = set(stopwords.words("english"))
from nltk.tokenize import word_tokenize
import string
import csv
from PIL import Image
from nltk.sentiment import SentimentIntensityAnalyzer
from wordcloud import WordCloud


def depunc(para):
  list1=[c for c in para if c not in string.punctuation and c not in list('0123456789')]
  return ''.join(list1)


def tokenize(para):
  tokens = word_tokenize(para)
  return tokens

from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
def remove_stopwords(token_list):
  list1 = [word for word in token_list if word not in stop_words and word != 'br']
  list1 = [lemmatizer.lemmatize(word) for word in list1]
  return ' '.join(list1)


def sentiment_labels(para):
  sid = SentimentIntensityAnalyzer()
  sentiment_scores = sid.polarity_scores(para)
  if sentiment_scores['compound'] >0:
    sentiment = 'Positive'
  elif sentiment_scores['compound']<0:
    sentiment = 'Negative'
  else:
    sentiment = 'Neutral'
  return sentiment

app = Flask(__name__)

@app.route("/assess",methods=["GET","POST"])
def assess():
    if request.method == "POST":
       pid = int(request.form.get("pid"))
       f = open('GFG.csv','a')
       try:
        df = pd.read_csv('GFG.csv')
       except:
         return "No Review Data"
       df.columns = ['student_id','course_id','review_body','labels']
       comment=''
       count_negative = len(df[(df['course_id']==pid) & (df['labels']=='Negative')])
       count_positive = len(df[(df['course_id']==pid) & (df['labels']=='Positive')])
       count_neutral = len(df[(df['course_id']==pid) & (df['labels']=='Neutral')])
       if count_negative ==0 and count_positive > 0:
        comment = "Quality of teaching is good enough"
       elif count_negative !=0:
        if count_positive/count_negative < 1:
          comment = "Quality of teaching needs improvement!"
        else:
          comment = "Quality of teaching is good enough!"
       elif count_neutral > 0:
        comment = "Quality of teaching is OK!"
       return "<body bgcolor='cyan'style='font-size:medium;'><h1>"+comment+"</body></h1>"
    return render_template("assess.html")

        
@app.route("/recommend",methods=["GET","POST"])
def recommend():
    if request.method == "POST":
        pid = int(request.form.get("pid"))
        f = open('GFG.csv','a')
        try:
          df = pd.read_csv('GFG.csv')
        except:
         return "No Review Data"
        df.columns = ['student_id','course_id','review_body','labels']
        customer_list = df[(df['course_id']==pid) & (df['labels']== 'Positive') ]['student_id'] #all customers who gave positive review about chosen product
        recommended_list=[]
        dict1={1:'Bootcamp in Python',2 : 'Machine Learninng in Python',3: 'Data Visualization Using Tableau',4:'Computer Networks',5:'Internet Of Things Embedded Systems',6:'Android Development',7: 'Full Stack Development',8: 'Data Structures'}
        for cust in customer_list:
            L = list(df[(df['student_id']==cust) & (df['course_id']!=pid) &  (df['labels']== 'Positive')]['course_id'])
            for item in L:
               recommended_list.append(dict1[item])
        recommended_list = list(set(recommended_list))
        str="<ol style='color:blue;font-weight: bold;font-size:40px;'>"
        for i in recommended_list:
           str = str +"<li>"+ i + "</li>"
        return "<body bgcolor='cyan'style='font-size:medium;'>"+str+"</ol></body>"
    return render_template("recommend.html")

@app.route("/home",methods=["GET","POST"])
def home():
    if request.method=="GET":
        return render_template("home.html")
        
    elif request.method=="POST":
        review = request.form.get("review")
        cid = request.form.get("cid")
        pid = request.form.get("pid")
        review = depunc(review)
        review = tokenize(review)
        review = remove_stopwords(review)
        sentiment = sentiment_labels(review)
        rows=[[cid,pid,review,sentiment]]
        f = open('GFG.csv','a')
        write = csv.writer(f)
        write.writerows(rows)
            
        return "<body bgcolor='cyan'style='font-size:medium;'><h2 style='border-size:3px;border-style:double;'>Your review has been recorded with "+sentiment+" sentiment analysis</h2></body>"

@app.route("/",methods=["GET","POST"])
def home1():
   if request.method == "GET":
    return render_template("home1.html")
   
@app.route("/analyse_feedback",methods=['GET','POST'])
def wordcloud():
  if request.method == "GET":
    return render_template("word_cloud.html") 
  elif request.method == 'POST':
    pid = int(request.form.get("pid"))
    f = open('GFG.csv','a')
    try:
        df = pd.read_csv('GFG.csv')
    except:
         return "No Review Data"
    df.columns = ['student_id','course_id','review_body','labels']
    rev = list(df[df['course_id']==pid]['review_body'])
    rev = " ".join(rev)
    rev = rev.lower()
    wc = WordCloud().generate(rev)
    wc.to_file('./static/wordcloud.jpg')
    filename = Image.open("./static/wordcloud.jpg")
    filename.show()
    file_name = os.path.join('static','wordcloud.jpg')
    return "<body bgcolor='blue'><img src ="+str(file_name)+">"
  