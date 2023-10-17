#!/usr/bin/env python3
# Last updated: Oct, 2021

import sys
import time
import socket
import datetime 
from checksum import checksum, checksum_verifier
import time

CONNECTION_TIMEOUT = 60 # timeout when the receiver cannot find the sender within 60 seconds
FIRST_NAME = "SHELY"
LAST_NAME = "FRADKIN"

def start_receiver(server_ip, server_port, connection_ID, loss_rate=0.0, corrupt_rate=0.0, max_delay=0.0):
    """
     This function runs the receiver, connnect to the server, and receiver file from the sender.
     The function will print the checksum of the received file at the end. 
     The checksum is expected to be the same as the checksum that the sender prints at the end.

     Input: 
        server_ip - IP of the server (String)
        server_port - Port to connect on the server (int)
        connection_ID - your sender and receiver should specify the same connection ID (String)
        loss_rate - the probabilities that a message will be lost (float - default is 0, the value should be between 0 to 1)
        corrupt_rate - the probabilities that a message will be corrupted (float - default is 0, the value should be between 0 to 1)
        max_delay - maximum delay for your packet at the server (int - default is 0, the value should be between 0 to 5)

     Output: 
        checksum_val - the checksum value of the file sent (String that always has 5 digits)
    """

    print("Student name: {} {}".format(FIRST_NAME, LAST_NAME))
    print("Start running receiver: {}".format(datetime.datetime.now()))

    checksum_val = "00000"

    ##### START YOUR IMPLEMENTATION HERE #####
    #set up socket 
    # serverName = "gaia.cs.umass.edu"
    # serverPort = 20500
    serverName = server_ip
    serverPort = server_port
    
    ex = 0 

    while ex == 0: 
        #create hello message
        helloMsg = "HELLO R " + str(loss_rate) + " " + str(corrupt_rate) + " " + str(max_delay) + " " + str(connection_ID)
        
        #create socket
        recSock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        #connect socket to GAIA
        recSock.connect((serverName,serverPort))
        #send hello message to GAIA
        recSock.send(helloMsg.encode())

        while ex == 0:
            #get response from gaia
            print("Waiting for gaia")
            reply = recSock.recv(1024).decode()

            if reply == "WAITING":
                print("Server is waiting for another client to connect")
                #time.sleep(3)
                continue
            if reply == "ERROR Incorrect Parameter Values":
                print("one or more of the parameters specified in your HELLO message are invalid")
                break
            elif reply == "ERROR CONNECTION ID IN USE":
                print("another sender/receiver pair are already communicating using the Connection ID you specified")
                break
            elif reply == "ERROR NO MATCHING CONNECTION REQUEST":
                print("no other client has made a request in the last 60 seconds for the same Connection ID, so your client could not be connected to another client")
                break
            else:
                #ok messsage recieved from gaia
                print("Connecting to server")

                exAckNum = '1'
                exSeqNum = '0'
                data = ""

                while True: 
                    #print("back up")
                    #recieve message from sender
                    msg = recSock.recv(1024).decode()


                    #print("msg: ", msg)

                    #if empty message received
                    if(msg == ""): 
                        ex = 1
                        break

                    chk = checksum_verifier(msg)

                    if(chk): #not corrupt packet
                        if(msg[0] == exSeqNum): 
                            #print("recieved packet correctly. Transmitting correct ACK")

                            if(exAckNum == '0'):
                                exAckNum = '1'
                            else: 
                                exAckNum = '0'
                            
                            rep = '  ' + exAckNum + ' ' + '                    ' + ' ' 
                            chkNew = checksum(rep)

                            #print("msg: ", msg)

                            data = data + msg[4:24]

                            finalrep = rep + chkNew
                            #print("rep:",finalrep)
                            #print("len of rep:", len(finalrep))
                            recSock.send(finalrep.encode())
                            #print("rep2:", finalrep.encode())

                            #changing expected Ack and Sequence numbers
                            

                            if(exSeqNum == '0'):
                                exSeqNum = '1'
                            else: 
                                exSeqNum = '0'
                        else: 
                            #print("Packet is duplicate")
                            rep = "  " + exAckNum + " " + "                    " + " " 
                            chk2 = checksum(rep)
                            rep = rep + chk2
                            recSock.send(rep.encode())
                    else:
                        #print("packet is corrupt") 
                        rep = "  " + exAckNum + " " + "                    " + " " 
                        chk2 = checksum(rep)
                        checksum_val = chk2
                        rep = rep + chk2 
                        recSock.send(rep.encode())
                    #print("here now")

        #closing socket
        print("Closing socket")
        recSock.close()

        if(ex == 0):
            print("trying to reconnect to gaia")
        
    checksum_val = checksum(data)
    print("Exiting")

    ##### END YOUR IMPLEMENTATION HERE #####

    print("Finish running receiver: {}".format(datetime.datetime.now()))

    # PRINT STATISTICS
    # PLEASE DON'T ADD ANY ADDITIONAL PRINT() AFTER THIS LINE
    print("File checksum: {}".format(checksum_val))

    return checksum_val

 
if __name__ == '__main__':
    # CHECK INPUT ARGUMENTS
    if len(sys.argv) != 7:
        print("Expected \"python PA2_receiver.py <server_ip> <server_port> <connection_id> <loss_rate> <corrupt_rate> <max_delay>\"")
        exit()
    server_ip, server_port, connection_ID, loss_rate, corrupt_rate, max_delay = sys.argv[1:]
    # START RECEIVER
    start_receiver(server_ip, int(server_port), connection_ID, loss_rate, corrupt_rate, max_delay)
