from email.mime import audio
from urllib import response
from flask import Flask, request, render_template
from matplotlib import artist
import pandas as pd
import random
import bisect

app = Flask(__name__)

# 楽曲データを読み込む関数
def music_data(genre):# 回答を引数とする
    if genre==1:
        df = pd.read_csv('spotify_data_global_mm_cluster.csv') # 正規化/クラスタリングしたデータ
    elif genre==2:
        df = pd.read_csv('spotify_data_JP_famous_mm_cluster.csv')
    elif genre==3:
        df = pd.read_csv('spotify_data_vocaloid_mm_cluster.csv')
    return df

# 楽曲をリコメンドする関数(質問バージョン)
def music_recommend(ans,df):# 回答を引数とする
    data=['name', 'artist', 'release_date', 'length', 'popularity', 'danceability', 'acousticness', 'energy', 'loudness', 'tempo',  'valence', 'url', 'image', 'audio']
    df = df[data]
    min_point=10000
    for i in range(len(df)):
        point=0
        cnt=len(df)/5
        for j in range(len(ans)-1):
            if ans[j+1]==5:
                point+=random.uniform(0, 1)
            else:
                df_sort=df.sort_values(by=data[j+5], ascending=True)
                rand=random.uniform(df_sort.values[int(ans[j+1]*cnt)][j+5], df_sort.values[int((ans[j+1]+1)*cnt)-1][j+5])
                point+=pow(df.values[i][j+5]-rand,2)
        if point<min_point:
            min_point=point
            min_i=i
        
    min_values=[]
    for k in range(len(ans)-1):
        min_values.append(df.values[min_i][k+5])

    rank=[]
    for i in range(6):
        df_sort=df.sort_values(by=data[i+5], ascending=True)
        cnt=bisect.bisect(list(df_sort[data[i+5]].values),min_values[i])
        rank.append(cnt)

    rec_music_data=[]
    rec_music_data.append(df.values[min_i][0]) # リコメンドする楽曲
    rec_music_data.append(df.values[min_i][1]) # リコメンドする楽曲のアーティスト名
    rec_music_data.append(df.values[min_i][11]) # リコメンドする楽曲のurl
    rec_music_data.append(df.values[min_i][12]) # リコメンドする楽曲のimage
    rec_music_data.append(df.values[min_i][13]) # リコメンドする楽曲のaudio
    rec_music_data.append(min_values) # リコメンドする楽曲の数値(リスト)
    rec_music_data.append(rank) # リコメンドする楽曲の数値の順位(リスト)(その音楽データの中での順位)
    return rec_music_data

def music_recommend2(rec_music_values,df):
    data=['name', 'artist', 'release_date', 'length', 'popularity', 'danceability', 'acousticness', 'energy', 'loudness', 'tempo',  'valence', 'url', 'image', 'audio']
    df = df[data]
    min_point=10000
    for i in range(len(df)):
        point=0
        for j in range(6):
            point+=pow(df.values[i][j+5]-rec_music_values[j],2)
        if point<min_point:
            min_point=point
            min_i=i

    min_values=[]
    for k in range(6):
        min_values.append(df.values[min_i][k+5])

    rank=[]
    for i in range(6):
        df_sort=df.sort_values(by=data[i+5], ascending=True)
        cnt=bisect.bisect(list(df_sort[data[i+5]].values),rec_music_values[i])
        rank.append(cnt)

    music_info=[]
    music_info.append(df.values[min_i][0]) # リコメンドする楽曲
    music_info.append(df.values[min_i][1]) # リコメンドする楽曲のアーティスト名
    music_info.append(df.values[min_i][11]) # リコメンドする楽曲のurl
    music_info.append(df.values[min_i][12]) # リコメンドする楽曲のimage
    music_info.append(df.values[min_i][13]) # リコメンドする楽曲のaudio

    rec_music_data=[]
    rec_music_data.append(music_info) # リコメンドする楽曲の情報(リスト)
    rec_music_data.append(min_values) # リコメンドする楽曲の数値(リスト)
    rec_music_data.append(rank) # リコメンドする楽曲の数値の順位(リスト)(その音楽データの中での順位)
    return rec_music_data

# 同じクラスタの曲をおすすめする関数(この関数は位置を返す)
def cluster_recommend(name,df):
    data=['name', 'artist', 'release_date', 'length', 'popularity', 'danceability', 'acousticness', 'energy', 'loudness', 'tempo',  'valence', 'url', 'image', 'audio', 'cluster_pred']
    df = df[data]
    for i in range(len(df)):
        if df.values[i][0]==name:
            min_i=i
            break
            
    cluster=df.values[min_i][14]
    cnt=0
    while cnt==0:
        rand=random.randrange(len(df))
        if df.values[rand][14]==cluster:
            new_name=df.values[rand][0]
            new_cluster=df.values[rand][14]
            if new_name!=name:
                cnt=1
    return rand

