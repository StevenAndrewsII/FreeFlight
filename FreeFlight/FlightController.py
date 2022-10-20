# locad PYsockets
import socket
import threading
from   threading import Thread

class TombStone(object):
    '''      Communication API       '''
    """ 
    // ----------------------------------------------------------------------------------------------------------------------------

    This module is created as an alternative communications layer for the DJI Tello drone   ( demo: alpha ) 

    -------------------------------------------------------------------------------------------------------------------------------
    BaceEnd:

            downlink_com            (   port   )                    Thread : Down data tranmissions from drone  ( ok + responses )
            downlink_telemetry      (   port   )                    Thread : Telemetry data from Drone
            uplink                  (   DATA   ,   Bool  )          Up data to the drone ( bool = ping hold ) 
            connection_             (   N/A    )                    Connection state machine - 120 FPS ( called in FC ) 
            telem_buffer            (   N/A    )                    Buffers telemetry data from the socket ( empty if not receiving ) 


    Utility ( front side ): 

            disconnect              (     N/A     )                    Disconnect toggle 
            get_telem               (  search id  )                    get a telemtry state from the buffer 

    // ----------------------------------------------------------------------------------------------------------------------------
    Writen  By:                                     Steven Andrews II
    Project By:                                  [[ Steven Andrews II ]] 
    // 
    -------------------------------------------------------------------------------------------------------------------------------
    """ 



    '''Buffer:     Telemetry parsing buffer     '''
    def telem_buffer(self):
        self.TELEMETRY__    =   {} 
        for _ in  self.telemetry_keys:
            for i in self.raw_telemetry :
                k_          =   i.split(":")
                key_        =   k_[0]
                if key_ == _ :       
                    self.TELEMETRY__[key_] = k_[1]   
            


    '''Utility:    Get telemetry from the buffer    '''
    def get_telem(self,search):  
         for k,v in self.TELEMETRY__.items():
             if k == search:
                 return v                          
         return False           
        
   
   
    '''Socket:      UDP Respons Receive Thread   ( receives responses from commands )   '''
    def downlink_com(self_,port):
        while True:
            if self_.connection_data["connection_toggle"] == True and self_.downlink_hold == False:
                try: 
                        DATA    ,  ADDRESS      = self_.client_socket.recvfrom(   port   ) 
                        self_.incoming          = True
                except socket.error as error_ :
                    print("Error: in downlink_com")                                        



    '''Socket:      Receives telemetry information from the drone      '''
    def downlink_telemetry(self_,port):
        while True:
            if self_.connection_data["connection_toggle"] == True and self_.downlink_hold == False :
                try:
                        DATA    ,  ADDRESS      =  self_.client_state_socket.recvfrom(   port   ) 
                        DATA                    =  DATA.decode(  'ASCII'  )
                        self_.raw_telemetry     =  DATA.split(";")
                        if self_.hold           == True:     
                           self_.incoming       =  True
                           self_.hold           =  False
                except socket.error as error_ :
                        print("Error: downlink_telemetry") 
               


    '''Socket:      Outgoing packet handler    '''
    def uplink(self,DATA,*arg):
        if  self.connection_data["connection_toggle"] == True:
            self.hold             = False or bool(  arg  )   
            try:
               PACKET             = str.encode(   DATA   )
               self.client_socket.sendto(  PACKET , self.DRONE_address  )  
            except socket.error:
                print("outgoing: socket error")
    


    '''Utility:      Quick toggle comunications off   '''
    def disconnect(self):
        if  self.connection_data["connection_toggle"]           == False:
            self.connection_data["connection_toggle"]           = True
            self.connection_data["connection_state"]            = False
            socket.socket .close(self.client_socket )                    
            socket.socket .close(self.client_state_socket )
            return  True
        else:
            self.connection_data["connection_toggle"]           = False
            return  True



    '''Handler:      Establish Connection and track state    '''
    def connection_(self):      
       if  self.connection_data["connection_toggle"]  == True:      
           self.connection_data["ping_clk"]                                 =  self.connection_data["ping_clk"]    +   1
           #     disconnection detection 
           if self.connection_data["connection_state"] == True and self.connection_data["conCheck_index"] > self.connection_data["conCheck_Mindex"]:
              self.connection_data["conCheck_index"]                        = 0
              self.connection_data["connection_state"]                      = False
              print("Drone connection has been severed...")
           
           #     AUto bind to local host 
           if self.connection_data["connection_state"] == False and self.connection_data["conCheck_index"] > self.connection_data["conCheck_Mindex"]:
              self.downlink_hold                                            = True
              socket.socket .close(self.client_socket )                     # clear socket objects 
              socket.socket .close(self.client_state_socket )
              print("Grabbing local host ip:",self.host_name,self.local_ip)
              self.host_name              = socket. gethostname()                                                          
              self.local_ip               = socket. gethostbyname( self.host_name )
              self.CMDsoc                 = socket. socket(  socket.AF_INET , socket.SOCK_DGRAM  )                         
              self.telemetry              = socket. socket(  socket.AF_INET , socket.SOCK_DGRAM  )                         
              self.CMDsoc          .bind(  (   self.local_ip ,  self.UDP_control_port         )  )
              self.telemetry       .bind(  (   ""            , self.UDP_state_port            )  )
              self.client_socket                                            = self.CMDsoc                                    
              self.client_state_socket                                      = self.telemetry                               
              self.connection_data["conCheck_index"]                        = 0
              self.downlink_hold                                            = False

           #    connection ping 
           if self.connection_data["ping_clk"] >= (self.connection_data["ping_MClk"]/2):
               if self.connection_data["connection_sub_state"] == False:
                  # Hold: holds the command uplink if streaming data ( telemetry downlink keeps the connection state open )
                  if self.hold  != True:
                        print       (   "Ping..."   ) 
                        self.uplink (   "command"   )

                  self.connection_data["conCheck_index"]                    = self.connection_data["conCheck_index"]   +  1
                  self.connection_data["connection_sub_state"]              = True    
                  
           # time out 
           if self.connection_data["ping_clk"] >= (self.connection_data["ping_MClk"]) :
                  self.hold                                                 = False
                  self.connection_data["connection_sub_state"]              = False
                  self.connection_data["ping_clk"]                          = 0

           # incoming data // reset state machine        
           if self.incoming == True: 
                self.connection_data["connection_state"]                    = True    
                self.connection_data["ping_clk"]                            = 0
                self.connection_data["connection_sub_state"]                = False
                self.connection_data["conCheck_index"]                      = 0
                self.incoming                                               = False

                


    '''      Iitial set up for Comunications lib        '''
    def __init__(self):

        #   Telemetry 
        self.raw_telemetry          = []                # raw telemetry data ( backend )
        self.TELEMETRY__            = {}                # parsed telemetry data from the buffer 
        # look up table 
        self.telemetry_keys = (                         # A list of every possible telemetry data index/key
                'mid', 'x', 'y', 'z',
                'pitch', 'roll', 'yaw',
                'vgx', 'vgy', 'vgz',
                'templ', 'temph',
                'tof', 'h', 'bat', 'time','baro',
                'agx', 'agy', 'agz'
            )


        #   connection state toggles 
        self.incoming               = False             # incoming data state 
        self.hold                   = False             # sending data / hold ping rquest 
        self.downlink_hold          = False             # hold threads while changing sockets ( ussed durring a loss of connection )
        self.UPLINK_PORT            = 1024              # Client ports 
        
        #   Connection Link State Data
        self.connection_data = {
            "connection_state"      : False,            # state of connection ckeck 
            "connection_sub_state"  : False,            # state of connection ckeck ( spam reduction )
            "ping_clk"              : 0,                # internal clock
            "ping_MClk"             : 4*60,             # frame time ( *60 ~ convert to seconds )
            "conCheck_index"        : 0,                # connection time out clk
            "conCheck_Mindex"       : 2,                # connection time out 
            "connection_toggle"     : True,             # on / off state for drone connection
            }

        #   Users IP and port 
        self.host_name              = socket. gethostname()                                                           # pull ip from socket host 
        self.local_ip               = socket. gethostbyname( self.host_name )
        self.CMDsoc                 = socket. socket(  socket.AF_INET , socket.SOCK_DGRAM  )                          # command    socket object  ( AFINET = IPV4 protocalll // DGRM = datagram )
        self.telemetry              = socket. socket(  socket.AF_INET , socket.SOCK_DGRAM  )                          # telemetry  socket object

       #    Drone coms_ data :
        self.drone_ip               = '192.168.10.1'
        self.droneVideo_ip          = '0.0.0.0'         
        self.UDP_control_port       = 8889
        self.UDP_state_port         = 8890
        self.UDP_video_port         = 1111 # beta 2.0
        self.DRONE_address          = (self.drone_ip , self.UDP_control_port)

        #   open sockets 
        self. CMDsoc        .bind(  (   self.local_ip ,  self.UDP_control_port         )  )
        self. telemetry     .bind(  (   ""            ,  self.UDP_state_port           )  )

        # wrap sockets 
        self.client_socket                           = self.CMDsoc          
        self.client_state_socket                     = self.telemetry        

        
        # create threads 
        self.threads_init                     = False
        if not self.threads_init:
            # command responsed thread
            self.receive_thread                      = threading.Thread( target = TombStone.downlink_com         , args = (  self,   self.UPLINK_PORT) )
            self.receive_thread.daemon               = True                                                               # force thred to run in parallel 
            self.receive_thread.start()
            # status responsed thread
            self.status_thread                       = threading.Thread( target = TombStone.downlink_telemetry   , args = (  self,   self.UPLINK_PORT) )
            self.status_thread.daemon                = True                                                               # force thred to run in parallel 
            self.status_thread.start()
            # <>>> end stop
            self.threads_init                 = True









