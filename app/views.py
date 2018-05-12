# -*- coding: utf-8 -*-

import os
from pwgen import pwgen

from flask import render_template, request, send_from_directory, redirect, flash
from flask_admin import BaseView, expose
from flask_admin.contrib import sqla
from flask_security import current_user, utils
from wtforms.fields import PasswordField
from werkzeug import secure_filename

from database import db
from models import Media, Loop, LoopMedia, User
from utils import get_uploads_path, get_thumbnails_path, \
    resize_and_crop, is_content_type_allowed, get_media_type, activate_loop, \
    is_youtube_url, embed_url, video_id


class UserAdmin(sqla.ModelView):

    column_exclude_list = ('password')
    form_excluded_columns = ('password', 'folder')
    can_view_details = True
    column_auto_select_related = True
    column_hide_backrefs = False

    column_filters = [
        'email', 'name'
    ]

    def scaffold_list_columns(self):
        return ['id', 'active', 'roles', 'name',
                'email', 'password']

    def scaffold_sortable_columns(self):
        return {'id': User.id, 'name': User.name, 'email': User.email,
                'password': 'password'}

    def is_accessible(self):
        return current_user.has_role('admin')

    def scaffold_form(self):
        form_class = super(UserAdmin, self).scaffold_form()
        form_class.password2 = PasswordField('New Password')
        return form_class

    def on_model_change(self, form, model, is_created):
        if len(model.password2):
            model.password = utils.encrypt_password(model.password2)
        if is_created:
            if model.has_role('client'):
                model.folder = pwgen(16, symbols=False).lower()
                try:
                    os.makedirs(get_uploads_path(model.folder), 0x775)
                    os.makedirs(get_thumbnails_path(model.folder), 0x775)
                    # os.makedirs(get_loops_path(model.folder), 0x775)
                except:
                    raise OSError(
                        'Something went wrong when trying to'
                        'create account folders!')


class LoopModelView(sqla.ModelView):
    page_size = 10
    can_delete = False
    edit_template = 'admin/custom_edit_loop.html'
    list_template = 'admin/custom_list_loops.html'
    form_excluded_columns = ('media', 'folder', 'active')

    def is_accessible(self):
        return current_user.has_role('client')

    def load_loop_contents(self, loop_id):
        loop = Loop.query.get(loop_id)
        return loop.media

    def on_model_change(self, form, model, is_created):
        if not is_created:
            if model.active:
                activate_loop(current_user, model.id)
        else:
            model.user_id = current_user.id

    @expose('/activate/<int:loop_id>', methods=('GET', 'POST'))
    def activate(self, loop_id):
        loop = Loop.query.filter_by(id=loop_id, user_id=current_user.id).first()
        if loop:
            activate_loop(current_user, loop_id)
            flash('Sekvencia {} bola synchronizovaná so zariadením...'.format(loop.title))
            return redirect(self.get_url('loops.index_view'))
        else:
            # TODO 404
            return 'FORBIDDEN'

    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        media = Media.query.filter_by(
            user_id=current_user.id,
            deleted=False
        ).order_by(db.desc(Media.uploaded)).all()
        self._template_args['media'] = media
        self._template_args['loop_media'] = self.load_loop_contents(
            request.args.get('id')
        )
        return super(LoopModelView, self).edit_view()

    @expose('/put_media/<int:loop_id>', methods=('GET', 'POST'))
    def put_media(self, loop_id):
        media_ids = request.form.getlist('media_ids[]')
        loop = Loop.query.filter_by(id=loop_id, user_id=current_user.id).first()
        position = len(loop.media)
        i = 1
        for media_id in media_ids:
            loop.media.append(
                LoopMedia(media_id=media_id,
                          loop_id=loop_id,
                          position=position+i)
            )
            i = i + 1
        db.session.commit()
        return self.render('admin/loop_media.html', loop_media=loop.media)

    @expose(
        '/delete/<int:loop_id>/<int:relation_id>',
        methods=('GET', 'POST')
    )
    def delete_media(self, loop_id, relation_id):
        loop = Loop.query.filter_by(id=loop_id, user_id=current_user.id).first()
        relation = LoopMedia.query.get(relation_id)
        loop.media.remove(relation)
        db.session.commit()
        return self.render('admin/loop_media.html', loop_media=loop.media)

    @expose(
        '/update_relation_interval/<int:loop_id>/<int:relation_id>',
        methods=('GET', 'POST')
    )
    def update_relation_interval(self, loop_id, relation_id):
        relation = LoopMedia.query.get(relation_id)
        relation.interval = int(request.form.get('interval'))
        db.session.commit()
        loop = Loop.query.get(loop_id)
        return self.render('admin/loop_media.html', loop_media=loop.media)

    @expose(
        '/update_order/<int:loop_id>',
        methods=('GET', 'POST')
    )
    def update_order(self, loop_id):
        data = request.form.get('data')
        data = data.replace('item[]=', ',')
        data = data.replace('&', '')
        data = data.split(',')
        data.pop(0)
        loop = Loop.query.filter_by(id=loop_id, user_id=current_user.id).first()
        for item in loop.media:
            item.position = data.index(str(item.id)) + 1
        db.session.commit()
        loop = Loop.query.get(loop_id)
        return self.render('admin/loop_media.html', loop_media=loop.media)


