# Na podstawie: http://www.pygame.org/wiki/OBJFileLoader

import OpenGL.GL as gl
import os

class ModelLoader(object):
    def __init__(self, filename):
        self.verticles = []
        self.normals = []
        self.faces = []
        self.mtl = {}
        #todo przerob
        self.load(filename)

    def load(self, filename):
        material = None
        for line in open(filename).readlines():
            if line.startswith('#'):
                continue
            parts = line.strip().split()
            if not parts:
                continue
            if parts[0] == 'v':
                v = map(float, parts[1:4])
                self.verticles.append(v)
            elif parts[0] == 'vn':
                n = map(float, parts[1:4])
                self.normals.append(n)
            elif parts[0] == 'usemtl':
                material = parts[1]
            elif parts[0] == 'mtllib':
                self.mtl = self.parse_mtl(parts[1])
            elif parts[0] == 'f':
                face = []
                texcoords = []
                norms = []
                for v in parts[1:]:
                    w = v.split('/')
                    face.append(int(w[0]))
                    if len(w) >= 2 and len(w[1]) > 0:
                        texcoords.append(int(w[1]))
                    else:
                        texcoords.append(0)
                    if len(w) >= 3 and len(w[2]) > 0:
                        norms.append(int(w[2]))
                    else:
                        norms.append(0)
                self.faces.append((face, norms, texcoords, material))

    def paint(self):
        self.gl_list = gl.glGenLists(1)
        gl.glNewList(self.gl_list, gl.GL_COMPILE)
        gl.glEnable(gl.GL_TEXTURE_2D)
        gl.glFrontFace(gl.GL_CCW)
        for face in self.faces:
            vertices, normals, texture_coords, material = face

            mtl = self.mtl[material]
            if 'texture_Kd' in mtl:
                # use diffuse texmap
                gl.glBindTexture(gl.GL_TEXTURE_2D, mtl['texture_Kd'])
            else:
                # just use diffuse colour
                gl.glColor(*mtl['Kd'])

            gl.glBegin(gl.GL_POLYGON)
            for i in range(len(vertices)):
                if normals[i] > 0:
                    gl.glNormal3fv(self.normals[normals[i] - 1])
                if texture_coords[i] > 0:
                    gl.glTexCoord2fv(self.texcoords[texture_coords[i] - 1])
                gl.glVertex3fv(self.vertices[vertices[i] - 1])
            gl.glEnd()
        gl.glDisable(gl.GL_TEXTURE_2D)
        gl.glEndList()

    def parse_mtl(self, filename):
        mtl = {}
        for line in open(filename).readlines():
            if line.startswith("#"):
                continue
            parts = line.strip().split()
            if not parts:
                continue
            if parts[0] == "newmtl":
                mtl['name'] = parts[1]
            elif parts[0] in ('Ka', "Kd", "Ks", "Ke"):
                v = map(float, parts[1:4])
                mtl[parts[0]] = v
            elif parts[0] in ('Ns', "Ni", 'd', 'illum'):
                v = float(parts[1])
                mtl[parts[0]] = v
        return mtl