# Bridge for the communication layer and the controller API
class FC(object):
    """     Controller Module     """
    """ 
    // ----------------------------------------------------------------------------------------------------------------------------------------------------------------
    This module is created to link flight controls to the controller via streaming data with TombStone 
   
    Videogame inspired control maping // demo of scripting between the 2 main moduels // aka: bridge 

    ** you would write your own code here to bridge the 2 apis togehter ( this is an example essentially ) **
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------

    stream          (   N/A   )             Streams data channels to uplink() -> in TombStone
    bindings_       (   N/A   )             Controller input bridge to TombStone
    update          (   N/A   )             60 Fps updater ( Called in FreeFlight at 60 fps ) // streaming controller input at 60fps (.01666.. seconds between tranmissions )


    //---------------------------------------------------------------------------------------------------------------------------------------------------------------
    Writen  By:                                 Steven Andrews II
    Project By:                              [[ Steven Andrews II ]]  
    // ---------------------------------------------------------------------------------------------------------------------------------------------------------------
    """ 
    
    def __init__(   self  , CM    ):

        self.CM_                  = CM                          #   controller module ( By: Stevem Andrews )
        self.communication      = TombStone()                   #   // Created BY: Steven Andrews II
        self.channels           = [0,0,0,0]                     #   channels packet constructor

        #   chanel write state toggles
        self.channel_3_alive     = False                        #   channel activity states 
        self.channel_2_alive     = False
        self.channel_1_alive     = False
        self.channel_0_alive     = False
        self.last_known_input    = 0                            #   (stick input) 0 is forward, 1 is backwards
        self.brake_              = False                        #   air brake state // back thrust
        self.dead_               = False                        #   toggles when all sticks are dead  ( sends  0 0 0 0 to stablize the drone )
        self.circle              = False                        #   circle a point toggle 
        self.rs_mag = 0
        self.ls_mag = 0
        self.L_ang  =   0
        self.R_ang  =   0

        # vectorization data
        self.yaw                       = 0    # real yaw
        self.rotation_vector_angle     = 0    # Right stick
        self.direction_vector_angle    = 0    # left stik
        self.direction_mag             = 0
        self.rotation_mag              = 0

        # dead man safty toggle
        self.DM_CALL             = False
        self.dead_man            = False  
        
        # debug 
        self.debug_t            = 0 

   
        #   controller mappings and settings for pilot 
        self.pilot = {
            "con_"          : {                                 #   controller mappings for pilot ( remappable special buttons )
                            "lift"          :  "A" ,                   
                            "land"          :  "B" ,
                            "flip"          :  "X" ,
                            "Air brakes"    :  "LB",
                            "Circle Point"  :  "RB",
                            },

            "settings"      :{
                            "port"                  : 0,        #   port id for the pilots controller to be accepted on ( see ControllModuel )
                            "telem_debug"           : True,     #   telemetry debug toggle
                            "debug_update"          : 3*60,     #   battery read out speed
                            },
                     } #    EO_pilot
        
        




    # get the correct angles for yaw for thrust vectors 
    def stick_vectorizatio(self):
        #////////////////////////////////////////
        self.drone_yaw = self.communication.get_telem("yaw")
        raw_yaw     =   int(self.drone_yaw) *-1
        #////////////////////////////////////////
        if self.ls_mag == None:
            self.direction_mag   = 0
        else:
            self.direction_mag = (float(self.ls_mag)/1)
        #////////////////////////////////////////
        if self.rs_mag == None:
            self.rotation_mag   = 0
        else:
            self.rotation_mag   = (float(self.rs_mag)/1)
        #////////////////////////////////////////
        # 0 - 360 telemetry patch
        #////////////////////////////////////////
        if self.yaw <= 0:
            self.yaw = raw_yaw + 360
        else:
            self.yaw = raw_yaw
        #////////////////////////////////////////
        if self.R_ang is None:
            self.rotation_vector_angle = 0
        else:
            if self.R_ang > 0 and  self.R_ang < 180:
                self.rotation_vector_angle = self.yaw -90
            else:
                self.rotation_vector_angle = self.yaw +90
        #////////////////////////////////////////
        if self.L_ang is None:
            self.direction_vector_angle       = 0
        else:
            if ((self.L_ang >= 0.0 or self.L_ang >=0)  and  self.L_ang <= 25) or self.L_ang >= 335 and  self.L_ang <= 360  :
                self.direction_vector_angle   = self.yaw   
            if self.L_ang > 65 and  self.L_ang < 115:
                self.direction_vector_angle   = self.yaw -90
            if self.L_ang > 155 and  self.L_ang < 205:
                self.direction_vector_angle   = self.yaw -180
            if self.L_ang > 245 and  self.L_ang < 295:
                self.direction_vector_angle   = self.yaw +90
        # returns the correct angle for the vector display in the GUI 
        return  self.direction_vector_angle , self.rotation_vector_angle

         


    '''Backend:      Stream Cntroller input to Uplink     '''
    def stream(self):

        if self.dead_man    == False :
            #   if all button binds are dead ( drone uplink stabalization )
            if  self.channel_0_alive  == False and self.channel_1_alive  == False and self.channel_2_alive == False and self.channel_3_alive == False and self.dead_ == False and  self.brake_ == False and self.circle == False:
                self.channels               = [0,0,0,0]
                print("Streaming:  ",self.channels)
                cmd = 'rc {} {} {} {}'.format( self.channels[0],self.channels[1],self.channels[2],self.channels[3])
                self.communication.uplink( cmd, True)
                self.dead_                  = True

            #   stream data at 60 FPS
            if  self.channel_0_alive  == True or self.channel_1_alive  == True or self.channel_2_alive == True or self.channel_3_alive == True or self.circle == True:
                print("Streaming:  ",self.channels)
                cmd = 'rc {} {} {} {}'.format( self.channels[0] , self.channels[1] , self.channels[2] , self.channels[3] )
                self.communication.uplink( cmd , True )
                self.channel_0_alive        = False
                self.channel_1_alive        = False
                self.channel_2_alive        = False
                self.channel_3_alive        = False
                self.dead_                  = False

        #   dead controller port
        if self.dead_man == True and self.DM_CALL == False:
           print("dead man landing")
           self.communication.uplink(  "land"    ,  True  )   # could also send 0000 to stablize ( maybe add a time )
           self.DM_CALL  = True   
          


    '''Frontend interface:      Controller Binding Bridge     '''
    def bindings_(self):
       
        # Stick data from the ControllerModule ( CM )
        right_stick , rs_mag   = self.CM_.get_stick_angle(    self.pilot["settings"]["port"] , "R_stick"  )
        left_stick  , ls_mag   = self.CM_.get_stick_angle(    self.pilot["settings"]["port"] , "L_stick"  )
        self.rs_mag = rs_mag
        self.ls_mag = ls_mag
        self.L_ang = left_stick
        self.R_ang = right_stick
        RT                     = self.       CM_.get_axis(    self.pilot["settings"]["port"] , "RT"       )
        LT                     = self.       CM_.get_axis(    self.pilot["settings"]["port"] , "LT"       )


        #----------------------------------------------------------------------------------------------------------------------------------
        #   Trigger input layout  (  Accend // Decend  ) 
        #----------------------------------------------------------------------------------------------------------------------------------

        # reset the channel
        if self.channel_2_alive == False:
            self.channels[2]                =   0
        # right trigger
        if RT != None:   
            if RT >= .8:
                self.channels[2]            =   70
                self.channel_2_alive        =   True
       
        # left trigger 
        if LT != None:
            if LT >= .8:
                self.channels[2]            =   -70
                self.channel_2_alive        =   True
      
        #----------------------------------------------------------------------------------------------------------------------------------
        #   Right Stick (  Rotation // Yaw  )
        #----------------------------------------------------------------------------------------------------------------------------------
        if self.circle == False:
            # reset the channel
            if self.channel_3_alive == False :
                self.channels[3]                =   0
       
            if right_stick != None :
                # rotate left 
                 if right_stick >= 180 and right_stick <= 360 :
                      self.channels[3]          =   (-100 * rs_mag)
                      self.channel_3_alive      =   True
           
                # rotate rigth
                 if right_stick >= 0 and right_stick < 180 :
                      self.channels[3]          =   (100 * rs_mag)
                      self.channel_3_alive      =   True
         
            #----------------------------------------------------------------------------------------------------------------------------------
            #   Left Stick (  Directional motion  )
            #----------------------------------------------------------------------------------------------------------------------------------


            # reset the channel
            if self.channel_1_alive == False and self.brake_ == False :
                self.channels[1]                =   0

            if self.channel_0_alive == False :
                self.channels[0]                =   0

            if left_stick != None :
                # mvove forward 
                if left_stick >= 335 and left_stick <= 360 or left_stick >= 0.0 and left_stick <= 25 and self.brake_ == False:
                      self.channels[1]          =   int( 100 * ls_mag )
                      self.last_known_input     =   0
                      self.channel_1_alive      =   True

                # move backward 
                if left_stick >= 155 and left_stick <= 205 and self.brake_ == False :
                      self.channels[1]          =   int( -100 * ls_mag )
                      self.last_known_input     =   1
                      self.channel_1_alive      =   True
     
                # straif left
                if left_stick >= 245 and left_stick <= 295 :
                      self.channels[0]          =   int( -100 * ls_mag )
                      self.channel_0_alive      =   True
      
                # straif right
                if left_stick >= 65 and left_stick <= 115 :
                      self.channels[0]          =   int( 100 * ls_mag )
                      self.channel_0_alive      =   True
  
            

        #----------------------------------------------------------------------------------------------------------------------------------
        #   Button layout ( special commands ) 
        #----------------------------------------------------------------------------------------------------------------------------------


        for k,v in self.pilot["con_"].items():
             # grab current data from CM
             button_value           = self.CM_.get_button(   self.pilot["settings"]["port"]  ,   v    )
             # button layout 


             if button_value == 1 and v == "A":
                # take off
                self.communication.uplink(  "takeoff" ,  True  )
                self.CM_.set_rumble( self.pilot["settings"]["port"] , [.25,.25,3] )   #     Haptic feed back 


             if button_value == 1 and v == "X":
                # flip
                self.communication.uplink(  "flip b" ,  True  )


             if button_value == 1 and v == "B":
                # landing
                for i in range(0,3): # just spam lamding, ill code that after the semester into Tombstone
                    self.communication.uplink(  "land"    ,  True  )
                self.CM_.set_rumble( self.pilot["settings"]["port"] , [.25,.25,3] )   #     Haptic feed back
               

             '''   Air brake_  (hold)  '''
             if button_value == 1 and v == "LB":         
                self.brake_                   =    True
                if  self.last_known_input     ==   0:   #   Forwards
                    self.channels[1]          =    -100
                if  self.last_known_input     ==   1:   #   Backwards
                    self.channels[1]          =    100
             else:
                    self.brake_               =    False


             '''   Rotate around a point  (hold)   '''
             if button_value == 1 and v == "RB":
                self.circle = True 
                self.channels[0]          =    100      # large circle 
                self.channels[3]          =   -75
             else:
                self.circle = False 

       
        '''   Dead man safty  '''
        if self.CM_.port_[ self.pilot["settings"]["port"] ]["attached"] == "none":
                 self.dead_man    = True
        else:
                 self.DM_CALL     = False
                 self.dead_man    = False

       

       
            

    '''      120fps FPS updater     '''
    def update_(   self   ):
        self. stream(  )                                  #   streams controller information from the bridge 
        self. bindings_(  )                               #   controller bridge 
        self. communication. connection_(  )              #   UP_DOWN link 
        self. communication. telem_buffer(  )             #   Telemetry downlink parsing buffer 

          