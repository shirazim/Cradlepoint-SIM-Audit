#Author: Michael Shirazi
#4/10/2022

#In order to run this, you will need a text file called CPList.txt in the same directory as this script. That text file should include all CradlePoint hostnames

import paramiko
import getpass
import csv

f = open('CPList.txt', 'r')
CPList = f.read()
CPList = CPList.split('\n')
problemlist = []
username = getpass.getuser()
password = getpass.getpass(prompt='Enter your password:')


for cp in CPList:
    try:
        
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()       
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(cp,
                    username=username,
                    password=password,
                    look_for_keys=False )

        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("get status/wan/devices/mdm-*/diagnostics/ICCID status/wan/devices/mdm-*/diagnostics/HOMECARRID /status/wan/devices/mdm-*/diagnostics/SIM_NUM")
        output = ssh_stdout.readlines()
        ssh.close()


        #The following iterates through the output. Each 3 lines of output relates to a single SIM card
        i = 0
        for line in output:

            if not "status" in line:
                continue

            line = line.replace(',','')
            line = line.rstrip()
        
        #This pulls the SIM priority
            if "SIM_NUM" in line:
                simn_num = (line[-2])

                if simn_num == '1':
                    simn_num = "Active"
                if simn_num == "2":
                    simn_num = "Passive"

        #Extracts the SIM provider from the output

            if "Rogers Wireless" in line:
                provider = (line[-16:-1]).replace('"','')
            elif "TELUS" in line:
                provider = (line[-7:-1]).replace('"','')
            elif "T-Mobile" in line:
                provider = (line[-10:-1]).replace('"','')
            elif "Verizon" in line:
                provider = (line[-9:-1]).replace('"','')
            elif "AT&T" in line:
                provider = (line[-6:-1]).replace('"','')
            if "ICCID" in line:
                line = (line[-21:-1]).replace('"','')
                iccid = line

            i = i + 1

            #After 3 lines of output, the SIM priority, provider and ICCID will be appended to a CSV

            if i == 3:

                print(cp,simn_num.encode("ascii"), provider.encode("ascii"), iccid.encode("ascii"))

                f = open("CradlePointcsv.csv","a")
                cr = csv.writer(f,delimiter=',')
                cr.writerow([cp, simn_num.encode("ascii"),provider.encode("ascii"),iccid])
                f.close()

                i = 0

                #The following is error handling which tells you which CPs need to be manually reviewed (A list of sites will go to ProblemCP.txt)
    except:
        print('You will need to manually audit ',cp)
        problemlist.append(cp)


g = open('ProblemCP.txt', 'w')

for d in problemlist:
        g.write(d)
        g.write('\n')