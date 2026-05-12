"""
SQLAlchemy ORM Models untuk Pothole Detection
Database: MySQL
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Pothole(db.Model):
    """Model untuk menyimpan data deteksi jalan berlubang"""
    
    __tablename__ = 'potholes'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    confidence = db.Column(db.Float, nullable=False)  # 0.0 - 1.0
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    severity = db.Column(db.String(20), nullable=False, default='medium')  # high, medium, low
    description = db.Column(db.Text, nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    
    # Relationship
    alerts = db.relationship('Alert', backref='pothole', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert model ke dictionary"""
        return {
            'id': self.id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'confidence': round(self.confidence, 3),
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'severity': self.severity,
            'description': self.description,
            'user_agent': self.user_agent
        }
    
    def __repr__(self):
        return f'<Pothole id={self.id} severity={self.severity} lat={self.latitude} lon={self.longitude}>'


class UserLocation(db.Model):
    """Model untuk menyimpan lokasi tracking user"""
    
    __tablename__ = 'user_locations'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    speed = db.Column(db.Float, nullable=True, default=0)  # dalam m/s
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    accuracy = db.Column(db.Float, nullable=True)  # dalam meter
    
    def to_dict(self):
        """Convert model ke dictionary"""
        return {
            'id': self.id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'speed': round(self.speed, 2) if self.speed else 0,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'accuracy': round(self.accuracy, 2) if self.accuracy else None
        }
    
    def __repr__(self):
        return f'<UserLocation id={self.id} lat={self.latitude} lon={self.longitude}>'


class Alert(db.Model):
    """Model untuk menyimpan proximity alert history"""
    
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pothole_id = db.Column(db.Integer, db.ForeignKey('potholes.id'), nullable=False)
    distance_m = db.Column(db.Float, nullable=False)
    user_lat = db.Column(db.Float, nullable=False)
    user_lon = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    severity = db.Column(db.String(20), nullable=False)
    
    def to_dict(self):
        """Convert model ke dictionary"""
        return {
            'id': self.id,
            'pothole_id': self.pothole_id,
            'distance_m': round(self.distance_m, 1),
            'user_lat': self.user_lat,
            'user_lon': self.user_lon,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'severity': self.severity
        }
    
    def __repr__(self):
        return f'<Alert id={self.id} pothole_id={self.pothole_id} distance={self.distance_m}m>'


class DetectionHistory(db.Model):
    """Model untuk menyimpan history live detection"""
    
    __tablename__ = 'detection_history'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    frame_count = db.Column(db.Integer, nullable=False)
    num_detections = db.Column(db.Integer, nullable=False)
    avg_confidence = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    gps_latitude = db.Column(db.Float, nullable=True)
    gps_longitude = db.Column(db.Float, nullable=True)
    
    def to_dict(self):
        """Convert model ke dictionary"""
        return {
            'id': self.id,
            'frame_count': self.frame_count,
            'num_detections': self.num_detections,
            'avg_confidence': round(self.avg_confidence, 3),
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'gps_latitude': self.gps_latitude,
            'gps_longitude': self.gps_longitude
        }
    
    def __repr__(self):
        return f'<DetectionHistory id={self.id} detections={self.num_detections}>'
