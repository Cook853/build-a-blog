#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import jinja2
import hashutils

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blog(db.Model):
    title = db.StringProperty(required = True)
    entry = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
    def render_front(self):
        past_entries = db.GqlQuery("SELECT * FROM Blog "
                            "ORDER BY created DESC LIMIT 5 ")
        self.render("front.html", past_entries=past_entries)

    def get(self):
        self.render_front()

    def post(self):
        self.redirect("/blog")

class NewPostPage(Handler):
    def render_new_entry(self, title="", entry="", error=""):
        self.render("new-entry.html", title=title,
                    entry=entry, error=error)

    def get(self):
        self.render_new_entry()

    def post(self):
        title = self.request.get("title")
        entry = self.request.get("entry")

        if title and entry:
            a = Blog(title=title, entry=entry)
            a.put()
            route = a.key().id()
            self.redirect("/blog/{}".format(route))
        else:
            error = "we need both a title and an entry!"
            self.render_new_entry(title, entry, error)

class ViewPostHandler(Handler):
    def get(self, id):
        if Blog.get_by_id(int(id),parent=None):
            latest_entry = Blog.get_by_id(int(id),parent=None)
            self.response.write(latest_entry.title + '<br>' + latest_entry.entry +
                '<br>' + '<a href="/">Back to Your Blog</a>')
        else:
            error = "Entry does not exist"
            link = '<a href="/">Back to Your Blog</a>'
            self.response.write(error + '<br>' + link)

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/blog', MainPage),
    ('/newpost', NewPostPage),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)], debug=True)
