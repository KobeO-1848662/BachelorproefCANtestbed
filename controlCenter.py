import serial
import tkinter as tk
import os

receivedMessages = {}

def sendDataToEcu(data, ecuPort, baudRate):
    ser = serial.Serial(ecuPort, baudRate)
    ser.write(data)
    ser.close()

def sendData():
    selectedLogFile = logFileVar.get()
    baudRate = 9600

    ecuPorts = {
        'ECU1' : 'COM3'#,
        #'ECU2' : 'COM6'
    }

    desiredIds = {
        'ECU1': ['1031', '117', '1512', '458', '569', '61', '722', '1788', '651', '737', '930', '1262', '631', '1661', '1694', '1505'],
        'ECU2': ['1076', '1124', '1176', '1314', '1408', '215', '403', '526', '870', '1072', '304', '738', '837', '452', '1227', '560', '14']
    }

    with open(selectedLogFile, "r") as logfile:
        for line in logfile:
            try:
                parts = line.strip().split(' ')
                canIdHex = parts[2].split('#')[0]
                canId = int(canIdHex, 16)
                
                canDataHex = parts[2].split('#')[1]
                canData = bytes.fromhex(canDataHex)
                
                for ecu, ecuIds in desiredIds.items():
                    if str(canId) in ecuIds:
                        ecuPort = ecuPorts.get(ecu, None)
                        if ecuPort:
                            sendDataToEcu(canData,ecuPort,baudRate)
                            print(f"Sent CAN data to {ecu}: {canData.hex()}")

                            if ecu not in receivedMessages:
                                receivedMessages[ecu] = []
                            receivedMessages[ecu].append(canData.hex())
            except (ValueError, IndexError):
                print("Invalid line format:", line.strip())

    showReceivedMessagesWindow()


def showReceivedMessagesWindow():
    receivedMessagesWindow = tk.Toplevel(root)
    receivedMessagesWindow.title("Received Messages")

    sortedReceivedMessages = dict(sorted(receivedMessages.items(), key=lambda item: int(item[0][-1])))

    for ecu, messages in sortedReceivedMessages.items():
        ecuFrame = tk.Frame(receivedMessagesWindow)
        ecuFrame.pack(side=tk.LEFT, padx=10, pady=10)

        label = tk.Label(ecuFrame, text=f"{ecu} messages: ")
        label.pack()

        messageText = '\n'.join(messages)

        textWidget = tk.Text(ecuFrame, wrap=tk.NONE)
        textWidget.insert(tk.END, messageText)
        textWidget.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(ecuFrame, command=textWidget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        textWidget.config(yscrollcommand=scrollbar.set)


root = tk.Tk()
root.title("CAN log file sender")


logFileVar = tk.StringVar()
logFileLabel = tk.Label(root, text="Select log file:")
logFileLabel.pack()
logFileDropdown = tk.OptionMenu(root, logFileVar, "")
logFileDropdown.pack()


sendButton = tk.Button(root,text="Send data", command=sendData)
sendButton.pack()

logFileDropdown["menu"].delete(0, "end") 
logDirectory = "C:/Users/kobeo/OneDrive/Documenten/Kobe/Bachelorproef/ambient"
for logFile in os.listdir(logDirectory):
    if logFile.endswith(".log"):
        logFileDropdown["menu"].add_command(label=logFile, command=tk._setit(logFileVar, os.path.join(logDirectory, logFile)))

root.mainloop()