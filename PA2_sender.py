#!/usr/bin/env python3
# Last updated: Oct, 2021

import sys
import socket
import datetime
from checksum import checksum, checksum_verifier
import time

CONNECTION_TIMEOUT = 60 # timeout when the sender cannot find the receiver within 60 seconds
FIRST_NAME = "SHELY"
LAST_NAME = "FRADKIN"

def start_sender(server_ip, server_port, connection_ID, loss_rate=0, corrupt_rate=0, max_delay=0, transmission_timeout=60, filename="declaration.txt"):
    """
     This function runs the sender, connnect to the server, and send a file to the receiver.
     The function will print the checksum, number of packet sent/recv/corrupt recv/timeout at the end. 
     The checksum is expected to be the same as the checksum that the receiver prints at the end.

     Input: 
        server_ip - IP of the server (String)
        server_port - Port to connect on the server (int)
        connection_ID - your sender and receiver should specify the same connection ID (String)
        loss_rate - the probabilities that a message will be lost (float - default is 0, the value should be between 0 to 1)
        corrupt_rate - the probabilities that a message will be corrupted (float - default is 0, the value should be between 0 to 1)
        max_delay - maximum delay for your packet at the server (int - default is 0, the value should be between 0 to 5)
        tranmission_timeout - waiting time until the sender resends the packet again (int - default is 60 seconds and cannot be 0)
        filename - the path + filename to send (String)

     Output: 
        checksum_val - the checksum value of the file sent (String that always has 5 digits)
        total_packet_sent - the total number of packet sent (int)
        total_packet_recv - the total number of packet received, including corrupted (int)
        total_corrupted_pkt_recv - the total number of corrupted packet receieved (int)
        total_timeout - the total number of timeout (int)

    """

    print("Student name: {} {}".format(FIRST_NAME, LAST_NAME))
    print("Start running sender: {}".format(datetime.datetime.now()))

    checksum_val = "00000"
    total_packet_sent = 0
    total_packet_recv = 0
    total_corrupted_pkt_recv = 0
    total_timeout =  0

    print("Connecting to server: {}, {}, {}".format(server_ip, server_port, connection_ID))

    ##### START YOUR IMPLEMENTATION HERE #####
    #getting first 200 characters of text
    f = open(filename,'r')
    toRead = ""
    i = 0
    while 1: 
        toAdd = f.read(1)
        if not toAdd or i == 200:
            break
        toRead += toAdd
        i += 1
    f.close()

    arr = []
    cpy = toRead
    for i in range(0, 10):
        arr.append(toRead[0:20])
        toRead = toRead[20:]

    #setting up socket 
    #serverName = "gaia.cs.umass.edu"
    serverName = server_ip
    #serverPort = 20500
    serverPort = server_port

    transmission_timeout = int(transmission_timeout) #number of seconds sender will wait for ACK from reciver 


    #declar_txt = "When in the Course of human events, it becomes necessary for one people to dissolve the political bands which have connected them with another, and to assume among the powers of the earth, the separat"

    ex = 0

    while (ex == 0):
        #hello message 
        helloMsg = "HELLO S " + str(loss_rate) + " " + str(corrupt_rate) + " " + str(max_delay) + " " + str(connection_ID)

        #create socket 
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        #connect to GAIA
        sock.connect((serverName, serverPort))

        #send initial hello message to gaia 
        sock.send(helloMsg.encode())

        while True: 
            #get response from GAIA
            print("Getting response from GAIA")
            resp = sock.recv(1024).decode() 

            #check if error connecting to GAIA
            if(resp == "ERROR “Incorrect Parameter Values"): 
                print("One or more of the parameters specifies in your HELLO message are invalid")
                sock.close()
                break 
            elif(resp == "ERROR CONNECTION ID IN USE"):
                print("Another sender/reciever pair are already communicating using the Connection ID you specified")
                sock.close() 
                break 
            elif(resp == "ERROR NO MATCHING CONNECTION REQUEST"): 
                print("No other cliesnt has made a request in the last 60 seconds for thr same Connection ID")
                sock.close() 
                break 
            elif(resp == "WAITING"): 
                #time.sleep(5)
                print("Server is waiting for another client to connect within the next 60 seconds")
                continue
            else: 
                #OK message recieved from GAIA
                print("Client Connected to GAIA") 

                exSeqNum = "0"
                exAckNum = "0"
                count = 0

                #loop through array of file packets to send 
                for data in arr: 
                #while True: 

                    #data = declar_txt[:20]
                    #declar_txt = declar_txt[20:]

                    sock.settimeout(transmission_timeout)

                    #print("Data:", data)
                    #print("Data len:", len(data))

                    preMsg = exSeqNum + " " + exAckNum + " " + data + " "

                    #get checksum value for message 
                    chckSumVal = checksum(preMsg)

                    #get checksum value for entire file
                    tmp = int(checksum(data))
                    tmp2 = int(checksum_val)
                    tmp3 = tmp + tmp2
                    checksum_val = str(tmp3)
                    #print("checksum_val:", checksum_val)

                    postMsg = preMsg + chckSumVal 

                    #print("postMsg:", postMsg)

                    while True: 
                        #print("pre sent")
                        #transmitting to reciever 
                        sock.send(postMsg.encode())
                        total_packet_sent += 1

                        #print("sent")

                        try: 
                            #recieve response from reciever
                            #print("ok")
                            reply = sock.recv(1024)
                            #print("reply:", reply.decode())
                            #print(reply)
                           # print(len(reply))

                            reply = reply.decode()

                            if reply == "":
                                #print("bruh this shit dumb")
                                ex = 1
                                break
                        except socket.timeout: 
                            #timeout occured
                            total_timeout += 1
                            continue 

                        #print("replyyyyy", reply)
                        
                        total_packet_recv += 1

                        #check if recieved correct checksum from receiver
                        checkChkSum = checksum_verifier(reply)

                        if(checkChkSum): 
                            #print("here")
                            #print("ACK: ", reply[2])
                            #print("exAckNum: ", exAckNum)
                            #count += 1
                            if(reply[2] == exAckNum): 
                                #print("Correct packet recieved, sending next packet")
                                count += 1
                                #change value of expected ack number
                                if(exAckNum == "0"): 
                                    exAckNum = "1"
                                else: 
                                    exAckNum = "0"
                                
                                #change value of expected sequence number 
                                if(exSeqNum == "0"): 
                                    exSeqNum = "1"
                                else: 
                                    exSeqNum = "0"
                                break
                            else: 
                                #print("incorrect ACK")
                                total_corrupted_pkt_recv += 1
                                continue
                        else: 
                            #print("incorrect checksum")
                            total_corrupted_pkt_recv += 1
                            continue
                    if(ex == 1): 
                        #print("shutting down")
                        #checksum_val = str(chckSumVal)
                        break 

                    if(count == 10): 
                        ex = 1
                    #if(data == "e earth, the separat"):
                    #if(declar_txt == ""):
                        #ex = 1
            if(ex == 1): 
                break 

        #close socket
        print("Closing socket")
        sock.close()  

        if(ex == 0): 
            print("attempting to reconnect to Gaia")
            #time.sleep(3)
    print("Now exiting")  
    ##### END YOUR IMPLEMENTATION HERE #####

    print("Finish running sender: {}".format(datetime.datetime.now()))

    # PRINT STATISTICS
    # PLEASE DON'T ADD ANY ADDITIONAL PRINT() AFTER THIS LINE
    print("File checksum: {}".format(checksum_val))
    print("Total packet sent: {}".format(total_packet_sent))
    print("Total packet recv: {}".format(total_packet_recv))
    print("Total corrupted packet recv: {}".format(total_corrupted_pkt_recv))
    print("Total timeout: {}".format(total_timeout))

    return (checksum_val, total_packet_sent, total_packet_recv, total_corrupted_pkt_recv, total_timeout)
 
if __name__ == '__main__':
    # CHECK INPUT ARGUMENTS
    if len(sys.argv) != 9:
        print("Expected \"python3 PA2_sender.py <server_ip> <server_port> <connection_id> <loss_rate> <corrupt_rate> <max_delay> <transmission_timeout> <filename>\"")
        exit()

    # ASSIGN ARGUMENTS TO VARIABLES
    server_ip, server_port, connection_ID, loss_rate, corrupt_rate, max_delay, transmission_timeout, filename = sys.argv[1:]
    
    # RUN SENDER
    start_sender(server_ip, int(server_port), connection_ID, loss_rate, corrupt_rate, max_delay, float(transmission_timeout), filename)
