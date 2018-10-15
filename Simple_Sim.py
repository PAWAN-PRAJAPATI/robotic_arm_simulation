from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import socket
import sys
import math
import pygame
import pickle
import time

#from mpurecieverpi import myThread_R,myThread_S

'''
s1 = socket.socket()
s2 = socket.socket()        
host = "127.0.0.1"
print(host)
port1 = int(sys.argv[1])
port2 = int(sys.argv[2])
s1.connect((host, port1))
s2.connect((host, port2))
#p1 elbow
#p2 shoulder
'''
#t = myThread_R()
#t1 = myThread_S()

class SimpleRobotArm:
        def __init__(self):

                self.angles=[90,0,225] #base shoulder elbow
                self.config=[0,0] #(thetha,beta),(xy,zx)
                self.anglstep=1
                self.xyz=[0.5,0.2,0.05]
                self.xyzstep=0.025
                self.name = "Simple Robot Arm"
                self.mode="reverse" # inverse reverse combat mouse
                # thresholds = [[base_l,base_h],[shoulder........],[elbow........]]
                self.thresh = [[-25, 200], [-30, 110], [190, 400]]
                self.r_max=1.32
                self.view="no_view"
                self.golax=0
                self.golay=0
                self.pos_c=[0,0]
                self.wheel_size=0.7
                self.claw=self.wrist=0
                self.host = "10.42.0.241"
                self.s1=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                self.s2=None



        def ret_ascii(self,i):
            s = str(i)
            ascii1 =int(s[0])+48
            ascii2 =int(s[1])+48
            return [ascii1,ascii2]
            glClear(GL_COLOR_BUFFER_BIT)

        def axis(self):
            glBegin(GL_LINES)
            glColor3f(0.3, 0.3, 0.3)
            glVertex3f(-10.0, 0.0, 0.0)
            glVertex3f(10.0, 0.0, 0.0)
            glVertex3f(0.0, -10.0, 0.0)
            glVertex3f(0.0, 10.0, 0.0)
            glVertex3f(0.0, 0.0, -10.0)
            glVertex3f(0.0, 0.0, 10.0)
            glEnd()

            biggest = 10
            x = 88
            y = 89
            z = 90
            r = range (0, (biggest + 1))
            for i in r:
                ascii = 48+i

                # x axis positive
                glRasterPos3f(i, 0.0, 0.0)
                glColor3f(0.3, 0.3, 0.3)
                if i == biggest:
                    glutBitmapCharacter(GLUT_BITMAP_8_BY_13, x)
                else:
                    glutBitmapCharacter(GLUT_BITMAP_8_BY_13, ascii)
                # x axis negative
                glRasterPos3f(-i, 0.0, 0.0)
                glColor3f(0.5, 0.0, 0.0)
                if i == biggest:
                    glutBitmapCharacter(GLUT_BITMAP_8_BY_13, x)
                else:
                    glutBitmapCharacter(GLUT_BITMAP_8_BY_13, ascii)

                # y axis positive
                glRasterPos3f(0.0, i, 0.0)
                glColor3f(0.3, 0.3, 0.3)
                if i == biggest:
                    glutBitmapCharacter(GLUT_BITMAP_8_BY_13, y)
                else:
                    glutBitmapCharacter(GLUT_BITMAP_8_BY_13, ascii)
                # x axis negative
                glRasterPos3f(0.0, -i, 0.0)
                glColor3f(0.5, 0.0, 0.0)
                if i == biggest:
                    glutBitmapCharacter(GLUT_BITMAP_8_BY_13, y)
                else:
                    glutBitmapCharacter(GLUT_BITMAP_8_BY_13, ascii)

                # z axis positive
                glRasterPos3f(0.0, 0.0, i)
                glColor3f(0.3, 0.3, 0.3)
                if i == biggest:
                    glutBitmapCharacter(GLUT_BITMAP_8_BY_13, z)
                else:
                    glutBitmapCharacter(GLUT_BITMAP_8_BY_13, ascii)
                # z axis negative
                glRasterPos3f(0.0, 0.0, -i)
                glColor3f(0.5, 0.0, 0.0)
                if i == biggest:
                    glutBitmapCharacter(GLUT_BITMAP_8_BY_13, z)
                else:
                    glutBitmapCharacter(GLUT_BITMAP_8_BY_13, ascii)

            glFlush()


        def run(self):

                glutInit(sys.argv)
                glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
                glutInitWindowSize(600, 800)
                glutInitWindowPosition(100, 100)
                glutCreateWindow(self.name)
                glClearColor(0.0, 0.0, 0.0, 0.0)
                glShadeModel(GL_FLAT)
                glutDisplayFunc(self.display)
                glutReshapeFunc(self.reshape)
                #glutKeyboardUpFunc(self.keys_up)
                glutKeyboardFunc(self.keys)
                #glutJoystickFunc(self.joystick,1)
                glutMainLoop()

        def wheel(self,radius, height, num_slices):
            r = radius
            h = height
            n = float(num_slices)

            circle_pts = []
            for i in range(int(n) + 1):
                angle = 2 * math.pi * (i/n)
                x = r * math.cos(angle)
                y = r * math.sin(angle)
                pt = (x, y)
                circle_pts.append(pt)

            glBegin(GL_TRIANGLE_FAN)#drawing the back circle
            glColor(0, 0, 1)
            glVertex(0, 0, h/2.0)
            for (x, y) in circle_pts:
                z = h/2.0
                glVertex(x, y, z)
            glEnd()

            glBegin(GL_TRIANGLE_FAN)#drawing the front circle
            glColor(0.25, 0.25, 0.25)
            glVertex(0, 0, h/2.0)
            for (x, y) in circle_pts:
                z = -h/2.0
                glVertex(x, y, z)
            glEnd()

            glBegin(GL_TRIANGLE_STRIP)#draw the tube
            glColor4f(0.6, 0.6, 0.6, 1)
            for (x, y) in circle_pts:
                z = h/2.0
                glVertex(x, y, z)
                glVertex(x, y, -z)
            glEnd()


        def display(self):
            

                try:
                    elb=t.run()
                    elb=elb.split(",")
                    self.angles[2]=int(elb[0])
                except Exception as e:
                    #print(e)
                    pass
                '''
                try:
                    sho=(self.s2.recv(1024).decode())
                    sho=sho.split(",")
                    self.angles[1]=int(sho[0])  
                except Exception as e:
                    print(e)
                    pass
                '''
                #print("sho:",sho)
                #print("elb:",elb)
                
                
                

                glClear(GL_COLOR_BUFFER_BIT);
                glPushMatrix();
                glTranslatef(0, -2, -7);
                glEnable(GL_BLEND)
                glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA);
                glRotatef(self.golax, 0, 1, 0);
                glRotatef(self.golay, 1, 0, 0);
                glColor4f(0.0,0.0,1.0,1)
                if(self.dis(self.xyz)>self.r_max):
                        glColor4f(1.0,0,0,0.5)

                glDisable(GL_BLEND)
                self.axis()
                glColor4f(0,0.4,0.4,0.5)
                glTranslatef(0, 0, 0);

                #if(self.angles[0]>self.thresh[0][1]-20 or self.angles[0]<self.thresh[0][0]+20):
                #       glColor4f(1.0,0,0,0.5)
                #bbb = self.angles[0] - 90
                #glRotatef(bbb, 0, 1, 0);
                glTranslatef(0, 0.0, 0.0);
                glPushMatrix();
                glScalef(10, 1, 5);
                glutSolidCube(0.5)
                glPopMatrix();


                glTranslatef (-2, 0, -2);
                self.wheel(self.wheel_size,self.wheel_size,20)
                glTranslatef (4, 0, 4);
                self.wheel(self.wheel_size,self.wheel_size,20)
                glTranslatef (0, 0, -4);
                self.wheel(self.wheel_size,self.wheel_size,20)
                glTranslatef (-4, 0, 4);
                self.wheel(self.wheel_size,self.wheel_size,20)

                ###
                glColor4f(0,0,1,0.5)
                glTranslatef(4.3, 0, -2);
                glPushMatrix();
                if(self.view=="view"):
                        glutWireSphere(3.14*1.8,25,25)
                glPopMatrix();
                #if(self.angles[0]>self.thresh[0][1]-20 or self.angles[0]<self.thresh[0][0]+20):
                #        glColor4f(1.0,0,0,0.5)
                bbb = self.angles[0] - 90
                glRotatef(bbb, 0, 1, 0);
                glTranslatef(-2, 0.0, 0.0);
                glPushMatrix();
                glScalef(10, 1, 5);
                glutWireCube(0.0)
                glPopMatrix();
                ###
                glColor4f(0.5,0.5,1.0,0.5)
                glTranslatef(2.5,0,0);
                #if(self.angles[1]>self.thresh[1][1]-20 or self.angles[1]<self.thresh[1][0]+20):
                #        glColor4f(1.0,0,0,0.5)

                glRotatef(self.angles[1], 0, 0.0, 1);
                glTranslatef(1, 0, 0.0);
                glPushMatrix();
                glScalef(2.0, 0.2, 0.5);
                glutSolidCube(1.1);
                glPopMatrix();

                glColor4f(1,0.5,0.5,0.5)
                glTranslatef(1.2, 0.0, 0.0);
                if(self.angles[2]>self.thresh[2][1]-20 or self.angles[2]<self.thresh[2][0]+20):
                        glColor4f(1.0,0,0,0.5)
                glRotatef(self.angles[2], 0.0, 0.0, 1.0);
                glTranslatef(1.2, 0.0, 0.0);
                glPushMatrix();
                glScalef(2.0, 0.2, 0.5);
                glutSolidCube(1.3);
                glPopMatrix();

                glColor4f(1,1,1,1)
                glTranslatef(1.3, 0.0, 0.0);
                glRotatef(self.wrist, 1, 0.0, 0);
                glTranslatef(0, 0.0, 0.0);
                glPushMatrix();
                glScalef(0.1, 0.2, 0.5);
                glutSolidCube(1.3);
                glPopMatrix();


                glColor4f(1,1,1,1)
                glTranslatef(0, 0.0, -0.34);
                glRotatef(self.claw, 0.0, 1, 0);
                glBegin(GL_TRIANGLES)       
                glVertex3f(0.5, 0, -0.4) 
                glVertex3f(1,0, 0.0)
                glVertex3f( 0,0, 0.0)
                glEnd()
                glRotatef(-self.claw, 0.0, 1, 0);


                glColor4f(1,1,1,1)
                glTranslatef(0, 0.0, 2*0.34);
                glRotatef(0, 0.0, 1, 0);
                glRotatef(-self.claw, 0.0, 1, 0);
                #glRotatef(self.claw, 0.0, 1, 0);
                glBegin(GL_TRIANGLES)      
                glVertex3f(0.5, 0, 0.4) 
                glVertex3f(1,0, 0.0)
                glVertex3f( 0,0, 0.0)
                glEnd()

                glPopMatrix();
                glutSwapBuffers();
                glutPostRedisplay()

        def reshape(self, w, h):

                glViewport(0, 0, w, h)
                glMatrixMode(GL_PROJECTION)
                glLoadIdentity()
                gluPerspective(65.0, w / h, 1.0, 20.0)
                glMatrixMode(GL_MODELVIEW)
                glLoadIdentity()
                glTranslatef(0.0, 0.0, -6.0)

        def view_mode(self,keys):

                if(keys=='4'.encode("utf-8")):
                        self.golax+=2
                elif(keys=='6'.encode("utf-8")):
                        self.golax-=2
                elif(keys=='8'.encode("utf-8")):
                        self.golay+=2
                elif(keys=='5'.encode("utf-8")):
                        self.golay-=2

        def apply(self,angles,xyz,angles_chg,xyz_chg):
                self.angles[0]=(angles[0]+angles_chg[0])%360
                self.angles[1]=(angles[1]+angles_chg[1])%360
                self.angles[2]=(angles[2]+angles_chg[2])%360
                self.xyz[0]=xyz[0]+xyz_chg[0]
                self.xyz[1]=xyz[1]+xyz_chg[1]
                self.xyz[2]=xyz[2]+xyz_chg[2]

        def dis(self,xyz):
                x,y,z=xyz
                s=(x**2+y**2+z**2)**(1/2)

                return (s)
        def angle_check(self,angles):
                if(self.thresh[0][0]<angles[0]<self.thresh[0][1] and self.thresh[1][0]<angles[1]<self.thresh[1][1] and
                    self.thresh[2][0]<angles[2]<self.thresh[2][1]):
                    return 1
                return 0


        def print_data(self):
          #print("Mode:",self.mode)
          #print("Angles:",self.angles)
          print("Wrist:",self.wrist)
          print("Claw:",self.claw)
	
        def keys(self,*args):
                #port1 = int(sys.argv[1])
                #port2 = int(sys.argv[2])
                keys=args[0]
                if(keys=='1'.encode("utf-8")):
                    '''
                    try:
                        self.s1.close()
                    except Exception as e:
                        print(e)
                        pass
                    '''
                 
                    #self.s1.connect((self.host, port1))
                    print("elbo connected!!!")
                if(keys==2):
                    try:
                        self.s2.close();
                       
                    except Exception as e:
                        print(e)
                        pass
                    self.s2 = socket.socket()
                    self.s2.connect((self.host, port2))
                    print("sho connected!!!")
                
                if(keys=='v'.encode("utf-8")):
                        self.view="view"
                elif(keys=='b'.encode("utf-8")):
                        self.view="no_view"
                elif(keys=='C'.encode("utf-8")):
                        self.golay=0
                        self.golax=0
                elif(keys=='+'.encode("utf-8")):
                        self.xyzstep+=0.025
                elif(keys=='-'.encode("utf-8")):
                        self.xyzstep-=0.025

                self.view_mode(keys)
                if(keys=='q'.encode("utf-8")):
                    self.apply(self.angles,self.xyz,[self.anglstep,0,0],[0,0,0])
                elif(keys=='a'.encode("utf-8")):
                    self.apply(self.angles,self.xyz,[-self.anglstep,0,0],[0,0,0])
                if(keys=='w'.encode("utf-8")):
                    self.apply(self.angles,self.xyz,[0,self.anglstep,0],[0,0,0])
                elif(keys=='s'.encode("utf-8")):
                    self.apply(self.angles,self.xyz,[0,-self.anglstep,0],[0,0,0])
                if(keys=='e'.encode("utf-8")):
                    self.apply(self.angles,self.xyz,[0,0,self.anglstep],[0,0,0])
                elif(keys=='d'.encode("utf-8")):
                    self.apply(self.angles,self.xyz,[0,0,-self.anglstep],[0,0,0])
                if(keys=='t'.encode("utf-8") and self.claw<=6):
                    self.claw=self.claw+2
                elif(keys=='g'.encode("utf-8") and self.claw>=-24):
                    self.claw=self.claw-2
                if(keys=='r'.encode("utf-8")):
                    self.wrist=self.wrist+2
                elif(keys=='f'.encode("utf-8")):
                    self.wrist=self.wrist-2
                
                print(self.print_data())
                glutPostRedisplay()




if __name__ == '__main__':
        app = SimpleRobotArm()
        #connect_arm()
        app.run()
