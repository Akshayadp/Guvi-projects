from googleapiclient.discovery import build
import pymongo
#import MySQLdb
import mysql.connector
import pandas as pd
import datetime
import streamlit as st
from streamlit_option_menu import option_menu


# API Key Connection

def api_connect():
    #api_key = "AIzaSyComLKqHzS9Zf2cGVh0JhtSvlW1M8rlCAg"
    api_key = "AIzaSyAgDlAMyKH1Z6wD9whTwtFqdT0dWUoan5k"
    api_name = "Youtube"
    api_version = "v3"

    youtube_api = build(api_name, api_version, developerKey = api_key)

    return youtube_api

youtube_api = api_connect()

# Getting Channel Info 

def channel_info(channel_id):
    request = youtube_api.channels().list(
    part = "snippet, contentDetails, statistics",
    id = channel_id
    )
    outcome = request.execute()

    for i in outcome['items']:
        content = dict (Channel_name = i ["snippet"]["title"],
                        Channel_id = i ["id"],
                        Subscriber_count = i ["statistics"]["subscriberCount"],
                        Views_count = i ["statistics"]["viewCount"],
                        Videos_count = i ["statistics"]["videoCount"],
                        Channel_description = i ["snippet"]["description"],
                        Playlist_id = i ["contentDetails"]["relatedPlaylists"]["uploads"])
        
        return content
    
#all_details = channel_info ("UC90R_fHWlQP50ANrk28aOzA")
#all_details = channel_info ("UCNrlHfYLo7s2eoeKEJiJi3Q")
#all_details = channel_info ("UCH6acC9jnug-mI4vdGvuDbA")


#all_details

# Getting all the video IDs

def get_vids (channel_id):
    video_ids = []

    outcome = youtube_api.channels().list(id = channel_id,
                                    part = "contentDetails").execute()


    playlist_id = outcome ["items"] [0] ["contentDetails"] ["relatedPlaylists"] ["uploads"]
    npt = None   #nextPageToken(npt)

    while True:
        request = youtube_api.playlistItems().list(part = 'snippet',
                                                playlistId = playlist_id,
                                                maxResults = 50,
                                                pageToken = npt).execute()
        #outcome = request.execute()

        for i in range(len(request["items"])):
            video_ids.append(request["items"] [i] ["snippet"]['resourceId']['videoId'])
        npt = request.get('nextPageToken')

        if npt is None:
            break
    return (video_ids)

#vids = get_vids('UCNrlHfYLo7s2eoeKEJiJi3Q')
#vids = get_vids('UC90R_fHWlQP50ANrk28aOzA')
#vids = get_vids("UCH6acC9jnug-mI4vdGvuDbA")
#outcome
#print(len(vids))
#vids

# Getting video details using video ids

def video_details(vdetails):
    Video_info = []
    for video_id in vdetails:
        vdata = youtube_api.videos().list(part = "snippet, contentDetails, statistics",
                                        id = video_id)
        outcome = vdata.execute()

        for item in outcome['items']:
            video_content = dict(Channel_Name = item['snippet']['channelTitle'],
                                Channel_Id = item['snippet']['channelId'],
                                Video_Id = item['id'],
                                Title = item['snippet']['title'],
                                Tags = item['snippet'].get('tags'),
                                Video_Duration = item['contentDetails']['duration'],
                                Description = item['snippet'].get('description'),
                                Published_on = item['snippet']['publishedAt'],
                                Thumbnail = item['snippet']['thumbnails']['default']['url'],
                                Video_views = item['statistics']['viewCount'],
                                Likes_count = item['statistics'].get('likeCount'),
                                Video_comments = item['statistics'].get('commentCount'),
                                Favorite_count = item['statistics']['favoriteCount'],
                                Definition = item ['contentDetails']['definition'],
                                Caption = item['contentDetails']['caption']
                                )
        Video_info.append(video_content)

    return Video_info

#video_det = video_details(vids)

#for i in video_det:
#    print(i)


#Getting comments details

