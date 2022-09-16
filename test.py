from flask import Flask, request, render_template
import pandas as pd
import random
import bisect

app = Flask(__name__)

# 楽曲データを保存する関数関数
def music_data(ans):# 回答を引数とする
    if ans[0]==1:
        df = pd.read_csv('spotify_data_global_mm.csv') # 正規化したデータ
    elif ans[0]==2:
        df = pd.read_csv('spotify_data_JP_famous_mm.csv')
    elif ans[0]==3:
        df = pd.read_csv('spotify_data_vocaloid_mm.csv')
    return df

# 楽曲をリコメンドする関数
def music_recommend(ans,df):# 回答を引数とする
    data=['name', 'artist', 'release_date', 'length', 'popularity', 'danceability', 'acousticness', 'energy', 'loudness', 'tempo',  'valence', 'url', 'image', 'audio']
    df = df[data]
    rec_music_data=[]
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

    rec_music_data.append(df.values[min_i][0]) # リコメンドする楽曲
    rec_music_data.append(df.values[min_i][1]) # リコメンドする楽曲のアーティスト名
    rec_music_data.append(df.values[min_i][11]) # リコメンドする楽曲のurl
    rec_music_data.append(df.values[min_i][12]) # リコメンドする楽曲のimage
    rec_music_data.append(df.values[min_i][13]) # リコメンドする楽曲のaudio
    rec_music_data.append(min_values) # リコメンドする楽曲の数値(リスト)
    rec_music_data.append(rank) # リコメンドする楽曲の数値の順位(リスト)(その音楽データの中での順位)
    return rec_music_data

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
    df=music_data(ans)
    rec_music_data=music_recommend(ans,df)
    rec_music_name=rec_music_data[0]
    rec_music_artist=rec_music_data[1]
    rec_music_url=rec_music_data[2]
    rec_music_image=rec_music_data[3]
    rec_music_audio=rec_music_data[4]
    rec_music_values=rec_music_data[5]
    rec_music_rank=rec_music_data[6]
    
    response = render_template('result.html',music=rec_music_name,artist=rec_music_artist,url=rec_music_url,image=rec_music_image,audio=rec_music_audio,values=rec_music_values,rank=rec_music_rank,size=len(df))
    return response

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)