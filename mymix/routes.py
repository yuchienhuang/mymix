from flask import request, render_template, redirect, url_for, flash
#from werkzeug import secure_filename
import json
from mymix import app, db
from mymix.models import Spotify_Artists, AZLyrics_Artists
from mymix.azlyrics import *
from mymix.spotify import *
from mymix.audioAnalysis import *




ALLOWED_EXTENSIONS = set(['wav'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def homepage():
    
    

    try:
        features_data = Spotify_Artists.query.all()
        
        features_list = []
        for o in features_data:
            features_list.append({"id":o.id,"track_name":o.track_name,"artist_names":o.artist_names,"spotify_features":o.spotify_features,"web":o.web})
        
        others_data = AZLyrics_Artists.query.all()

        others_list = []
        for o in others_data:
            #others_list.append({"web":o.web,"track_name":o.track_name,"artist_names":o.artist_names,"lyrics":o.lyrics})
            others_list.append({"web":o.web,"track_name":o.track_name,"artist_names":o.artist_names})
        
        data = json.dumps([features_list,others_list])
        
    
    except: 
        data = json.dumps("")
        

    return render_template('index.html', data=data)




@app.route('/best_cover_versions')
def bestcovers():
    return render_template('bestcovers.html')


@app.route('/search', methods=['GET'])
def search():
    
    return_string = ""

    track_name =  request.args['song']
    track_artist_names = request.args['artist']

 
    tracks = search_tracks(track_name)
    
    tracks = [track for track in tracks if track['name'].split('-')[0].strip().lower() == track_name.lower()]
    
    tracks_artistnames = [track["artists"][0]['name'].strip().lower() for track in tracks]
    

    #filtered_labels, other_cover_versions = lyrics_filter(track_name, tracks_artistnames)
    #tracks = [tracks[i] for i in filtered_labels]
    cover_versions = all_versions(track_name, track_artist_names)
    
    if len(cover_versions) == 0:
        db.drop_all()
        return "not sure {} has covered {}...".format(track_artist_names,track_name)

    lyrics_filtered_tracks = []
    lyrics_filtered_artistnames = []
    
    for i, track in enumerate(tracks):
        if tracks_artistnames[i] in cover_versions:
            lyrics_filtered_tracks.append(track)
            lyrics_filtered_artistnames.append(tracks_artistnames[i])

        

    tracks_features = get_audio_features(lyrics_filtered_tracks, lyrics_filtered_artistnames)
    try:
        tracks_keys = tracks_features.keys()
    except:
        tracks_keys = []
        

    # global features_json 
    # features_json = json.dumps(tracks_features)


    db.drop_all()
    db.create_all()
    
    for key in tracks_keys:
        db.session.add(Spotify_Artists(id=key, track_name=track_name, artist_names=tracks_features[key][0], web=tracks_features[key][2], spotify_features=str(tracks_features[key][1])))
    db.session.commit()
    
    no_spotify_versions = list(cover_versions - set(lyrics_filtered_artistnames))

    for v in no_spotify_versions:
        
        url = get_lyrics_url(v,track_name)
        #db.session.add(AZLyrics_Artists(web=url, track_name=track_name, artist_names=v, lyrics=get_lyrics(url)))
        db.session.add(AZLyrics_Artists(web=url, track_name=track_name, artist_names=v))
    db.session.commit()
    
    
    
    return return_string
    #return json.dumps(no_spotify_versions)
    #return json.dumps([{key: tracks_features[key][0] for key in tracks_keys}, no_spotify_versions])


@app.route("/features/<string:id>", methods=['GET', 'POST'])
def track_features(id):
    
    # posts = json.loads(features_json)[id]
    track_features = Spotify_Artists.query.get(id)

    

    return render_template('features.html', track_features = track_features)

@app.route('/audio_analysis/uploader', methods = ['GET', 'POST'])
def upload_file():
#    if request.method == 'POST':
#       f = request.files['file']
#       f.save(secure_filename(f.filename))
#       return 'file uploaded successfully'

    # check if the post request has the file part
    if 'file' not in request.files:
        
        return render_template('audioanalysis.html')
    file = request.files['file']
    # if user does not select file, browser also
    # submit a empty part without filename
    if file.filename == '':
        
        return render_template('audioanalysis.html')
    if file and allowed_file(file.filename):
        #filename = secure_filename(file.filename)
        path1 = os.path.join(app.root_path, 'public/uploaded_audio_files', 'audio_file_1.wav')
        path2 = os.path.join(app.root_path, 'public/uploaded_audio_files', 'audio_file_2.wav')

        if os.path.exists(path1) and os.path.exists(path2):
            os.remove(path2)
            file.save(path1)
        elif not os.path.exists(path1) and not os.path.exists(path2):
            file.save(path1)
        else:
            file.save(path2)
            

        return render_template('audioanalysis.html')
        #return 'the file uploaded successfully'


@app.route('/background_process_test', methods = ['GET', 'POST'])
def background_process_test():
    return_string = generate_plots()
    
    return return_string

@app.route('/audio_analysis')
def audioanalysis():
    return render_template('audioanalysis.html')



