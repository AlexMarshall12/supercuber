import re
import math
import itertools
import operator
import os
import json
import boto
import shortuuid
import struct

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



@view_config(route_name='home_page', renderer='templates/edit.pt')
def home_page(request):
    if 'form.submitted' in request.params:
        name= request.params['name']
       
        input_file=request.POST['stl'].file
        vertices, normals = [],[]
        if input_file.read(5) == b'solid':
            for line in input_file:
                parts = line.split()
                if parts[0] == 'vertex':
                    vertices.append(map(float, parts[1:4]))
                elif parts[0] == 'facet':
                    normals.append(map(float, parts[2:5]))

            ordering=[]
            N=len(normals)
            for i in range(0,N):
                ordering.append([3*i,3*i+1,3*i+2])
            data=[vertices,ordering]
        else:
            f=input_file
            f.seek(0)
            points=[]
            triangles=[]
            normals=[]
            def unpack (f, sig, l):
                s = f.read (l)
                
                return struct.unpack(sig, s)

            def read_triangle(f):
                n = unpack(f,"<3f", 12)
                p1 = unpack(f,"<3f", 12)
                p2 = unpack(f,"<3f", 12)
                p3 = unpack(f,"<3f", 12)
                b = unpack(f,"<h", 2)

                normals.append(n)
                l = len(points)
                points.append(p1)
                points.append(p2)
                points.append(p3)
                triangles.append((l, l+1, l+2))
                #bytecount.append(b[0])


            def read_length(f):
                length = struct.unpack("@i", f.read(4))
                return length[0]

            def read_header(f):
                f.seek(f.tell()+80)


            read_header(f)
            l = read_length(f)

            try:
                while True:
                   read_triangle(f)
            except Exception, e:
                print "Exception",e[0]
            
            #write_as_ascii(outfilename)
            data=[points,triangles]

            
        jsdata=json.dumps(data)
        renderer_dict = dict(name=name,data=jsdata)
        
        path=shortuuid.uuid()
        html_string = render('tutorial:templates/view.pt', renderer_dict, request=request)
        s3=boto.connect_s3(aws_access_key_id = 'AKIAIJEXF25B6H5F4L7Q', aws_secret_access_key = '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' )
        bucket=s3.get_bucket('cubes.supercuber.com')
        k=Key(bucket)
        k.key='%(path)s' % {'path':path}
        k.set_contents_from_string(html_string, headers={'Content-Type': 'text/html'})
        k.set_acl('public-read')

        return HTTPFound(location="http://cubes.supercuber.com/%(path)s" % {'path':path})

    return {}                                                       

