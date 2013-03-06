import re
import math
import itertools
import operator
import os
import json
import boto

from docutils.core import publish_parts

from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    )
from pyramid.view import view_config
from pyramid.response import Response

from pyramid.renderers import render

from boto.s3.key import Key

from .models import (
    DBSession,
    Page,
    )

# regular expression used to find WikiWords
wikiwords = re.compile(r"\b([A-Z]\w+[A-Z]+\w+)")


@view_config(route_name='home_page', renderer='templates/edit.pt')
def home_page(request):
    if 'form.submitted' in request.params:
        name= request.params['name']
        body = request.params['body']
        input_file=request.POST['stl'].file
        vertices, normals = [],[]
        for line in input_file:
            parts = line.split()
            if parts[0] == 'vertex':
                vertices.append(map(float, parts[1:4]))
            elif parts[0] == 'facet':
                normals.append(map(float, parts[2:5]))

        ordering=[]
        N=len(normals)


        for i in range(0,N):
            p1=vertices[3*i]
            p2=vertices[3*i+1]
            p3=vertices[3*i+2]

            x1=p1[0]
            y1=p1[1]
            z1=p1[2]

            x2=p2[0]
            y2=p2[1]
            z2=p2[2]

            x3=p3[0]
            y3=p3[1]
            z3=p3[2]

            a=[x2-x1,y2-y1,z2-z1]
            b=[x3-x1,y3-y1,z3-z1]

            a1=x2-x1
            a2=y2-y1
            a3=z2-z1
            b1=x3-x1
            b2=y3-y1
            b3=z3-z1

            normal=normals[i]

            cross_vector=[a2*b3-a3*b2,a3*b1-a1*b3,a1*b2-a2*b1]
            dot=reduce( operator.add, map( operator.mul, cross_vector, normal))

            if dot>0:
                ordering.append([3*i,3*i+1,3*i+2])
            else:
                ordering.append([3*i,3*i+1,3*i+2])

        data=[vertices,ordering]
        jsdata=json.dumps(data)
        renderer_dict = dict(name=name,data=jsdata)
        html_string = render('tutorial:templates/view.pt', renderer_dict, request=request)
        s3=boto.connect_s3(aws_access_key_id = 'AKIAIJEXF25B6H5F4L7Q', aws_secret_access_key = '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' )
        bucket=s3.get_bucket('alexmarshalltest')
        k=Key(bucket)
        k.key='%(pagename)s' % {'pagename':name}
        k.set_contents_from_string(html_string, headers={'Content-Type': 'text/html'})
        return HTTPFound(location="https://s3.amazonaws.com/alexmarshalltest/%(pagename)s" % {'pagename':name})

    return {}                                                       

@view_config(route_name='view_page', renderer='templates/view.pt')
def view_page(request):
    pagename = request.matchdict['pagename']
    page = DBSession.query(Page).filter_by(name=pagename).first()
    if page is None:
        return HTTPNotFound('No such page')

    def check(match):
        word = match.group(1)
        exists = DBSession.query(Page).filter_by(name=word).all()
        if exists:
            view_url = request.route_url('view_page', pagename=word)
            return '<a href="%s">%s</a>' % (view_url, word)
        else:
            add_url = request.route_url('add_page', pagename=word)
            return '<a href="%s">%s</a>' % (add_url, word)

    content = publish_parts(page.data, writer_name='html')['html_body']
    content = wikiwords.sub(check, content)
    edit_url = request.route_url('edit_page', pagename=pagename)
    return dict(page=page, content=content, edit_url=edit_url)

@view_config(route_name='add_page', renderer='templates/edit.pt')
def add_page(request):
    name = request.matchdict['pagename']
    if 'form.submitted' in request.params:
        body = request.params['body']
        page = Page(name, body)
        DBSession.add(page)
        return HTTPFound(location = request.route_url('view_page',
                                                      pagename=name))
    save_url = request.route_url('add_page', pagename=name)
    page = Page('', '')
    return dict(page=page, save_url=save_url)

@view_config(route_name='edit_page', renderer='templates/edit.pt')
def edit_page(request):
    name = request.matchdict['pagename']
    page = DBSession.query(Page).filter_by(name=name).one()
    if 'form.submitted' in request.params:
        page.data = request.params['body']
        DBSession.add(page)
        return HTTPFound(location = request.route_url('view_page',
                                                      pagename=name))
    return dict(
        page=page,
        save_url = request.route_url('edit_page', pagename=name),
        )