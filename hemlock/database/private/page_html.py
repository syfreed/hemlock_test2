"""Page html database model

Stores html snapshot of each Page for each Participant. These can be accessed
in the researcher dashboard.
"""

from hemlock.app.factory import db
from hemlock.database.types import MarkupType

from base64 import b64encode
from bs4 import BeautifulSoup
from flask import render_template
from flask_login import current_user
from io import BytesIO
from PIL import Image, ImageOps
import numpy as np
import os
import requests

# Video aspect ratio
ASPECT_RATIO = 16/9.0

# Padding tolerance parameters for video thumbnail
# Euclidean distance of pixel color from black
COLOR_TOLERANCE = 27
# Black percent of row or column to detect padding
PCT_PADDING = .95
# Max cropping when removing padding
MAX_CROP = 45


class PageHtml(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    part_id = db.Column(db.Integer, db.ForeignKey('participant.id'))
    css = db.Column(db.PickleType)
    html = db.Column(MarkupType)
    
    def __init__(self, page):
        self.css = page.css
        self.html = render_template(page.view_template, page=page)
        self.preprocess()
        
    def preprocess(self):
        self._process(preprocess=True)
        
    def process(self):
        self._process()
        return self.html
    
    def _process(self, preprocess=False):
        """Process html
        
        Store all images in base64 encoding. Store all videos as thumbnails.
        
        Convert only media to be copied for survey viewing during 
        preprocessing.
        """
        soup = BeautifulSoup(self.html, 'html.parser')
        images = soup.find_all('img')
        videos = soup.find_all('iframe')
        if preprocess:
            images = [i for i in images if i.has_attr('copy_for_viewing')]
            videos = [v for v in videos if v.has_attr('copy_for_viewing')]
        [self.encode_image(i) for i in images]
        [self.encode_video(soup, v) for v in videos]
        self.html = str(soup)
    
    def encode_image(self, image):
        """Encode an image as base64 data
        
        If the image is local, encode using the absolute path. If the image 
        is from a URL, encode content from request.
        """
        src = image['src']
        if src.startswith('/'): # local image
            path = os.path.join(os.getcwd(), src[1:]).replace('\\', '/')
            data = b64encode(open(path, 'rb').read()).decode('utf-8')
        elif src.startswith('http'): # from URL
            try:
                data = b64encode(requests.get(src).content).decode('utf-8')
            except:
                data = ''
        else:
            return
        image['src'] = 'data:image/png;base64,{}'.format(data)
    
    def encode_video(self, soup, video):
        """Encode video thumbnail as base64 data"""
        try:
            buffer = BytesIO()
            thumbnail = self.create_thumbnail(video)
            thumbnail.save(buffer, format='png')
            data = b64encode(buffer.getvalue()).decode('utf-8')
        except:
            data = ''
        image = soup.new_tag('img')
        image.attrs = video.attrs
        image['src'] = 'data:image/png;base64,{}'.format(data)
        video.replace_with(image)
        
    def create_thumbnail(self, video):
        """Create video thumbnail
        
        Get the raw thumbnail image. Then superimpose the YouTube play button.
        """
        thumbnail = self.get_thumbnail(video)

        path = os.path.join(os.getcwd(), 'static/YouTube.png')
        play = Image.open(path.replace('\\', '/'))
        thumbnail = thumbnail.resize(play.size)
        
        thumbnail.paste(play, (0,0), play)
        return thumbnail
    
    def get_thumbnail(self, video):
        """Get the raw video thumbnail from YouTube URL"""
        url = 'https://i4.ytimg.com/vi/{}/0.jpg'.format(video['vid'])
        thumbnail = Image.open(BytesIO(requests.get(url).content))
        thumbnail = self.remove_padding(thumbnail)
        thumbnail = self.fit_aspect(thumbnail)
        return thumbnail
        
    def remove_padding(self, thumbnail):
        """Remove black padding from the thumbnail"""
        width, height = thumbnail.size
        temp = np.linalg.norm(np.array(thumbnail)-np.array([0,0,0]), axis=2)
        temp = temp < COLOR_TOLERANCE
        min_y = 0
        while sum(temp[min_y]) > PCT_PADDING*width and min_y < MAX_CROP:
            min_y += 1
        max_y = thumbnail.size[1]-1
        while sum(temp[max_y])>PCT_PADDING*width and height-max_y<MAX_CROP:
            max_y -= 1
        thumbnail = thumbnail.crop((0, min_y, thumbnail.size[0], max_y))
        return thumbnail
    
    def fit_aspect(self, thumbnail):
        """Crop thumbnail to fit aspect ratio"""
        width, height = thumbnail.size
        crop_vertical = width/float(height) < ASPECT_RATIO
        if crop_vertical:
            new_width, new_height = width, width // ASPECT_RATIO
        else:
            new_width, new_height = round(height * ASPECT_RATIO), height
        delta_w, delta_h = new_width - width, -(new_height - height)
        crop = (delta_w//2, delta_h//2, width-delta_w//2, height-delta_h//2)
        return thumbnail.crop(crop)