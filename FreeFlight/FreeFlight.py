"""[[
    ///---------------------------------------------------------------------------------------------------------------------------------------------------------///
    ///---------------------------------------------------------------------------------------------------------------------------------------------------------///
    ///---------------------------------------------------------------------------------------------------------------------------------------------------------///
    ///-----------------------------------------------------////////////////////----////////////////////--------------------------------------------------------///
    ///----------------------------------------------------/////////////////-------/////////////////------------------------------------------------------------///
    ///---------------------------------------------------/////-------------------/////-------------------------------------------------------------------------///
    ///--------------------------------------------///////////////---------/////////////------------------------------------------------------------------------///
    ///------------------------------------------------//////////////---------//////////////--------------------------------------------------------------------///
    ///------------------------------------------------/////-------------------/////-----------////--------///////--------////----------------------------------///
    ///-----------------------------------------------/////-------------------/////-------------//--------//---//-------//---//---------------------------------///
    ///----------------------------------------------/////-------------------/////-------------//--------//---//-------///////----------------------------------///
    ///---------------------------------------------/////-------------------/////-----------//////--//--///////-------//---//-----------------------------------///
    ///---------------------------------------------------------------------------------------------------------------------------------------------------------///
    ///---------------------------------------------------------------------------------------------------------------------------------------------------------///
    ///-----------------------------------------------------[[    Free Flight By: Steven Andrews   ]]--------Fall--2022-----------------------------------------///
    ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    FreeFlight is a student project created by Steven Andrews II  

    Freeflight is a set of libraries created to allow a user to fly the DJI Tello drone
    via gamepad remotes without use of the official Tello Libraries or apps. 



    Utilizizing standard Python libraries and Pygame ( for controller input and graphics output ) 
    these libraries allow for streaing RC commands + auto handling of connection states + gamepad states
    for precision flight control from the user. 


    Dev note: 
    Expanding on these concepts, an AI with the use of PyCV and VS could interface
    with libraires created for this project to control/interface with a vitual gampad 
    to enable autonomous flight. Only a realitive few functions would need to be 
    created to enable this functionality in full. 

   

    All Rights Reserved @ SA 
    ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    Libraires and scripts created for the project: ( By: Steven Andrews II )

    ControllerModule ( CM ) --  >  Discriptions: A small library to interface with Pygames controller functions // allows re_mapping, multi controller suport, timeout, ( a large range of functions, see file ) 
    FlightController ( FC ) --  >                A library that bridges the ControllerModuel API to allow data streaming and auto connection to the drone ( Interface between ControllerModule and Tombstone )
    TombStone        ( TS ) --  >                A custom connection system for the DJI Tello drone ( auto connection, client side connection state, control streaming )
    GraphicsModule   ( GM ) --  >                A Small class script to display things to the screen  


    Features include:

    Controller Support:                                     ( CM )
    >>      Full controller support
    >>      Multi controller support "virtual ports" ( no limit )
    >>      Controller disconnecton handling 
    >>      Controller remapping 
    >>      Time out on "virtual ports" 
    >>      awaitng contollers timeout
    >>      Muti controller rumble support
    >>      Joystick handling
    >>      Controller to port auto aisgnment 


    TombStone:                                              ( TS )
    >>      Auto connect to DJI drone 
    >>      Client side connection state detection 
    >>      Connection loss auto handling ( socket handling )
    >>      Dissconect 
    >>      Dedicated RC command streaming 
    >>      Telemetry downlink 
    >>      Telemetry state parsing 
    >>      Realtime accessable telemetry downlink 


    FlightController:                                       ( FC )
    >>      API Bridging  ( TombStone and ControllerModule ) 
    >>      Controller input streaming to Tombstone
    >>      safty landings and flight stabilization handling 
    >>      Pricision Stick control // Flight control ( stick magnatiude from center = thrust ammount in any direction ) 
    >>      Special moves: ( 
                                AIR BRAKES                       * a button dedicated to stoping forward direction of travel with back thrust
                                DEAD MAN STICK [safty landing]   * dead controller landing 
                                Stick Stabilization              * no input flight stablization 
                                Rumble on take off/landings      * haptic feedback 
                                Flip                             # note: its hit or miss, the drone decides if it can make the flip ( the client can only send the comand, no downlink other than standard error )
                                Auto circle                      # Will tightly cicle a point ( early demo )
                            )


    Other libraries used ( Non-standard python libs ):
    Pygame                              ( Wsed for graphics and controller input )
    ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

                                                                       //   CSU Fall 2022  // -  Computer Engineering - Final Project

    College:                        Columbus State University          //   Fall 2022
    Project BY:         [[              Steven Andrews II              ]]

    Package Version: Prototype ( pre alpha ) 
    ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
]]"""
   

#--------------------------------------------------------------------------------------------------------
#--//   Import and Initialize Libs
#--------------------------------------------------------------------------------------------------------
import  pygame
import  time
import  math 
#import socket
#import threading
#from   threading import Thread


#   Initialize Pygame/utilities & set header 
pygame.init()
pygame.display.set_caption("FreeFlight BY: Steven Andrews  ")
pygame.joystick.init()                                         



#-------------------------------------------------------------------------------------------------------- 
#   Import FREE_FLIGHT engine modules
#-------------------------------------------------------------------------------------------------------- 

import                    ControllerModule                   # controller manager module
Controller__            = ControllerModule  .CM(  pygame , math , 1  )    # Number = number of virtual ports ( number of controllers to support )                         


import                    FlightController
FlightController__      = FlightController  .FC(  Controller__  ) 

import                    GraphicsModule                   # controller manager module
Graphics__              = GraphicsModule    .GM(  pygame ,FlightController__ ) 



# set the screen to full screen and set resizable // return screen data
EXIT_                   = False                             # Main Loop exit
clock                   = pygame.time.Clock()               # Pygame clock moduel/class init


# FREAME RATE DATA [ 120 fps and 60 fps selected ] 
# rendering at 60, communications and bridging at 120 fps

max_skip                = 1
max_skip_               = 1                                 # frame skipping // compencation 
#  120 fps
accum_                  = float(0)
interval_               = float(1/120)                      # Frame setting ( 1 second / # of frames )
skip_                   = 0
#  60  fps
accum                   = float(0)
interval                = float(1/60)
skip                    = 0 




#--------------------------------------------------------------------------------------------------------
# ------------------------------/   FPS limited and function hook in   /---------------------------------
#--------------------------------------------------------------------------------------------------------




def Update_60():
    Controller__.update_() 
    Graphics__.update_()
    

def Update_120():
    FlightController__.update_()       
 



#-------------------------------------------------------------------------------------------------------- 
#  Main loop + FPS limiter 
#-------------------------------------------------------------------------------------------------------- 
cur_tick    = 0                                    
while not EXIT_:
    cur_tick = clock.tick()  /1000                  # calling this more than once throw off my calc
    
    # 60 FPS calc
    accum           = (accum        + cur_tick)    
    skip            = max_skip                      # rexet frame skipping 
    # 30 FPS calc
    accum_          = (accum_       + cur_tick)    
    skip_           = max_skip_                
 

    # 60 FPS function call out 
    if accum >= interval and skip >= 0:
        skip        = skip          -   1
        accum       = accum         -   interval
        Update_60()
      
    # 120 FPS function call out 
    if accum_ >= interval_ and skip_ >= 0:
        skip_       = skip_         -    1
        accum_      = accum_        -    interval_
        Update_120()
    
        
   












