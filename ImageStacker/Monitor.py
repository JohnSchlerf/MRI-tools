import pygame
from pygame.locals import *

FLIP_DEFAULT = False

# I'm defining this to handle basic pygame initialization stuff and deal
# with the screen object in an easy-to-use way.

def loadImage(filename, colorkey=(0,0,0)):
    """Load an image from the image-directory."""
    if filename:
        image = pygame.image.load(filename)
        image = image.convert()
        if colorkey:
            image.set_colorkey(colorkey)
        return image

class Monitor:

    def __init__(self,width=1024,height=768,fullscreen=True,grabValue=1,textSize=40,mouseVisible=0):
        
        pygame.init()
        pygame.font.init()
        pygame.mouse.set_visible(mouseVisible)
        pygame.event.set_grab(grabValue)
        if fullscreen:
            self.myScreen = pygame.display.set_mode((width,height),FULLSCREEN)
        else:
            self.myScreen = pygame.display.set_mode((width,height))
        self.horizSize = width
        self.vertSize = height

        self.font = pygame.font.Font(None,textSize)

        # Using these speeds things up enormously
        self.rectlist = []
        self.blankrectlist = []

        self.horizFlipped = False
        self.vertFlipped = FLIP_DEFAULT

        self.textDic = {} # slightly speeds up drawText

    def blank(self,color=(0,0,0)):
        self.rectlist.append(self.myScreen.fill(color))
        #pygame.display.flip()
    def draw(self):
		pygame.display.update(self.rectlist)
    def flipHorizontal(self):
        self.horizFlipped = not(self.horizFlipped)

    def flipVertical(self):
        self.vertFlipped = not(self.vertFlipped)

    def update(self):
        pygame.display.update(self.blankrectlist+self.rectlist)
        #pygame.display.update(self.rectlist)
        self.blankrectlist = self.rectlist
        self.blankRects()
        self.rectlist = []

    def drawObject(self,imageObject,position):
        # draw an object centered on position

        # handle screen flipping
        if self.horizFlipped:
            position = [self.horizSize-position[0],position[1]]
        if self.vertFlipped:
            position = [position[0],self.vertSize-position[1]]

        # Get around deprecation warnings:
        position = [int(round(position[0])),int(round(position[1]))]
       
        width,height = imageObject.get_size()
        posAdj = [round(position[0]-width/2),round(position[1]-height/2)]
        self.rectlist.append(self.myScreen.blit(pygame.transform.flip(imageObject,self.horizFlipped,self.vertFlipped),posAdj))

    def blankRects(self,color=(0,0,0)):
        for rect in self.blankrectlist:
            self.myScreen.fill(color,rect)

    def drawFix(self,color,position,radius,width=2):
        # draws a circle with a cross in the center
        self.drawCircle(color,position,radius,width)
        self.drawLine(color,[position[0]-radius,position[1]],
                 [position[0]+radius,position[1]],width)
        self.drawLine(color,[position[0],position[1]-radius],
                 [position[0],position[1]+radius],width)

    def drawCircle(self,color,position,radius,width=0):
        # draw a circle.  Filled by default.

        # handle screen flipping
        if self.horizFlipped:
            position = [self.horizSize-position[0],position[1]]
        if self.vertFlipped:
            position = [position[0],self.vertSize-position[1]]
        
        # Get around deprecation warnings:
        position = [int(round(position[0])),int(round(position[1]))]
        radius = int(round(radius))
        width = int(round(width))
        
        self.rectlist.append(pygame.draw.circle(self.myScreen,color,\
                                                    position,radius,width))

    def fillRect(self,color=(0,0,0),rect=[0,0,0,0]):
        if self.horizFlipped:
            rect = [self.horizSize-(rect[0]+rect[2]),rect[1],rect[2],rect[3]]
        if self.vertFlipped:
            rect = [rect[0],self.vertSize-(rect[1]+rect[3]),rect[2],rect[3]]
        
        self.rectlist.append(self.myScreen.fill(color,rect))

    def drawLine(self,color,start_pos,end_pos,width=3):
        # draw a line.
                
        # handle screen flipping
        if self.horizFlipped:
            start_pos = [self.horizSize-start_pos[0],start_pos[1]]
            end_pos = [self.horizSize-end_pos[0],end_pos[1]]
        if self.vertFlipped:
            start_pos = [start_pos[0],self.vertSize-start_pos[1]]
            end_pos = [end_pos[0],self.vertSize-end_pos[1]]
        
        # Get around deprecation warnings:
        start_pos = [int(round(start_pos[0])),int(round(start_pos[1]))]
        end_pos = [int(round(end_pos[0])),int(round(end_pos[1]))]

        self.rectlist.append(pygame.draw.line(self.myScreen,color,
                                              start_pos,end_pos,width))

    def drawText(self,color,pos,text,defaultVertIsFlipped = FLIP_DEFAULT):
        #def blitText(self, text, x, y, color = (200, 200, 255), cache = True):
        """Draw (blit) text on the screen (self.screen). If cache is True, the
        text bitmap will be stored into textDic for reuse.
        """
        if not self.textDic.has_key(text+str(color)):
            self.textDic[text+str(color)] = self.font.render(text, 1, color)
        
        width,height = self.textDic[text+str(color)].get_size()
        
        # handle screen flipping
        if self.horizFlipped:
            pos = [self.horizSize-pos[0],pos[1]]
        if self.vertFlipped:
            pos = [pos[0],self.vertSize-pos[1]]
        
        pos = [int(round(pos[0]))-width/2,int(round(pos[1]))-height/2]
        
        self.rectlist.append(self.myScreen.blit(pygame.transform.flip(self.textDic[text+str(color)],
                                                                      self.horizFlipped,
                                                                      not(self.vertFlipped==defaultVertIsFlipped)),
                                                pos))
        
    def close(self):
        pygame.display.quit()
    def saveScreenShot(self,filename):
		pygame.image.save(self.myScreen,filename)
