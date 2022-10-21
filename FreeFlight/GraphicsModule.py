import math
""" 
    // ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    This Module is a sample script for a GUI  

    Dev note: 
    just a sample script, not a full graphics system roll out.
    // -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    API Writen By:                                   Steven Andrews II
    Project By:                                   [[ Steven Andrews II ]]                                       - Fall 2022 
    // -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
""" 
   

class GM(object):
    """ Graphics interface """
    def __init__(   self    ,   pygame , FC ):
       self.pygame                      = pygame                                   
       self.compas_                 = pygame.image.load('compas_ind.png')
       self.drone_                  = pygame.image.load('drone_.png')
       self.ring_                   = pygame.image.load('ring.png')
       self.bat_                    = pygame.image.load('Bat.png')

       self.screen_ref              = pygame.display.get_desktop_sizes()
       self.screen_width            = self.screen_ref[0][0]
       self.screen_height           = self.screen_ref[0][1]
       self.screen_center_x         = self.screen_ref[0][0]/2
       self.screen_center_y         = self.screen_ref[0][1]/2
       self.screen                  = pygame.display.set_mode((500, 500),pygame.RESIZABLE)

       self.FC                      = FC
       self.TS                      = FC.communication  # import tombstone

       self.drone_yaw               = 0
       self.drone_bat               = 1

     
    # pygame makes this difficult 
    def draw_img(self, image, x, y, angle):
        rotated_image = self.pygame.transform.rotate(image, angle) 
        self.screen.blit(rotated_image, rotated_image.get_rect(center=image.get_rect(topleft=(x, y)).center).topleft)




    #-------------------------------------------------------------------------------------------------------------------
    # Internal updater: //  60 FPS
    #-------------------------------------------------------------------------------------------------------------------
    def update_(self):

        # screen data ( resizeable center ) 
        w,h             = self.pygame.display.get_surface().get_size()
        self.screen_center_x         = w/2
        self.screen_center_y         = h/2
        
    
        # background 
        self.pygame.draw.rect(self.screen, (150,0,255), self.pygame.Rect(0, 0, w, h))
 
        # grab telemetry from buffer 
        self.drone_yaw = self.TS.get_telem("yaw")
        self.drone_bat = self.TS.get_telem("bat")
   

        # battery from telemetry 
        if self.drone_bat != 0 :
            if int(self.drone_bat) > 75:
                self.pygame.draw.rect(self.screen, (0,255,0), self.pygame.Rect(self.screen_center_x - 200, self.screen_center_y+100, (int(self.drone_bat)/100)*100, 38))
            if int(self.drone_bat) <= 75 and int(self.drone_bat) >=50:
                self.pygame.draw.rect(self.screen, (255,191,0), self.pygame.Rect(self.screen_center_x - 200, self.screen_center_y+100, (int(self.drone_bat)/100)*100, 38))
            if int(self.drone_bat) < 50 and int(self.drone_bat) >=0:
                self.pygame.draw.rect(self.screen, (255,0,0), self.pygame.Rect(self.screen_center_x - 200, self.screen_center_y+100, (int(self.drone_bat)/100)*100, 38))


        # vector data 
        x           =   self.screen_center_x
        y           =   self.screen_center_y
        # callback to FC to grab the correct vector angles for the control mapping 
        direction_vector_angle , rotation_vector_angle  = self.FC.stick_vectorizatio()
        # vector points around a center point 
        if self.FC.channel_1_alive == True or self.FC.channel_0_alive == True :
            X_VECX =(  (self.FC.direction_mag*100)* math.sin( math.radians(  direction_vector_angle   ))  / math.sin( math.radians(90))    ) 
            X_VECY =(  (self.FC.direction_mag*100)* math.sin( math.radians(  180-90-direction_vector_angle  )) / math.sin( math.radians(90) ) ) 
            self.pygame.draw.line(self.screen, (0,255,0), (x,y), ( x - X_VECX ,y - X_VECY), width=8)
        if self.FC.channel_3_alive == True:
            Y_VECX =(  (self.FC.rotation_mag*100)* math.sin( math.radians(  rotation_vector_angle   ))  / math.sin( math.radians(90))    ) 
            Y_VECY =(  (self.FC.rotation_mag*100)* math.sin( math.radians(  180-90-rotation_vector_angle  )) / math.sin( math.radians(90) ) ) 
            self.pygame.draw.line(self.screen, (255,0,0), (x,y), ( x - Y_VECX ,y - Y_VECY), width=8) 



        # draw images ( rotate them about center points ) 
        self.draw_img(self.ring_   ,self.screen_center_x- (self.ring_.get_width()/2)   ,self.screen_center_y- (self.ring_.get_height()/2),  int(self.drone_yaw)*-1  )
        self.draw_img(self.drone_  ,self.screen_center_x- (self.drone_.get_width()/2)  ,self.screen_center_y- (self.ring_.get_height()/2),  int(self.drone_yaw)*-1  )
        # nomral pygame blit 
        self.screen.blit(self.bat_, ((self.screen_center_x - 200), self.screen_center_y+98))
        self.screen.blit(self.compas_, (self.screen_center_x- (self.compas_.get_width()/2) , self.screen_center_y- (self.compas_.get_height()/2)))
        # offscreen render flip 
        self.pygame.display.flip()
        