def video_comments(vcomments):
    comment_info = []
    try:

        for videoid in vcomments:
            request = youtube_api.commentThreads().list(part = "snippet",
                                                        videoId = videoid,
                                                        maxResults = 50)
            outcome = request.execute()

            for item in outcome['items']:
                comment_content = dict(Comment_ID = item['snippet']['topLevelComment']['id'],
                                    Video_Id = item['snippet']['topLevelComment']['snippet']['videoId'],
                                    Comments = item['snippet']['topLevelComment']['snippet']['textDisplay'],
                                    Comment_Author = item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                                    commented_on = item['snippet']['topLevelComment']['snippet']['publishedAt']
                                    )
            comment_info.append(comment_content)
    
    except:
        pass

    return comment_info

#comment_details = video_comments(vids)

#for j in comment_details:
 #   print(j)

# Getting playlist details

def playlist_details(channel_id):
    npt = None
    playlist_info = []

    while True:
        request = youtube_api.playlists().list(part = "snippet,contentDetails",
                                               channelId = channel_id,
                                               maxResults = 50,
                                               pageToken = npt)
        outcome = request.execute()

        for item in outcome['items']:
            playlist_det = dict(Playlist_Id = item['id'],
                                Title = item['snippet']['title'],
                                Channel_Id = item['snippet']['channelId'],
                                Channel_Name = item['snippet']['channelTitle'],
                                Published_on = item['snippet']['publishedAt'],
                                Video_count = item['contentDetails']['itemCount']
                                )
            playlist_info.append(playlist_det)

        npt = outcome.get('nextPageToken')
        if npt is None:
            break
    
    return playlist_info

#playlist_dett = playlist_details('UCNrlHfYLo7s2eoeKEJiJi3Q')
#playlist_dett = playlist_details('UC90R_fHWlQP50ANrk28aOzA')
#playlist_dett = playlist_details('UCH6acC9jnug-mI4vdGvuDbA')

#len(playlist_dett)

#for n in playlist_dett:
#    print(n)


#Connecting mongodb 

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["Youtube_dataharvesting"]

#creating DB and uploading the details to mongodb

def channel_details(channel_id):
    
    chann_details = channel_info(channel_id)
    play_details = playlist_details(channel_id)
    video_ids = get_vids (channel_id)
    vid_details = video_details(video_ids)
    comm_details = video_comments(video_ids)

    connection1 = db["channel_details"]
    connection1.insert_one({"channel_informations": chann_details,
                            "playlist_informations": play_details,
                            "video_informations": vid_details,
                            "comment_informations": comm_details})
    
    return "Informations Uploaded Successfully"

#call = channel_details("UCNrlHfYLo7s2eoeKEJiJi3Q")
#call = channel_details("UCH6acC9jnug-mI4vdGvuDbA")
#call = channel_details("UCvoBYKyBDVXrBHH2aF5cLVA")
#call = channel_details("UCmStss7XaGLmmE6k8lpW5_Q")
#call = channel_details("UCuxZyUMvZCIVx6fV0omnssQ")
#call = channel_details("UC8iJjhq3c1K1Mc-jpl51EKg")
#call = channel_details("UCPIs4IuXK7K_Hq-BcjW9MzA")
#call = channel_details("UCeqG5xk1KiPoRdVPHkwGTAA")
#call = channel_details("UCTkSSggbQgouxa8cH02SE_A")


# Database creation for data harvesting
#Creating Channels table

def channel_table():

    mydb =  mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "NANANANA",
        database = "Youtube_dataharvesting"
        )

    cursor = mydb.cursor()               


    drop_query = '''drop table if exists Channels'''
    cursor.execute(drop_query)
    mydb.commit()


    try:
        create_query = '''create table if not exists Channels(Channel_Name varchar(100),
        Channel_id varchar(100) primary key,
        Subscriber_count bigint,
        Views_count bigint,
        Videos_count int,
        Channel_description text,
        Playlist_id varchar(100))'''

        cursor.execute(create_query)
        mydb.commit()

    except:
        print("Unable to create channels table")


    channel_list = []

    db = client ["Youtube_dataharvesting"]
    collection = db ["channel_details"]

    for channel_data in collection.find({},{"_id":0,"channel_informations":1}):
        channel_list.append(channel_data["channel_informations"])

    df = pd.DataFrame(channel_list)


    for index,row in df.iterrows():
        #print(index,row)
        insert_row = '''insert into Channels(Channel_name,
                                            Channel_id,
                                            Subscriber_count,
                                            Views_count,
                                            Videos_count,
                                            Channel_description,
                                            Playlist_id)
                                            
                                            values(%s, %s, %s, %s, %s, %s, %s)'''
        
        values = (row['Channel_name'],
                row['Channel_id'],
                row['Subscriber_count'],
                row['Views_count'],
                row['Videos_count'],
                row['Channel_description'],
                row['Playlist_id']) 
        

        cursor.execute(insert_row,values)
        mydb.commit()


