from mymix import db


class Spotify_Artists(db.Model):
    id = db.Column(db.String, primary_key = True)
    track_name = db.Column(db.String)
    artist_names = db.Column(db.String)
    spotify_features = db.Column(db.String)
    web = db.Column(db.String)


    def __repr__(self):
        return "track name: %s \n artist names: %s \n features (spotify): %s \n song url: %s" %(self.track_name,self.artist_names,self.spotify_features,self.web)

    
class AZLyrics_Artists(db.Model):
    web = db.Column(db.String,primary_key = True)
    track_name = db.Column(db.String)
    artist_names = db.Column(db.String)
    lyrics = db.Column(db.String)

    def __repr__(self):
        return "track name: %s \n artist names: %s \n lyrics (AZLyrics): %s" %(self.track_name,self.artist_names,self.lyrics)

