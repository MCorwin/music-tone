import json
from watson_developer_cloud import ToneAnalyzerV3
from bs4 import BeautifulSoup
import requests
import pickle

tone_analyzer = ToneAnalyzerV3(
    version='2017-09-21',
    iam_apikey='dnXxkBJ0r2Qz7rSCKX3zkshJNNZiLJM1H6NMu6aRMfnV',
    url='https://gateway.watsonplatform.net/tone-analyzer/api'
)

# Importing the Billboard Top 100 URL
page_link = 'https://www.billboard.com/charts/hot-100'
page_response = requests.get(page_link, timeout=5)
# Capturing the content from the Top 100
page_content = BeautifulSoup(page_response.content, "html.parser")

# Storing top 100 songs and artists
top_100 = []

# Grabbing the top song and artist of the week
top_title = page_content.find('div', class_ = 'chart-number-one__title').string
top_artist = page_content.find('div', class_ = 'chart-number-one__artist').get_text("|", strip=True)
top_100.append([top_title, top_artist])

# Grabbing the other 99 hits
for chart_item in page_content.find_all('div', 'chart-list-item'):
    artist = chart_item['data-artist']
    title = chart_item['data-title']
    top_100.append([title, artist])

# Base lyrics URL
base_lyrics_url = 'https://www.azlyrics.com/lyrics/'

# FOR NOW ONLY HAVE 2 SONGS IN TOP_100
top_100 = top_100[0:2]

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
    lyrics_content = BeautifulSoup(lyrics_response.content, "html.parser")
    lyrics_wrapper = lyrics_content.find('div', class_ = 'col-xs-12 col-lg-8 text-center')

    if lyrics_wrapper is not None:
        lyrics = lyrics_wrapper.find_all('div')[6].get_text()
        # Use the lyrics as input for the tone analyzer
        song_analysis =  tone_analyzer.tone(
                        {'text': lyrics},
                        'application/json',
                        False
                    ).get_result()

        # Some songs do not match the minimum threshold for tone detection (i.e. too many conflicting moods)
        # For now just ignoring those via this condition
        if song_analysis['document_tone']['tones']:
            song_score = song_analysis['document_tone']['tones'][0]['score']
            song_tone = song_analysis['document_tone']['tones'][0]['tone_name']

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

with open('topsongs.txt') as f:
    imported = json.load(f)
    print(imported['Sadness'])

# Prompt the user to input some text, use this as input to tone analyzer

# Sort through the song tone results, find the closest matching one (i.e. tone = tone, min_diff b/w scores)

# Return the associated song title and artist
'''
tone_analyzer = ToneAnalyzerV3(
    version='2017-09-21',
    iam_apikey='dnXxkBJ0r2Qz7rSCKX3zkshJNNZiLJM1H6NMu6aRMfnV',
    url='https://gateway.watsonplatform.net/tone-analyzer/api'
)

text = 'Team, I know that times are tough! Product '\
    'sales have been disappointing for the past three '\
    'quarters. We have a competitive product, but we '\
    'need to do a better job of selling it!'

tone_analysis = tone_analyzer.tone(
    {'text': text},
    'application/json'
).get_result()
print(json.dumps(tone_analysis, indent=2))

'''