@app.route('/')
def post():
    response = render_template('index.html')
    return response

@app.route('/result', methods=['POST'])
def result():
    ans=[]
    q=['genre','q1','q2','q3','q4','q5','q6']
    for i in range(len(q)):
        ans.append(int(request.form[q[i]]))
    df=music_data(ans[0])
    rec_music_data=music_recommend(ans,df)
    rec_music_name=rec_music_data[0]
    rec_music_artist=rec_music_data[1]
    rec_music_url=rec_music_data[2]
    rec_music_image=rec_music_data[3]
    rec_music_audio=rec_music_data[4]
    rec_music_values=rec_music_data[5]
    rec_music_rank=rec_music_data[6]
    Q=[['好き','やや好き','普通','やや嫌い','嫌い','特に好みはない']
      ,['強め','やや強め','普通','やや弱め','弱め','特に好みはない']
      ,['強め','やや強め','普通','やや弱め','弱め','特に好みはない']
      ,['強め','やや強め','普通','やや弱め','弱め','特に好みはない']
      ,['速め','やや速め','普通','やや遅め','遅め','特に好みはない']
      ,['楽観的','やや楽観的','普通','やや悲観的','悲観的','どちらでも良い']]
    answer=[]
    for i in range(6):
        answer.append(Q[i][ans[i+1]])
    response = render_template('result.html',music=rec_music_name,artist=rec_music_artist,url=rec_music_url,image=rec_music_image,audio=rec_music_audio,values=rec_music_values,rank=rec_music_rank,size=len(df),ans=answer,genre=ans[0])
    return response

@app.route('/chart', methods=['POST'])
def chart():
    rec_music_values=[]
    q=['range-1','range-2','range-3','range-4','range-5','range-6', 'genre']
    for i in range(len(q)-1):
        rec_music_values.append(float(request.form[q[i]]))
    genre=int(request.form[q[6]])
    df=music_data(genre)
    rec_music_data=music_recommend2(rec_music_values,df)
    response = render_template('chart.html',values=rec_music_data[1],music=rec_music_data[0][0],artist=rec_music_data[0][1],url=rec_music_data[0][2],image=rec_music_data[0][3],audio=rec_music_data[0][4],music_rank=rec_music_data[2],size=len(df),genre=genre)
    return response

@app.route('/cluster', methods=['POST'])
def cluster():
    q=['genre','name']
    genre=int(request.form[q[0]])
    name=request.form[q[1]]
    df=music_data(genre)
    min_i=cluster_recommend(name,df)
    data=['name', 'artist', 'release_date', 'length', 'popularity', 'danceability', 'acousticness', 'energy', 'loudness', 'tempo',  'valence', 'url', 'image', 'audio', 'cluster_pred']
    df = df[data]

    min_values=[]
    for k in range(6):
        min_values.append(df.values[min_i][k+5])

    rank=[]
    for i in range(6):
        df_sort=df.sort_values(by=data[i+5], ascending=True)
        cnt=bisect.bisect(list(df_sort[data[i+5]].values),min_values[i])
        rank.append(cnt)

    rec_music_data=[]
    rec_music_data.append(df.values[min_i][0]) # リコメンドする楽曲
    rec_music_data.append(df.values[min_i][1]) # リコメンドする楽曲のアーティスト名
    rec_music_data.append(df.values[min_i][11]) # リコメンドする楽曲のurl
    rec_music_data.append(df.values[min_i][12]) # リコメンドする楽曲のimage
    rec_music_data.append(df.values[min_i][13]) # リコメンドする楽曲のaudio
    rec_music_data.append(min_values) # リコメンドする楽曲の数値(リスト)
    rec_music_data.append(rank) # リコメンドする楽曲の数値の順位(リスト)(その音楽データの中での順位)

    rec_music_name=rec_music_data[0]
    rec_music_artist=rec_music_data[1]
    rec_music_url=rec_music_data[2]
    rec_music_image=rec_music_data[3]
    rec_music_audio=rec_music_data[4]
    rec_music_values=rec_music_data[5]
    rec_music_rank=rec_music_data[6]
    response = render_template('chart.html',music=rec_music_name,artist=rec_music_artist,url=rec_music_url,image=rec_music_image,audio=rec_music_audio,values=rec_music_values,music_rank=rec_music_rank,size=len(df),genre=genre)
    return response

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)