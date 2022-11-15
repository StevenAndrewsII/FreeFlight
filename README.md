# FreeFlight
FreeFlight is a student project created to control DJI Tello drones via gamepad and with a basic GUI 

Fall Semester 2022 - Columbus State Univeristy 
// Writen by: Steven Andrews II 
-----------------------------------------------------------------------------------------------------------------------------------

This application was writen as a project submission to CSU for robotics. The premise of the project was to control DJI Tello drones with a gamepad and render a GUI for the flight telemetry data. 

I created 2 standalone APIs for the project:
-----------------------------------------------------------------------------------------------------------------------------------
[ TombStone ] | [ PyGame controller ] 


>Tombstone    = A network layer for the Tello Drone platform 
>
>PyGame controller = A controller api that suports multicontroller and dynamic remapping of the control input. 



Dev Note:   All other scripts are demonstrations of interfacing the 2 standalone apis. 


Non-standard APIs used:

Pygame:
used mostly for hardware and graphics backend



To run the application you must install Pygame via the pip-installer. 
This is the only requirment to run the application. 

