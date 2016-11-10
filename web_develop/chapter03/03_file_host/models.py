# coding=utf-8
import os
import uuid
from datetime import datetime

try:
    from urllib import quote
except:
    from urllib.parse import quote

import cropresize2
import short_url
from flask import abort, request
from PIL import Image

from ext import db
from mimes import AUDIO_MIMES, IMAGE_MIMES, VIDEO_MIMES
from utils import get_file_path, get_file_md5
from werkzeug.utils import cached_property


class PasteFile(db.Model):
    __tablename__ = 'PasteFile'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(5000), nullable=False)
    filehash = db.Column(db.String(128), nullable=False, unique=True)
    filemd5 = db.Column(db.String(128), nullable=False, unique=True)
    uploadtime = db.Column(db.DateTime, nullable=False)
    mimetype = db.Column(db.String(256), nullable=False)
    size = db.Column(db.Integer, nullable=False)

    def __init__(self, filename='', mimetype='application/octet-stream',
                 size=0, filehash=None, filemd5=None):
        self.uploadtime = datetime.now()
        self.mimetype = mimetype
        self.size = int(size)
        self.filehash = filehash if filehash else self._hash_filename(filename)
        self.filename = filename if filename else self.filehash
        self.filemd5 = filemd5

    @staticmethod
    def _hash_filename(filename):
        _, _, suffix = filename.rpartition('.')
        return '%s.%s' % (uuid.uuid4().hex, suffix)

    @classmethod
    def get_by_md5(cls, filemd5):
        return cls.query.filter_by(filemd5=filemd5).first()

    @property
    def path(self):
        return get_file_path(self.filehash)

    @classmethod
    def create_by_upload_file(cls, uploaded_file):
        rst = cls(uploaded_file.filename, uploaded_file.mimetype, 0)
        uploaded_file.save(rst.path)
        with open(rst.path) as f:
            filemd5 = get_file_md5(f)
            uploaded_file = cls.get_by_md5(filemd5)
            if uploaded_file:
                os.remove(rst.path)
                return uploaded_file
        filestat = os.stat(rst.path)
        rst.size = filestat.st_size
        rst.filemd5 = filemd5
        return rst

    @property
    def quoteurl(self):
        return quote(self.url_i)

    @classmethod
    def rsize(cls, old_paste, weight, height):
        assert old_paste.is_image, TypeError('Unsupported Image Type.')

        img = cropresize2.crop_resize(
            Image.open(old_paste.path), (int(weight), int(height)))
        rst = cls(old_paste.filename, old_paste.mimetype, 0)
        img.save(rst.path)
        filestat = os.stat(rst.path)
        rst.size = filestat.st_size
        return rst

    @classmethod
    def get_by_filehash(cls, filehash, code=404):
        return cls.query.filter_by(filehash=filehash).first() or abort(code)

    def get_url(self, subtype, is_symlink=False):
        hash_or_link = self.symlink if is_symlink else self.filehash
        return 'http://{host}/{subtype}/{hash_or_link}'.format(
            subtype=subtype, host=request.host, hash_or_link=hash_or_link)

    @property
    def url_i(self):
        return self.get_url('i')

    @property
    def url_p(self):  # Preview.
        return self.get_url('p')

    @property
    def url_s(self):  # Short link.
        return self.get_url('s', is_symlink=True)

    @property
    def url_d(self):  # Download.
        return self.get_url('d')

    @cached_property
    def symlink(self):
        return short_url.encode_url(self.id)

    @classmethod
    def get_by_simlink(cls, symlink, code=404):
        id = short_url.decode_url(symlink)
        return cls.query.filter_by(id=id).first() or abort(code)

    @property
    def is_image(self):
        return self.mimetype in IMAGE_MIMES

    @property
    def is_audio(self):
        return self.mimetype in AUDIO_MIMES

    @property
    def is_video(self):
        return self.mimetype in VIDEO_MIMES

    @property
    def is_pdf(self):
        return self.mimetype == 'application/pdf'

    @property
    def type(self):
        for t in ('image', 'pdf', 'video', 'audio'):
            if getattr(self, 'is_' + t):
                return t
        return 'binary'
