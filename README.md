**Youtube data harvesting and warehousing**

**Introduction:**
Youtube Data Harvesting and Warehousing is a project that aims to allow users to access and analyze data from multiple youtube channels.This project involves creating a user friendly Streamlit application that utilizes the Google API to collect data from YouTube channels. The collected data is stored in MongoDB, and then transfered to a SQL database for analysis through Streamlit.

**Technologies Used:**
* Python Scripting
* API integration
* MongoDb
* SQL
* Streamlit

**Packages installed and used:**
* googleapiclient.discovery
* pymongo
* mysql connector
* pandas
* streamlit

**Features**
* **Retriving data:** This project uses Google API to collect the youtube data, such as channels, playllists, videos and comments.
* **Storing collected data:** In this project the collect data are stored in MongodB, based on their channel ID.
* **Migrating data to SQL:** The data stored in MongodB are been migrated to SQL, through the channe ID by the user. Here pandas has been used to segregate each information like channel details, playlist details, video details, comment details in a table formate using SQL queries.

**Conclusion:**
This project uses the Google API to collect, store and analyze data from YouTube channels, making it accessible through a user-friendly Streamlit application. Using MongoDB for initial storage and MySQL for structured data warehousing, users can seamlessly explore data. Through this project user can view and analize the channel activities seemlessly.


**User Interface**

![image](https://github.com/Akshayadp/Guvi-projects/assets/162536617/c711e5a5-52a8-47ba-9c43-0b1ba5090e27)


![image](https://github.com/Akshayadp/Guvi-projects/assets/162536617/e621d16f-782e-4d7b-9642-6f7c870fd99d)


![Screenshot 2024-03-10 031559](https://github.com/Akshayadp/Guvi-projects/assets/162536617/223c5646-0ffa-4fb0-8635-bec21070a267)


![image](https://github.com/Akshayadp/Guvi-projects/assets/162536617/44e481c6-363c-4a9a-bb56-58c75c21a207)

