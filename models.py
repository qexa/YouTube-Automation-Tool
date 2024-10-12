from app import db

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    transcription = db.Column(db.Text)
    summary = db.Column(db.Text)
    playlist = db.Column(db.String(100))
    hierarchical_number = db.Column(db.String(20), unique=True, nullable=False)

    def __repr__(self):
        return f'<Video {self.title}>'
