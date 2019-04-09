import json
from watson_developer_cloud import ToneAnalyzerV3
from bs4 import BeautifulSoup
import requests
import os
import time

tone_analyzer = ToneAnalyzerV3(
    version='2017-09-21',
    iam_apikey={apikey},
    url={url}
)

def music_data_grabber():
    # Importing the Billboard Top 100 URL
    page_link = 'https://www.billboard.com/charts/hot-100'
    page_response = requests.get(page_link, timeout=5)
    # Capturing the content from the Top 100
    page_content = BeautifulSoup(page_response.content, "html.parser")

    # Storing top 100 songs and artists
    top_100 = []

    # Grabbing the top song and artist of the week
    top_title = page_content.find('div', class_='chart-number-one__title').string
    top_artist = page_content.find('div', class_='chart-number-one__artist').get_text("|", strip=True)
    top_100.append([top_title, top_artist])

    # Grabbing the other 99 hits
    for chart_item in page_content.find_all('div', 'chart-list-item'):
        artist = chart_item['data-artist']
        title = chart_item['data-title']
        top_100.append([title, artist])

    # Base lyrics URL
    base_lyrics_url = 'https://www.azlyrics.com/lyrics/'

    # Sorting some tunes...
    sad_songs = []
    angry_songs = []
    joyful_songs = []
    confident_songs = []
    fearful_songs = []
    analytical_songs = []
    tentative_songs = []

    # For each song and artist pair, get the associated lyrics (5th div in a certain div)
    for song in top_100:
        time.sleep(10)
        title = song[0]
        artist = song[1]
        original_artist = song[1]

        # If artist is multiple in number, only list the primary one
        artist = artist.split('Featuring')[0]
        artist = artist.split(',')[0]
        artist = artist.split('&')[0]

        clean_title = ''.join(e for e in title if e.isalnum())
        clean_artist = ''.join(e for e in artist if e.isalnum())
        lyrics_url = base_lyrics_url + clean_artist.lower() + '/' + clean_title.lower() + '.html'

        lyrics_response = requests.get(lyrics_url, timeout=5)

        if lyrics_response.status_code == 200:
            lyrics_content = BeautifulSoup(lyrics_response.content, "html.parser")
            lyrics_wrapper = lyrics_content.find('div', class_='col-xs-12 col-lg-8 text-center')

            if lyrics_wrapper is not None:
                lyrics = lyrics_wrapper.find_all('div')[6].get_text()
                # Use the lyrics as input for the tone analyzer
                song_analysis = tone_analyzer.tone(
                    {'text': lyrics},
                    'application/json',
                    False
                ).get_result()

                # Some songs do not match the minimum threshold for tone detection (i.e. too many conflicting moods)
                # For now just ignoring those via this condition
                if song_analysis['document_tone']['tones']:
                    song_score = song_analysis['document_tone']['tones'][0]['score']
                    song_tone = song_analysis['document_tone']['tones'][0]['tone_name']

                print(title)

                # Take the score, tone_name, song name, and artist, and store these as [tone, score, song, artist]
                if song_tone == 'Sadness':
                    sad_songs.append([song_score, title, original_artist])
                elif song_tone == 'Anger':
                    angry_songs.append([song_score, title, original_artist])
                elif song_tone == 'Joy':
                    joyful_songs.append([song_score, title, original_artist])
                elif song_tone == 'Confident':
                    confident_songs.append([song_score, title, original_artist])
                elif song_tone == 'Fear':
                    fearful_songs.append([song_score, title, original_artist])
                elif song_tone == 'Analytical':
                    analytical_songs.append([song_score, title, original_artist])
                elif song_tone == 'Tentative':
                    tentative_songs.append([song_score, title, original_artist])
                else:
                    print(song_tone)


        else:
            print(page_response.status_code)
            # notify, try again




    # Now that the top 100 songs have been analyzed, print the data to a text file to minimize API calls.
    data = {
        'Sadness': sad_songs,
        'Anger': angry_songs,
        'Joy': joyful_songs,
        'Confident': confident_songs,
        'Fear': fearful_songs,
        'Analytical': analytical_songs,
        'Tentative': tentative_songs
    }

    with open('topsongs.txt', 'w') as file:
        file.write(json.dumps(data))


def analyzer():
    with open('topsongs.txt') as f:
        imported = json.load(f)
        # If the song data hasn't been grabbed yet, do so
        if os.stat("topsongs.txt").st_size == 0:
            music_data_grabber()
    # Prompt the user to input some text, use this as input to tone analyzer
    user_input = input("What's on your mind lately? ")

    user_analysis = tone_analyzer.tone(
        {'text': user_input},
        'application/json',
        False
    ).get_result()

    # Some songs do not match the minimum threshold for tone detection (i.e. too many conflicting moods)
    # For now just ignoring those via this condition
    if user_analysis['document_tone']['tones']:
        user_score = user_analysis['document_tone']['tones'][0]['score']
        user_tone = user_analysis['document_tone']['tones'][0]['tone_name']
        max_score = 0
        score_dif = 1
        song_name = ''
        song_artist = ''
        for song in imported[user_tone]:
            score = song[0]
            if abs(score - user_score) < score_dif:
                score_dif = abs(score - user_score)
                max_score = score
                song_name = song[1]
                song_artist = song[2]
        print('Your song is ', song_name, ' by ', song_artist, ' and we think you are feeling ', user_tone)



analyzer()