#creating playlist table

def playlist_table():

    mydb =  mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "NANANANA",
        database = "Youtube_dataharvesting"
        )

    cursor = mydb.cursor()

    drop_query = '''drop table if exists Playlist'''
    cursor.execute(drop_query)
    mydb.commit()



    create_query = '''create table if not exists Playlist(Playlist_Id varchar(100) primary key,
                                                        Title varchar(100),
                                                        Channel_Id varchar(100),
                                                        Channel_Name varchar(100),
                                                        Published_on timestamp,
                                                        Video_count int)'''

    cursor.execute(create_query)
    mydb.commit()


    #Creating Table


    play_list = []

    db = client ["Youtube_dataharvesting"]
    collection = db ["channel_details"]

    for playlist_data in collection.find({},{"_id":0,"playlist_informations":1}):
        for i in range(len(playlist_data["playlist_informations"])):
            play_list.append(playlist_data["playlist_informations"][i])

    playlist_df = pd.DataFrame(play_list)

    playlist_df['Published_on'] = playlist_df["Published_on"].apply(lambda x:datetime.datetime.strptime(x, '%Y-%m-%dT%H:%M:%SZ'))


    for index,row in playlist_df.iterrows():
        #print(index,row)
        insert_row = '''insert into Playlist(Playlist_Id,
                                        Title,
                                        Channel_Id,
                                        Channel_Name,
                                        Published_on,
                                        Video_count)
                                        
                                        values(%s, %s, %s, %s, %s, %s)'''

        values = (row['Playlist_Id'],
                row['Title'],
                row['Channel_Id'],
                row['Channel_Name'],
                row['Published_on'],
                row['Video_count']) 


        cursor.execute(insert_row,values)
        mydb.commit()

# Creating Videos table

def parse_duration(duration_str):
    minutes = 0 
    seconds = 0
    if 'M' in duration_str:
        minutes = int(duration_str.split('M')[0].split('T')[-1])
        if 'S' in duration_str:
            seconds = int(duration_str.split('S')[0].split('M')[-1])
            return datetime.timedelta(minutes=minutes, seconds=seconds)
        
