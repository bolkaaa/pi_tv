from flask import current_app
from PIL import Image
import re

from database import db
from models import Loop


def activate_loop(user, loop_id):
    account_loops = Loop.query.filter_by(user_id=user.id).all()
    for loop in account_loops:
        loop.active = False
    loop = Loop.query.get(loop_id)
    loop.active = True
    with open('/'.join([get_media_path(), 'playlist']), 'w') as playlist_file:
        for item in loop.media:
            playlist_file.write("{}@{}@{}\n".format(
                item.media.filename if item.media.type != 'url' else item.media.url,
                item.media.type,
                item.interval
            ))
    db.session.commit()


def is_content_type_allowed(content_type):
    if content_type.startswith('image'):
        return True
    if content_type.startswith('video'):
        return True
    return False


def get_media_type(content_type):
    if content_type.startswith('image'):
        return 'image'
    if content_type.startswith('video'):
        return 'video'


def get_media_path():
    return '/'.join(
        [current_app.config['STATIC_FOLDER'],
         current_app.config['MEDIA_FOLDER']]
    )


def get_uploads_path(account_dirname):
    return '/'.join(
        [current_app.config['STATIC_FOLDER'],
         current_app.config['MEDIA_FOLDER'],
         # account_dirname,
         current_app.config['UPLOADS_FOLDER']]
    )


def get_thumbnails_path(account_dirname):
    return '/'.join(
        [current_app.config['STATIC_FOLDER'],
         current_app.config['MEDIA_FOLDER'],
         # account_dirname,
         current_app.config['UPLOADS_FOLDER'],
         'thumbnails'],
    )


def resize_and_crop(img_path, modified_path, size, crop_type='middle'):
    img = Image.open(img_path)
    img_ratio = img.size[0] / float(img.size[1])
    ratio = size[0] / float(size[1])
    if ratio > img_ratio:
        img = img.resize(
            (size[0], round(size[0] * img.size[1] / img.size[0])),
            Image.ANTIALIAS
        )
        if crop_type == 'top':
            box = (0, 0, img.size[0], size[1])
        elif crop_type == 'middle':
            box = (0, round((img.size[1] - size[1]) / 2), img.size[0],
                   round((img.size[1] + size[1]) / 2))
        elif crop_type == 'bottom':
            box = (0, img.size[1] - size[1], img.size[0], img.size[1])
        else:
            raise ValueError('ERROR: invalid value for crop_type')
        img = img.crop(box)
    elif ratio < img_ratio:
        img = img.resize(
            (round(size[1] * img.size[0] / img.size[1]), size[1]),
            Image.ANTIALIAS
        )
        if crop_type == 'top':
            box = (0, 0, size[0], img.size[1])
        elif crop_type == 'middle':
            box = (round((img.size[0] - size[0]) / 2), 0,
                   round((img.size[0] + size[0]) / 2), img.size[1])
        elif crop_type == 'bottom':
            box = (img.size[0] - size[0], 0, img.size[0], img.size[1])
        else:
            raise ValueError('ERROR: invalid value for crop_type')
        img = img.crop(box)
    else:
        img = img.resize((size[0], size[1]), Image.ANTIALIAS)
    img.save(modified_path)


def is_youtube_url(url):
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
    youtube_regex_match = re.match(youtube_regex, url)
    if youtube_regex_match:
        return youtube_regex_match.group(6)
    return youtube_regex_match


def embed_url(url):
    regex = r"(?:https:\/\/)?(?:www\.)?(?:youtube\.com|youtu\.be)\/(?:watch\?v=)?(.+)"
    return re.sub(regex, r"https://www.youtube.com/embed/\1", url)


def video_id(url):
    regex = r'((?<=(v|V)/)|(?<=be/)|(?<=(\?|\&)v=)|(?<=embed/))([\w-]+)'
    match = re.search(regex, url)
    try:
        return match.group(0)
    except:
        return ''