class UploadsView(BaseView):

    def is_accessible(self):
        return current_user.has_role('client')

    @expose('/')
    def index(self):
        media = Media.query.filter_by(
            user_id=current_user.id,
            deleted=False
        ).order_by(db.desc(Media.uploaded)).all()
        return self.render('admin/uploads.html', media=media)

    @expose('/get/<string:filename>', methods=['GET'])
    def get_file(self, filename):
        media = Media.query.filter_by(filename=filename).first()
        if media.type == 'url':
            return redirect(media.url)
        return send_from_directory(
            get_uploads_path(current_user.folder),
            filename
        )

    @expose('/get/thumbnail/<string:filename>', methods=['GET'])
    def thumbnail(self, filename):
        thumbnail_path = get_thumbnails_path(current_user.folder)
        try:
            return send_from_directory(thumbnail_path, filename)
        except:
            media = Media.query.filter_by(filename=filename).first()
            if media:
                orig_file = '/'.join([get_uploads_path(current_user.folder), filename])
                thumb_file = '/'.join([get_thumbnails_path(current_user.folder), filename])
                if media.type == "image":
                    resize_and_crop(orig_file, thumb_file, (120, 90))
                if media.type == "video":
                    return send_from_directory('static/img', 'video.png')
                if media.type == "url":
                    return redirect("https://img.youtube.com/vi/" + video_id(media.url) + "/1.jpg")
            return send_from_directory(thumbnail_path, filename)

    @expose('/put', methods=['POST'])
    def upload(self):
        if request.method == 'POST':
            target = get_uploads_path(current_user.folder)
            upload = request.files['files[]']
            if not is_content_type_allowed(upload.content_type):
                return ''
            orig_filename = secure_filename(upload.filename.rsplit("/")[0])
            fn, fext = os.path.splitext(orig_filename)
            filename = pwgen(16, symbols=False).lower() + fext
            destination = "/".join(
                [target, filename]
            )
            media_type = get_media_type(upload.content_type)
            media = Media(
                user_id=current_user.id,
                title=orig_filename,
                filename=filename,
                type=media_type,
                deleted=False)
            db.session.add(media)
            db.session.commit()
            upload.save(destination)
            return render_template("admin/media_item.html", media=media)

    @expose('/put_url', methods=['POST'])
    def put_url(self):
        if request.method == 'POST':
            url = request.form.get('url')
            if is_youtube_url(url):
                media = Media(
                    user_id=current_user.id,
                    title=embed_url(url),
                    url=embed_url(url),
                    filename=pwgen(16, symbols=False).lower(),
                    type="url",
                    deleted=False)
                db.session.add(media)
                db.session.commit()
                return render_template("admin/media_item.html", media=media)
            else:
                return ''

    @expose('/delete/<path:filename>', methods=['POST'])
    def delete_file(self, filename):
        media_item = Media.query.filter_by(
            user_id=current_user.id, filename=filename).first()
        media_item.deleted = True
        db.session.commit()
        media = Media.query.filter_by(
            user_id=current_user.id, deleted=False
        ).order_by(db.desc(Media.uploaded)).all()
        return render_template("admin/media.html", media=media)