def formate_duration(duration):
    seconds = duration.total_seconds()
    hours = int (seconds//3600)
    minutes = int ((seconds%3600)//60)
    seconds = int(seconds%60)

    return '{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)


def video_table():
    mydb =  mysql.connector.connect(
            host = "localhost",
            user = "root",
            password = "NANANANA",
            database = "Youtube_dataharvesting"
            )

    cursor = mydb.cursor()

    drop_query = '''drop table if exists Videos'''
    cursor.execute(drop_query)
    mydb.commit()



    create_query = '''create table if not exists Videos(Channel_Name varchar(100),
                                                    Channel_Id varchar(100),
                                                    Video_Id varchar(50) primary key,
                                                    Title varchar(200),
                                                    Tags text,
                                                    Video_Duration time,
                                                    Description text,
                                                    Published_on timestamp,
                                                    Thumbnail varchar(200),
                                                    Video_views bigint,
                                                    Likes_count bigint,
                                                    Video_comments int,
                                                    Favorite_count int,
                                                    Definition varchar(100),
                                                    Caption varchar(100))'''

    cursor.execute(create_query)
    mydb.commit()


    duration_str = 'PT9M11S'
    duration_timedelta = parse_duration(duration_str) 
    duration_formatted = str(duration_timedelta)


    video_list = []

    db = client ["Youtube_dataharvesting"]
    collection = db ["channel_details"]

    for video_data in collection.find({},{"_id":0,"video_informations":1}):
        for i in range(len(video_data["video_informations"])):
            video_list.append(video_data["video_informations"][i])

    video_df = pd.DataFrame(video_list)

    video_df['Tags'] = video_df["Tags"].apply(lambda x:','.join(x)
    if isinstance(x,list) else x)

    video_df['Published_on'] = video_df["Published_on"].apply(lambda x:datetime.datetime.strptime(x, '%Y-%m-%dT%H:%M:%SZ'))


    for index,row in video_df.iterrows():

        insert_row = '''insert into Videos(Channel_Name,
                                            Channel_Id,
                                            Video_Id,
                                            Title,
                                            Tags,
                                            Video_Duration,
                                            Description,
                                            Published_on,
                                            Thumbnail,
                                            Video_views,
                                            Likes_count,
                                            Video_comments,
                                            Favorite_count,
                                            Definition,
                                            Caption)
                                        
                                        values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''

        values = (row['Channel_Name'],
                row['Channel_Id'],
                row['Video_Id'],
                row['Title'],
                row['Tags'],
                duration_formatted,
                #row['Video_Duration'],
                row['Description'],
                row['Published_on'],
                row['Thumbnail'],
                row['Video_views'],
                row['Likes_count'],
                row['Video_comments'],
                row['Favorite_count'],
                row['Definition'],
                row['Caption'])
        
        cursor.execute(insert_row,values)
        mydb.commit()


#creating comment table

def comment_table():

    mydb =  mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "NANANANA",
        database = "Youtube_dataharvesting"
        )

    cursor = mydb.cursor()

    drop_query = '''drop table if exists Comments'''
    cursor.execute(drop_query)
    mydb.commit()



    create_query = '''create table if not exists Comments(Comment_ID varchar(100) primary key,
                                                        Video_Id varchar(100),
                                                        Comments text,
                                                        Comment_Author varchar(200),
                                                        commented_on varchar(100))'''

    cursor.execute(create_query)
    mydb.commit()



    comm_list = []

    db = client ["Youtube_dataharvesting"]
    collection = db ["channel_details"]

    for comment_data in collection.find({},{"_id":0,"comment_informations":1}):
        for i in range(len(comment_data["comment_informations"])):
            comm_list.append(comment_data["comment_informations"][i])

    comment_df = pd.DataFrame(comm_list)

    #comment_df

    for index,row in comment_df.iterrows():
        #print(index,row)
        insert_row = '''insert into Comments(Comment_ID,
                                        Video_Id,
                                        Comments,
                                        Comment_Author,
                                        commented_on)
                                        
                                        values(%s, %s, %s, %s, %s)'''

        values = (row['Comment_ID'],
                row['Video_Id'],
                row['Comments'],
                row['Comment_Author'],
                row['commented_on']) 


        cursor.execute(insert_row,values)
        mydb.commit()


def tables():
    channel_table()
    playlist_table()
    video_table()
    comment_table()

    return "Tables Created Successfully"

Tables = tables()

#Creating dataframe as streamlit

def view_channels():
    channel_list = []

    db = client ["Youtube_dataharvesting"]
    collection = db ["channel_details"]

    for channel_data in collection.find({},{"_id":0,"channel_informations":1}):
        channel_list.append(channel_data["channel_informations"])

    df = st.dataframe(channel_list)

    return df


def view_playlist():
    play_list = []

    db = client ["Youtube_dataharvesting"]
    collection = db ["channel_details"]

    for playlist_data in collection.find({},{"_id":0,"playlist_informations":1}):
        for i in range(len(playlist_data["playlist_informations"])):
            play_list.append(playlist_data["playlist_informations"][i])

    playlist_df = st.dataframe(play_list)

    return playlist_df


def view_videos():
    video_list = []

    db = client ["Youtube_dataharvesting"]
    collection = db ["channel_details"]

    for video_data in collection.find({},{"_id":0,"video_informations":1}):
        for i in range(len(video_data["video_informations"])):
            video_list.append(video_data["video_informations"][i])

    video_df = st.dataframe(video_list)

    return video_df


def view_comments():
    comm_list = []

    db = client ["Youtube_dataharvesting"]
    collection = db ["channel_details"]

    for comment_data in collection.find({},{"_id":0,"comment_informations":1}):
        for i in range(len(comment_data["comment_informations"])):
            comm_list.append(comment_data["comment_informations"][i])

    comment_df = st.dataframe(comm_list)

    return comment_df



#Streamlit function
st.title("YOUTUBE DATA HARVESTING AND WAREHOUSING")
selected = option_menu(
    menu_title=None,
    options= ["Home", "Harvest", "Migrate", "Tables", "FAQs"],
    menu_icon=None,
    icons=None,
    orientation="horizontal"

    #styles={}
)

#Home

if selected == "Home":
    st.title("About")
    st.text("Hello")

#Harvest

if selected == "Harvest":
    channels = st.text_input("Enter Channel ID")

    if st.button("Harvest"):
        ch_id = []
        db = client["Youtube_dataharvesting"]
        collection = db["channel_details"]

        for ch_data in collection.find({},{"_id":0,"channel_informations":1}):
            ch_id.append(ch_data["channel_informations"]["Channel_id"])

        if channels in ch_id:
            st.success("Channel details exists")

        else:
            insert = channel_details(channels)
            st.success(insert)


#Migrate

if selected == "Migrate":

    chan_name = []
    db = client["Youtube_dataharvesting"]
    collection = db["channel_details"]
    
    for ch_data in collection.find({},{"_id":0,"channel_informations":1}):
            chan_name.append(ch_data["channel_informations"]["Channel_name"])

    selected_channel = st.selectbox("Select Channel to Migrate to SQL",
                           chan_name)
    
    st.write("You have Selected:", selected_channel)

    if st.button("Migrate"):
        table_fun = tables()
        st.success(table_fun)


#Tables
        
if selected == "Tables":

    show_table = st.radio("SELECT THE TABLE TO VIEW", ("CHANNELS", "PLAYLIST", "VIDEOS", "COMMENTS"))

    if show_table == "CHANNELS":
        view_channels()

    elif show_table == "PLAYLIST":
        view_playlist()

    elif show_table == "COMMENTS":
        view_comments()

    elif show_table == "VIDEOS":
        view_videos()


#FAQs
        
if selected == "FAQs":

    st.title("FAQs")
    
    mydb =  mysql.connector.connect(
            host = "localhost",
            user = "root",
            password = "NANANANA",
            database = "Youtube_dataharvesting"
            )

    cursor = mydb.cursor()

    ques = st.selectbox("Select the Question",("What are the names of all the videos and their corresponding channels?",
                        "Which channels have the most number of videos, and how many videos do they have?",
                        "What are the top 10 most viewed videos and their respective channels?",
                        "How many comments were made on each video, and what are their corresponding video names?",
                        "Which videos have the highest number of likes, and what are their corresponding channel names?",
                        "What is the total number of likes for each video, and what are their corresponding video names?",
                        "What is the total number of views for each channel, and what are their corresponding channel names?",
                        "What are the names of all the channels that have published videos in the year 2022?",
                        "What is the average duration of all videos in each channel, and what are their corresponding channel names?",
                        "Which videos have the highest number of comments, and what are their corresponding channel names?"))

    if ques == "What are the names of all the videos and their corresponding channels?":

            query = '''select title as videos,channel_name as chname from videos'''

            try:
                cursor.execute(query)
                q1 = cursor.fetchall()

                if q1:
                    df = pd.DataFrame(q1, columns=["Video", "Channel Name"])
                    st.write(df)
                else:
                    st.write("No Result Found")

                mydb.commit()

            except Exception as e:
                print("Error:", e)


    elif ques == "Which channels have the most number of videos, and how many videos do they have?":

        query2 = '''select channel_name as chname,videos_count as vcount from channels
                    order by videos_count desc'''

        try:
                cursor.execute(query2)
                q2 = cursor.fetchall()

                if q2:
                    df2 = pd.DataFrame(q2, columns=["Channel Name", "Total Videos"])
                    st.write(df2)
                else:
                    st.write("No Result Found")

                mydb.commit()

        except Exception as e:
            print("Error:", e)


    elif ques == "What are the top 10 most viewed videos and their respective channels?":

        query3 = '''select video_views as views,channel_name as chname,Title as vtitle from videos 
                    where video_views is not null order by video_views desc limit 10'''

        try:
                cursor.execute(query3)
                q3 = cursor.fetchall()

                if q3:
                    df3 = pd.DataFrame(q3, columns=["View count", "Channel Name", "Title"])
                    st.write(df3)
                else:
                    st.write("No Result Found")

                mydb.commit()

        except Exception as e:
            print("Error:", e)


    elif ques == "How many comments were made on each video, and what are their corresponding video names?":

        query4 = '''select video_comments as comments, title as vtitle from videos where video_comments is not null'''

        try:
                cursor.execute(query4)
                q4 = cursor.fetchall()

                if q4:
                    df4 = pd.DataFrame(q4, columns=["Comments", "Title"])
                    st.write(df4)
                else:
                    st.write("No Result Found")

                mydb.commit()

        except Exception as e:
            print("Error:", e)
                

    elif ques == "Which videos have the highest number of likes, and what are their corresponding channel names?":

        query5 = '''select title as vtitle,channel_name as chname,likes_count as likes from videos
                    where likes_count is not null order by likes_count desc'''

        try:
                cursor.execute(query5)
                q5 = cursor.fetchall()

                if q5:
                    df5 = pd.DataFrame(q5, columns=["Title", "Channel Name", "Likes"])
                    st.write(df5)
                else:
                    st.write("No Result Found")

                mydb.commit()

        except Exception as e:
            print("Error:", e)


    elif ques == "What is the total number of likes for each video, and what are their corresponding video names?":

        query6 = '''select title as vtitle,likes_count as likes from videos'''

        try:
                cursor.execute(query6)
                q6 = cursor.fetchall()

                if q6:
                    df6 = pd.DataFrame(q6, columns=["Title","Likes"])
                    st.write(df6)
                else:
                    st.write("No Result Found")

                mydb.commit()

        except Exception as e:
            print("Error:", e)


    elif ques == "What is the total number of views for each channel, and what are their corresponding channel names?":

        query7 = '''select channel_name as chname,views_count as views from channels'''

        try:
                cursor.execute(query7)
                q7 = cursor.fetchall()

                if q7:
                    df7 = pd.DataFrame(q7, columns=["Channel Name","Views"])
                    st.write(df7)
                else:
                    st.write("No Result Found")

                mydb.commit()

        except Exception as e:
            print("Error:", e)


    elif ques == "What are the names of all the channels that have published videos in the year 2022?":

        query8 = '''select title as vtitle,Published_on as published,channel_name as chname from videos
                    where extract(year from Published_on)=2022'''

        try:
                cursor.execute(query8)
                q8 = cursor.fetchall()

                if q8:
                    df8 = pd.DataFrame(q8, columns=["Title", "Published Date", "Channel Name"])
                    st.write(df8)
                else:
                    st.write("No Result Found")

                mydb.commit()

        except Exception as e:
            print("Error:", e)


    elif ques == "What is the average duration of all videos in each channel, and what are their corresponding channel names?":

        query9 = '''select channel_name as chname,AVG(video_duration) as averageduration from videos
                    group by channel_name'''

        try:
                cursor.execute(query9)
                result = cursor.fetchall()

                if result:
                    #df9 = pd.DataFrame(result, columns=["Channel Name", "Average Duration"])

                    duration = []
                    for entry in result:
                        channel_title = entry[0]
                        avg_duration = entry [1]
                        avg_duration_str = str(avg_duration)
                        duration.append({"Channel Name":channel_title, "Average Duration":avg_duration_str})

                    df9 = pd.DataFrame(duration)
                    st.write(df9)
                else:
                    st.write("No Result Found")

                mydb.commit()

        except Exception as e:
            print("Error:", e)


    elif ques == "Which videos have the highest number of comments, and what are their corresponding channel names?":


        query10 = '''select title as vtitle,channel_name as chname, video_comments as comments from videos
                    where video_comments is not null order by video_comments desc'''

        try:
                cursor.execute(query10)
                q10 = cursor.fetchall()

                if q10:
                    df10 = pd.DataFrame(q10, columns=["Title", "Channel Name", "Video Comments"])
                    st.write(df10)
                else:
                    st.write("No Result Found")

                mydb.commit()

        except Exception as e:
            print("Error:", e)