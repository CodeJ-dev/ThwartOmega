#Jay Doshi Mong-En ip
#12/2/19
#Program to create the game Thwart-Omega

#imports
import discord, re
import asyncio
from PIL import Image
from random import randint
from datetime import datetime
from time import sleep

#Create global variables 
global hasStarted, grid, player1, player2, player3, playerList, maxTime, maxReservedTime, whiteRole, blackRole, greyRole

#Intialize variables

#Set maxTime to 120 seconds and reserveTime to 300 seconds as a default value
maxTime = 120 #Stores the time in seconds
maxReservedTime = 300 #Stores the time in seconds

hasStarted = False

grid = None

player1 = None 
player2 = None
player3 = None

whiteRole = None
blackRole = None
greyRole = None

playerList = []

#Function that return an image of two images concatenated horizontally
def concat_h(image1, image2):
    
    image3 = Image.new('RGB', (image1.width + image2.width, image1.height))
    image3.paste(image1, (0, 0))
    image3.paste(image2, (image1.width, 0))
    
    return image3

#Function that return an image of two images concatenated vertically
def concat_v(image1, image2):
    
    image3 = Image.new('RGB', (image1.width, image1.height + image2.height))
    image3.paste(image1, (0, 0))
    image3.paste(image2, (0, image1.height))
    
    return image3

#Function that returns the playerList as a string
def prettyPlayerList(playerList):
    #Prints the player list
    string = "Player List:"
    #Goes through each player and gets prints their id in the form <@id> which when sent as a message in discord prints the user name instead
    for player in playerList:
        string += " <@" + str(player) + ">"
    #Returns teh list
    return string

#Function that converts the time from the form [##:##:##] = [hour:min:seconds] to their seconds value and returns the seconds value as an integer
def convertTime(timeString):
    #Takes in the hour value, min value, and sec value
    hour = int(timeString[1:3])
    minute = int(timeString[4:6])
    second = int(timeString[7:9])
    #Computes the total time in seconds
    total = hour*3600 + minute*60 + second
    
    return total

#Function that takes in the seconds value and returns it as a string it in the form [##:##:##] = [hour:min:sec]
def printTime(seconds):
    #converts the time into their hour, min, and sec value
    hourPrint = seconds//3600
    minPrint = (seconds%3600)//60
    secPrint = (seconds%3600%60)

    #prints the time in the form [##:##:##]
    #If hourPrint, minPrint, or secPrint are only one number instead of two it will add on (0+hourPrint, 0+minPrint, 0+secPrint)
    time = "["

    #Checks to see if the hourPrint is of len one if it is it will add a zero in the front
    if(len(str(hourPrint)) == 1):
        time += f'0{hourPrint}:'
    else:
        time += f'{hourPrint}:'
    #Checks to see if the minPrint is of len one if it is it will add a zero in the front
    if(len(str(minPrint)) == 1):
        time += f'0{minPrint}:'
    else:
        time += f'{minPrint}:'
    #Checks to see if the secPrint is of len one if it is it will add a zero in the front
    if(len(str(secPrint)) == 1):
        time += f'0{secPrint}'
    else:
        time += f'{secPrint}'
    time += "]"
    #return the time
    return time

#Discord bot
class MyClient(discord.Client):

    #The bot uses async and await syntax that allows for the bot to do multiple tasks at once when await and async occurs 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #Set up timers
        self.whiteTimer = None
        self.blackTimer = None
        self.greyTimer = None

    #Function that runs when the bot starts up and prints to console when the bot is ready to be used
    async def on_ready(self):
        #Acess the bots user ID and also will send to the bot channel the log(details) of the game
        print('Logged on as {0}!'.format(self.user))
        botLog = self.get_channel(513918307716562944)
        await botLog.send("Thwart Omega Bot is now online.")

    #Function to start the reserved count down timer
    async def reservedCountDownTimer(self,channelId,gameChannel,player,message):
        global hasStarted, whiteRole, blackRole, greyRole, player1, player2
        #Take in channels needed
        channel = self.get_channel(channelId)
        game = self.get_channel(gameChannel)
        #Loop through until certain conditions are met
        while not self.is_closed():
            #This is to check to make sure that if player submits then to stop the count down
            if player.hasSubmitted:
                return
            #Edits the printed message and prints the players remeaning reserved time
            await message.edit(content = f"`Reserve Time:{printTime(player.reservedTime)}`")
            #Pauses the function for one second
            await asyncio.sleep(1)

            #Player loses the game if the run out of reserved time
            if player.reservedTime <= 0 and hasStarted:
                #Player lost game and removes roles
                await channel.send(f'<@{player.uid}> you have run out of reserved time and have lost the game')
                await game.send(f'<@{player.uid}> you have run out of reserved time and have lost the game')
                await message.guild.get_member(player1.uid).remove_roles(whiteRole)
                await message.guild.get_member(player2.uid).remove_roles(blackRole)
                if(len(playerList) == 3):
                    await message.guild.get_member(player3.uid).remove_roles(greyRole)
                print("removed")
                #Resets the playerList and hasStarted 
                playerList = []
                hasStarted = False
                return
            #Decrease counter for reservedTime by one
            player.reservedTime -= 1

    #Function that prints and updates the timer
    async def countDownTimer(self,channelId,gameChannel,player):
        global hasStarted, maxTime
        #Sets the counter for timeLeft
        timeLeft = maxTime
        #Sets the channel and message
        channel = self.get_channel(channelId)
        message = None
        while not self.is_closed():
            #Checks to see if the game has not been ended during game play
            if not hasStarted:
                await channel.send(f"Sorry, the game has not started yet")
                return
            #Checks to see that the player has not submitted if the player has it exits the function
            if player.hasSubmitted:
                return
            #Prints a new message if message the message = None
            #It will then print to the discord channel the timeLeft in the new message
            if message == None:
                message = await channel.send(f"`{printTime(timeLeft)}`")
            #Updates the current message with the new timeLeft value
            else:
                await message.edit(content = f"`{printTime(timeLeft)}`")
            #Function sleeps or stops for a second
            await asyncio.sleep(1)
            #If the timerLeft is less then 0 then it switches to reservedTime
            if timeLeft <= 0:
                reserve = self.loop.create_task(self.reservedCountDownTimer(channelId,gameChannel,player,message))
                return
            #Decreases the timeLeft by one
            timeLeft -= 1

    #Function that checks for various key words in messages sent by users and will then execute certain tasks
    async def on_message(self, message):
        global hasStarted, grid, player1, player2, player3, playerList, setTimer, maxTime, setReservedTimer, maxReservedTime, whiteRole, blackRole, greyRole

        #Boolean that returns wheter a message is sent by an admin or not
        isAdmin = message.author.guild_permissions.administrator

        #Unique ID for the game channel
        gameRoom = Enter channel id for game channel

        #Sets the roles for each channel
        whiteRole = message.guild.get_role(Enter role id for white player)
        blackRole = message.guild.get_role(Enter role id for black player)
        greyRole = message.guild.get_role(Enter role id for grey player)

        #Sets the unique ID for each channel
        whiteChannel = Enter channel id for white player
        blackChannel = Enter channel id for black player
        greyChannel = Enter channel id for grey player

        print(str(message.author.id) + ": " + message.content)

        #/stop command
        #Can only be used by admins on the server and will remove the roles of each player if the game is going on and close the bot
        if (isAdmin and message.content == "/stop"):
            #Checks to see if the game has started
            if (hasStarted):
                #Removes the role
                await message.guild.get_member(player1.uid).remove_roles(whiteRole)
                await message.guild.get_member(player2.uid).remove_roles(blackRole)
                #If their is a third player removes their role to
                if(len(playerList) == 3):
                    await message.guild.get_member(player3.uid).remove_roles(greyRole)
                    
            sleep(1)
            #Exits the bot and closes it
            await self.logout()
            await self.close()
        
        #/join command
        #Allows for users to join the game if it has not started and also checks that /join is in the sent message
        if len(message.content) >= len("/join") and message.content[0:5] == "/join" and not hasStarted:
    
            if message.content == "/join":
                #Checks if the user is not already in the playerList and then if true adds them
                if message.author.id not in playerList:
                    playerList.append(message.author.id)
                    print(message.author.id)
                #Else a message is sent saying the user is already in the player list
                else:
                    await message.channel.send("You are already in the player list!")
                    
            #Allows the admin to add players that are not already in the playerList
            if isAdmin and message.mentions:
                for m in message.mentions:
                    if m.id not in playerList:
                        playerList.append(m.id)
            #Prints the player list
            await message.channel.send(prettyPlayerList(playerList))

        #/leave command
        #Allows to exit the game if it has not started yet and also checks that /leave is in the sent message
        if len(message.content) >= len("/leave") and message.content[0:6] == "/leave" and not hasStarted:
            #Checks if the player is in the player list and will then remove them
            if message.content == "/leave":
                if message.author.id in playerList:
                    playerList.remove(message.author.id)
                else:
                    #Player is not in the player list and sent the message you are not in the player list
                    await message.channel.send("You are not in the player list!")
            #Allows the admins to kick users
            if isAdmin and message.mentions:
                for m in message.mentions:
                    if m.id in playerList:
                        playerList.remove(m.id)
            #Prints the player list
            await message.channel.send(prettyPlayerList(playerList))
            
        #/start command
        #Checks if (/start [##:##:##][##:##:##] = /start [##:##:##] = /start) anyone of these commands are in the message and that the playerList has two or three people
        if message.content[:6] == "/start" and (len(playerList) == 2 or len(playerList) == 3):
            #Checks if the message contains [##:##:##][##:##:##]
            #Where the first set of brakets correspond to maxTime and second set correspond to resereved Time
            #if the brackets are their in the correct strings positions, it will set maxTime and reserveTime
            if len(message.content)>=17 and message.content[7] == "[" and message.content[16] == "]":
                maxTime = convertTime(message.content[7:17])
            if(len(message.content)>=27 and message.content[17] == "[" and message.content[26] == "]"):
                maxReservedTime = convertTime(message.content[17:27])

            #Get the gameChannel
            gameChannel = self.get_channel(gameRoom)

            #Set the grid and players to their initial states
            grid = Grid(7, 7)
            player1 = Player(playerList[0],maxReservedTime,"white")
            player2 = Player(playerList[1],maxReservedTime,"black")
            #Sets the third players initial state
            if (len(playerList) == 3):
                player3 = Player(playerList[2],maxReservedTime,"grey")
                await message.guild.get_member(player3.uid).add_roles(greyRole)

            #Set the roles for the players    
            await message.guild.get_member(player1.uid).add_roles(whiteRole)
            await message.guild.get_member(player2.uid).add_roles(blackRole)
            #Sends a message saying which player is playing what color
            if (len(playerList) == 3):
                await self.get_channel(gameRoom).send("<@" + str(player1.uid) + "> is playing as White\n" + "<@" + str(player2.uid) + "> is playing as Black\n" + "<@" + str(player3.uid) + "> is playing as Grey")            
            else:
                 await self.get_channel(gameRoom).send("<@" + str(player1.uid) + "> is playing as White\n" + "<@" + str(player2.uid) + "> is playing as Black")   
            #await message.channel.send(grid.printGrid())

            #Draws the starting state for the grid and sends them to the needed channels which are the game room, whiteChannel, blackChannel, and greyChannel
            #Grey channel is only if their are three players
            grid.drawGrid()
            await self.get_channel(gameRoom).send(file=discord.File('board.png'))
            await self.get_channel(whiteChannel).send(file=discord.File('board.png'))
            await self.get_channel(blackChannel).send(file=discord.File('board.png'))
            if(len(playerList) == 3):
                await self.get_channel(greyChannel).send(file=discord.File('board.png'))

            #Sets hasStarted to true
            hasStarted = True

            #Starts the timers by calling the countDownTimer function for all the players
            self.whiteTimer = self.loop.create_task(self.countDownTimer(whiteChannel,gameRoom,player1))
            self.blackTimer = self.loop.create_task(self.countDownTimer(blackChannel,gameRoom,player2))
            if(len(playerList) == 3):
                self.greyTimer = self.loop.create_task(self.countDownTimer(greyChannel,gameRoom,player3))

        #/end command
        #Allows non admins and admins of the server to end the game if the message contains /end 
        if message.content == "/end" and message.author.id in playerList and hasStarted:
            #Removes the roles
            await message.guild.get_member(player1.uid).remove_roles(whiteRole)
            await message.guild.get_member(player2.uid).remove_roles(blackRole)
            if(len(playerList) == 3):
                await message.guild.get_member(player3.uid).remove_roles(greyRole)                
            #Resets player list and sets hasStarted to false
            playerList = []
            hasStarted = False

        #/timer command
        #Allows the user to change the timer if needed before the game starts
        if message.content[:7] == "/timer " and not hasStarted:
            #Converts the time by calling converTime
            maxTime = convertTime(message.content[7:])
            #Checks to see the time is not above 24hrs which is the largest amount of time that can be called
            if maxTime>24*3600:
                return
            print(maxTime)

        #/reserve
        #Allows the user to change the reserve timer if needed before the game starts
        if message.content[:9] == "/reserve " and not hasStarted:
            maxReservedTime = convertTime(message.content[9:])
            #Checks to see the time is not above 24hrs which is the largest
            if maxReservedTime>24*3600:
                return
            print(maxReservedTime)

        #/submit command
        #Submission System for the game
        #Checks to see if the message contains /submit and hasStarted if not it sends a message that the game needs to start first
        if message.content[:8] == "/submit " and not hasStarted:
            await message.channel.send(f'@{message.author} you need to start the game first')
        #Goes through the submission
        elif message.content[:8] == "/submit " and hasStarted:
            print("submit")
            #Flag is used to know if the move the player submits was valid 
            flag = False
            arr = message.content.split()
            #For two players the submission is in the form /submit W[ALPHA][NUM] B[ALPHA][NUM] an example is /submit WA2 BA3 
            #For two players and makes sure the right input was passed in
            if (len(playerList) == 2 and len(arr) == 3 and len(arr[1]) == 3 and len(arr[2]) == 3):
                #Set flag to true
                flag = True
                #Converts the strings to uppercase
                wLoc = arr[1].upper()
                bLoc = arr[2].upper()
                #Changes the order if the input is not W B and instead B W -> W B
                if wLoc[0] == "W" and bLoc[0] == "B":
                    wLoc, bLoc = wLoc, bLoc
                elif wLoc[0] == "B" and bLoc[0] == "W":
                    wLoc, bLoc = bLoc, wLoc
                else:
                    #Sends a message the move was invalid
                    flag = False
                    await message.channel.send("Invalid Move")
                #Creates a cell for the black and white moves
                white = Cell(int(wLoc[2])-1,"ABCDEFG".index(wLoc[1]),"white", 1)
                black = Cell(int(bLoc[2])-1,"ABCDEFG".index(bLoc[1]),"black", 1)
            #For three players the submission is in the form /submit W[ALPHA][NUM] B[ALPHA][NUM] G[ALPHA][NUM] an example is /submit WA2 BA3 GA4
            #For three players and makes sure the right input was passed in    
            elif(len(playerList) == 3 and len(arr) == 4 and len(arr[1]) == 3 and len(arr[2]) == 3 and len(arr[3]) == 3):
                #Sets flag to true
                flag = True
                #Converts the strings to uppercase
                wLoc = arr[1].upper()
                bLoc = arr[2].upper()
                gLoc = arr[3].upper()
                #Changes the order if the input is not in the order W B G and instead some other combination such as B G W it will take the values and place them in the appopriate locations W B G
                #Goes through the various combinations and makes sure they are in the form W B G
                if wLoc[0] == "W" and bLoc[0] == "B" and gLoc[0] == "G":
                    wLoc, bLoc, gLoc = wLoc, bLoc, gLoc
                elif wLoc[0] == "W" and bLoc[0] == "G" and gLoc[0] == "B":
                    wLoc, bLoc, gLoc = wLoc, gLoc, bLoc
                elif wLoc[0] == "G" and bLoc[0] == "W" and gLoc[0] == "B":
                    wLoc, bLoc, gLoc = bLoc, gLoc, wLoc
                elif wLoc[0] == "G" and bLoc[0] == "B" and gLoc[0] == "W":
                    wLoc, bLoc, gLoc = gLoc, bLoc, wLoc
                elif wLoc[0] == "B" and bLoc[0] == "G" and gLoc[0] == "W":
                    wLoc, bLoc, gLoc = gLoc, wLoc, bLoc
                elif wLoc[0] == "B" and bLoc[0] == "W" and gLoc[0] == "G":
                    wLoc, bLoc, gLoc = bLoc, wLoc, gLoc
                else:
                    #Sets flag to false and says invalid move
                    flag = False
                    await message.channel.send("Invalid Move")

                #Creates cells for white, black, grey
                white = Cell(int(wLoc[2])-1,"ABCDEFG".index(wLoc[1]),"white", 1)
                black = Cell(int(bLoc[2])-1,"ABCDEFG".index(bLoc[1]),"black", 1)
                grey = Cell(int(gLoc[2])-1,"ABCDEFG".index(gLoc[1]),"grey", 1)
                
            else:
                #Prints that the move was invalid
                await message.channel.send("Invalid Move")
            if(flag):
                #Means that the moves were valid for the player
                #Checks which player submitted 
                if message.author.id == player1.uid and message.channel.id == whiteChannel:
                    print("b1")
                    #If the player submitted and the move was valid it sets player.hasSubmitted to true and cancels the timer
                    #Also depending on the playerList a different function is called because for three players you can place three colors vs two which is only two colors
                    if (len(playerList) == 3 and player1.isValidThree(grid, white, black, grey)) or (len(playerList) == 2 and player1.isValid(grid, white, black)):
                        player1.hasSubmitted = True
                        self.whiteTimer.cancel()
                        await message.channel.send("Valid!")
                    else:
                        #Invalid move
                        await message.channel.send("Invalid Move")
                elif message.author.id == player2.uid and message.channel.id == blackChannel:
                    print("b2")
                    #If the player submitted and the move was valid it sets player.hasSubmitted to true and cancels the timer
                    #Also depending on the playerList a different function is called because for three players you can place three colors vs two which is only two colors
                    if (len(playerList) == 3 and player2.isValidThree(grid, white, black, grey)) or (len(playerList) == 2 and player2.isValid(grid, white, black)):
                        player2.hasSubmitted = True
                        self.blackTimer.cancel()
                        await message.channel.send("Valid!")
                    else:
                        #Invalid move
                        await message.channel.send("Invalid Move")
                elif len(playerList) == 3 and message.author.id == player3.uid and message.channel.id == greyChannel:
                    print("b3")
                    #If the player submitted and the move was valid it sets player.hasSubmitted to true and cancels the timer
                    #Also depending on the playerList a different function is called because for three players you can place three colors vs two which is only two colors
                    if (len(playerList) == 3 and player3.isValidThree(grid, white, black, grey)):
                        player3.hasSubmitted = True
                        self.greyTimer.cancel()
                        await message.channel.send("Valid!")
                    else:
                        #Invalid move
                        await message.channel.send("Invalid Move")
                

                #check if all players have submitted
                if ((player1.hasSubmitted and player2.hasSubmitted and len(playerList) == 2) or (player1.hasSubmitted and player2.hasSubmitted and player3.hasSubmitted and len(playerList) == 3)):
                    #If the players have submitted place the colors for black and white in the cells needed
                    player1.place(grid, player1.white)
                    player1.place(grid, player1.black)
                    player2.place(grid, player2.white)
                    player2.place(grid, player2.black)

                    #Resets the cells for each player in black and white
                    player1.white = Cell(0,0)
                    player1.black = Cell(0,0)
                    player2.white = Cell(0,0)
                    player2.black = Cell(0,0)

                    #If their is a third player
                    if(len(playerList) == 3):
                        #Place the the third players cells for black and white
                        player3.place(grid, player3.white)
                        player3.place(grid, player3.black)

                        #Reset the cells for black and white
                        player3.white = Cell(0,0)
                        player3.black = Cell(0,0)

                        #Place the cells for gray for each player
                        player1.place(grid,player1.grey)
                        player2.place(grid,player2.grey)
                        player3.place(grid,player3.grey)

                        #Reset the cells for grey
                        player1.grey = Cell(0,0)
                        player2.grey = Cell(0,0)
                        player3.grey = Cell(0,0)

                    #Adds a one second delay
                    await asyncio.sleep(1)

                    #Draw the board at this state of the game and send it to the needed channels
                    grid.drawGrid()
                    await self.get_channel(gameRoom).send(file=discord.File('board.png'))
                    await self.get_channel(whiteChannel).send(file=discord.File('board.png'))
                    await self.get_channel(blackChannel).send(file=discord.File('board.png'))
                    
                    if(len(playerList) == 3):
                        await self.get_channel(greyChannel).send(file=discord.File('board.png'))
                        player3.hasSubmitted = False

                    #Set player.hasSubmitted to false
                    player1.hasSubmitted = False
                    player2.hasSubmitted = False

                    #Check if the game is over by calling grid.isDone()
                    if grid.isDone():
                        await asyncio.sleep(1)
                        w, b, g = grid.score()
                        #Sets the winner to tie as default
                        winner = "It's a tie."
                        #For two players
                        if(len(playerList) == 2):
                            #If white has a higher score then white wins if black has a score black wins
                            if (w > b):
                                winner = "<@" + str(player1.uid) + ">, playing as White, wins!"
                            elif (b > w):
                                winner = "<@" + str(player2.uid) + ">, playing as Black, wins!"
                            #Print the winner
                            await self.get_channel(gameRoom).send("\nWhite: " + str(w) + "\nBlack: " + str(b) + "\n" + winner)
                        #For three players
                        elif(len(playerList) == 3):
                            #if white wins
                            if (w > b and w > g):
                                winner = "<@" + str(player1.uid) + ">, playing as White, wins!"
                            #if black wins
                            elif (b > w and b > g):
                                winner = "<@" + str(player2.uid) + ">, playing as Black, wins!"
                            #if gray wins
                            elif (g > w and g > b):
                                winner = "<@" + str(player3.uid) + ">, playing as Grey, wins!"
                            #Print the winner
                            await self.get_channel(gameRoom).send("\nWhite: " + str(w) + "\nBlack: " + str(b) + "\nGrey: " + str(g) + "\n" + winner)

                        #Remove the roles of the players and ends the timers
                        self.whiteTimer.cancel()
                        self.blackTimer.cancel()
                        await message.guild.get_member(player1.uid).remove_roles(whiteRole)
                        await message.guild.get_member(player2.uid).remove_roles(blackRole)
                        if(len(playerList) == 3):
                            self.greyTimer.cancel()
                            await message.guild.get_member(player3.uid).remove_roles(greyRole)
                        #Reset game
                        playerList = []
                        hasStarted = False
                    else:
                        #call timer functions and reset them for the next turn
                        self.whiteTimer = self.loop.create_task(self.countDownTimer(whiteChannel,gameRoom,player1))
                        self.blackTimer = self.loop.create_task(self.countDownTimer(blackChannel,gameRoom,player2))
                        if (len(playerList) == 3):
                            print("timer")
                            self.greyTimer = self.loop.create_task(self.countDownTimer(greyChannel,gameRoom,player3))
            
            

        #/sample creates a sample game for users who want to see a visual example of the board
        if message.content == "/sample" and isAdmin:
            #An 2d array that stores various paramaters for a cell
            samples = [[0,0,"white",1],[0,1,"white",1],[1,0,"black",2],[2,0,"red",2],[2,3,"white",1],[2,4,"black",1],[3,3,"white",2],[3,0,"black",2],[3,1,"black",1],[3,4,"black",1],
                       [4,4,"black",1],[4,3,"black",1],[3,2,"red",2],[6,6,"white",1]]

            #Places the cell in each specified position
            for s in samples:
                grid.board[s[0]][s[1]] = Cell(s[0],s[1],s[2],s[3])

            #Draws the grid and sends it in a message as text to the channel
            grid.drawGrid()
            #Uploads the file to the channel
            await message.channel.send(file=discord.File('board.png'))

        #/place command can be used by the admin to over ride certain moves
        if message.content[:7] == "/place " and hasStarted and isAdmin:
            #Takes in the move
            place, x, y, color, number = message.content.split()
            x = int(x)
            y = int(y)
            number = int(number)
            #Places the color in the specfied location
            grid.place(x,y,color,number)
            #Draws the grid
            grid.drawGrid()
            await message.channel.send(file=discord.File('board.png'))
            #await message.channel.send(grid.printGrid())

        #/score command can be used by users to test the score for each round instead of only testing the score at the end
        if message.content == "/score" and hasStarted:
            #Gets the score for each player at the moment
            w, b, g = grid.score()
            #await message.channel.send(grid.printGrid())
            #Draws the grid and also uploads the file of the grid as a message
            grid.drawGrid()
            await message.channel.send(file=discord.File('board.png'))
            #Sends the message of the players
            await message.channel.send("\nWhite: " + str(w) + "\nBlack: " + str(b) + "\nGrey: " + str(g))

        #/draw command can be used by users to see the printed version of the board sent as a message if their is weak internet connections and also upload the board as a file 
        if message.content == "/draw" and hasStarted:
            grid.drawGrid()
            await message.channel.send(file=discord.File('board.png'))

        #/fill command is used for testing purposes for admins should be used only for three players though
        if message.content == "/fill" and hasStarted and isAdmin:
            #Fills the board with random cells of various colors
            grid.fill()
            #Draws the grid and uploads the image file of the board
            grid.drawGrid()
            await message.channel.send(file=discord.File('board.png'))


#Player class 
class Player:
    def __init__(self, uid, time, color):
        #Stores the fields for the player class
        #A player has a field to store their user id
        self.uid = uid
        #A player has a field that specifies where they place their colors each move
        self.white = Cell(0,0)
        self.black = Cell(0,0)
        self.grey = Cell(0,0)
        #A player has a field that stores the amount of reserve time they have left
        self.reservedTime = time
        #A player has a field that stores what color they play as
        self.color = color
        #A player has a field that specifies whether they have submitted or not
        self.hasSubmitted = False

    #Returns the boolean values True if the cells submitted by the player are valid or False otherwise
    def isValid(self, grid, white, black):
        print("is the move valid")
        print(white.color)
        print(black.color)
        #Makes sure the correct cells colors are submitted
        if (white.color == "white" and black.color == "black"):
            print("2")
            #Makes sure no cells are in the same place
            if (white.x != black.x or white.y != black.y):
                print("3")
                #Makes sure the cells are in bounds
                if (0 <= white.x < grid.height and 0 <= white.y < grid.width and 0 <= black.x < grid.height and 0 <= black.y < grid.width):
                    print("4")
                    #Makes sure the cells colors are blank and not already filled
                    if grid.board[white.x][white.y].color == "blank" and grid.board[black.x][black.y].color == "blank":
                        print("5")
                        self.white = white
                        self.black = black
                        #Return true since all of these conditions are met
                        return True
        return False

    #Makes sure the cells that are passed are valid for three players
    def isValidThree(self, grid, white, black, grey):
        print("is valid for three players")
        print(white.color)
        print(black.color)
        print(grey.color)
        #Makes sure the correct cells colors are submitted
        if (white.color == "white" and black.color == "black" and grey.color == "grey"):
            print("2")
            #Makes sure no cells are in the same place
            if (white.x != black.x or white.y != black.y) and (white.x != grey.x or white.y != grey.y) and (grey.x != black.x or grey.y != black.y):
                print("3")
                #Makes sure the cells are in bounds
                if (0 <= white.x < grid.height and 0 <= white.y < grid.width and 0 <= black.x < grid.height and 0 <= black.y < grid.width and 0 <= grey.x < grid.height and 0 <= grey.y < grid.width):
                    print("4")
                    #Makes sure the cells colors are blank and not already filled
                    if grid.board[white.x][white.y].color == "blank" and grid.board[black.x][black.y].color == "blank" and grid.board[grey.x][grey.y].color == "blank":
                        print("5")
                        self.white = white
                        self.black = black
                        self.grey = grey
                        #Returns true since all the condition are met
                        return True
        return False

    #Places the color in the cell 
    def place(self, grid, cell):
        x = cell.x
        y = cell.y
        #Sets the color in the cell if it is blank
        if grid.board[x][y].color == "blank":
            grid.board[x][y] = cell
        #Sets the color in the cell to two if their already exits in the same cell the color
        elif grid.board[x][y].color == cell.color:
            grid.board[x][y].number += 1
        #Sets the color to the burn color because the colors placed are not the same
        else:
            grid.board[x][y] = Cell(x,y,"red",2)

#Cell Class
class Cell:
    def __init__(self, x, y, color = "blank", number = 0):
        #Create the fields
        #Sets the x,y (row,col) location of the cell in the grid
        self.x = x
        self.y = y
        #Sets the color in the cell
        self.color = color
        #Sets the number of a certain color within a cell
        self.number = number

#Grid Class
class Grid:
    def __init__(self, height=7, width=7):
        #Create the fields
        #Sets the height and width of the board (7x7)
        self.height = height
        self.width = width
        #Make the board
        board = []
        for i in range(height):
            #Go through the row and the cell and its locations
            row = []
            for j in range(width):
                row.append(Cell(i,j))
            #Adds the row to the board
            board.append(row)
        #Sets the board which is a 2d array
        self.board = board

    #Used for testing purposes and fills the board with random colors should only be used for three players though
    def fill(self):
        for i in range(self.height):
            for j in range(self.width):
                self.board[i][j] = Cell(i,j,["white","white","white","black","black","black","grey","grey","grey","red","red","blank"][randint(0,12-1)],[1,1,2,2,3][randint(0,4)])

    #Returns True if their is less then 8(8 for three players) or 3(3 for two players) blank squares on the board otherwise False
    def isDone(self):
        global playerList
        #Counter to count the number of blank squares
        blank = 0
        #Count the number of blanks
        for i in range(self.height):
            for j in range(self.width):
                if self.board[i][j].color == "blank":
                    blank+=1
        #for two players if their are less then 3 blanks the game is over
        if len(playerList) == 2 and blank <= 3:
            return True
        #for three players if their are less then 8 blanks the game is over
        if len(playerList) == 3 and blank <= 8:
            return True
        return False

    #Draws the board using ASCII instead of images and can be used as a setting for users with weak internet connections
    def printGrid(self):
        grid = "```" + "  " + "A  B  C  D  E  F  G  H  I  J  K  L  M  N  O  P  Q  R  S  T  U  V  W  X  Y  Z  "[:self.width*3] + "\n"
        for i in range(self.height):
            grid += str(i+1) + " "
            #Goes through the grid
            for j in range(self.width):
                #Prints .. if their are blanks
                if self.board[i][j].color == "blank":
                    grid += ".. "
                #Prints 1, 2, or 3 B depending on the number of blacks
                elif self.board[i][j].color == "black":
                    if self.board[i][j].number == 1:
                        grid += "B  "
                    elif self.board[i][j].number == 2:
                        grid += "BB "
                    else:
                        grid += "BBB"
                #Prints 1, 2, or 3 W depending on the number of whites
                elif self.board[i][j].color == "white":
                    if self.board[i][j].number == 1:
                        grid += "W  "
                    elif self.board[i][j].number == 2:
                        grid += "WW "
                    else:
                        grid += "WWW"
                #Prints 1, 2, or 3 G depending on the number of greys
                elif self.board[i][j].color == "grey":
                    if self.board[i][j].number == 1:
                        grid += "G  "
                    elif self.board[i][j].number == 2:
                        grid += "GG "
                    else:
                        grid += "GGG"
                #For burns
                else:
                    grid+="XX "
            grid += "\n"

        grid += "```"
        
        print(grid)
        return grid

    #Draws the grid by using image files
    def drawGrid(self):

        #Opens the needed images
        letters = Image.open("abcdefg.png")
        
        topleft = Image.open("topleft.png")
        nothing = Image.open("topleft.png")
        #nothingtop = Image.open("nothingtop.png")
        
        w1 = Image.open("w1.png")
        w2 = Image.open("w2.png")
        b1 = Image.open("b1.png")
        b2 = Image.open("b2.png")
        g1 = Image.open("g1.png")
        g2 = Image.open("g2.png")

        w3 = Image.open("w3.png")
        b3 = Image.open("b3.png")
        g3 = Image.open("g3.png")
        #r = Image.open("r.png")
        r = Image.open("rred.png")
        blank = Image.open("blank.png")

        #Creates the board and adds in the images by concatating the topleft, letters images, and nothing horizontally
        board = concat_h(topleft, letters)
        board = concat_h(board, nothing)

        #Loops through the board and depedning on the color at the cell contanates a certain image
        for i in range(7):
            row = Image.open(str(i+1) + ".png")
            for j in range(7):
                #Takes the color at the cell and gets the image needed for the color
                #Sets cell to blank as default
                cell = blank
                #If the color at position (i,j) in the grid is blank set cell to blank
                if self.board[i][j].color == "blank":
                    cell = blank
                #If the color at position (i,j) in the grid is white set cell to white
                #Also depending on the number of white at the position in the board set the cell image to the specific one for 1,2,3
                elif self.board[i][j].color == "white":
                    if self.board[i][j].number == 1:
                        cell = w1
                    elif self.board[i][j].number == 2:
                        cell = w2
                    else:
                        cell = w3
                #If the color at position (i,j) in the grid is black set cell to black
                #Also depending on the number of black at the position in the board set the cell image to the specific one for 1,2,3
                elif self.board[i][j].color == "black":
                    if self.board[i][j].number == 1:
                        cell = b1
                    elif self.board[i][j].number == 2:
                        cell = b2
                    else:
                        cell = b3
                #If the color at position (i,j) in the grid is grey set cell to grey
                #Also depending on the number of grey at the position in the board set the cell image to the specific one for 1,2,3
                elif self.board[i][j].color == "grey":
                    if self.board[i][j].number == 1:
                        cell = g1
                    elif self.board[i][j].number == 2:
                        cell = g2
                    else:
                        cell = g3
                #If it is none of these the set the cell to r which is red and its a burn
                else:
                    cell = r
                #Concatenates the image cell to the whole row
                row = concat_h(row, cell)
            #Concatenates the row to the board
            row = concat_h(row, Image.open(str(i+1) + ".png"))
            board = concat_v(board, row)
        
        row = nothing
        #Concatenates the letters to the board
        row = concat_h(row, letters)
        row = concat_h(row, nothing)
        board = concat_v(board, row)
        
        #Saves the board to the file
        board.save('board.png')
        #board.show()

    
    #Places a certain color at a cell
    def place(self, x, y, color="blank", number=0):
        self.board[x][y].x = x
        self.board[x][y].y = y
        self.board[x][y].color = color
        self.board[x][y].number = number

    #Gets the score of each player in the game
    #Returns a list of the players scores
    #Uses the Floodfill algorithm 
    def score(self):
        #Stores the various groups of each player
        whiteGroups = []
        blackGroups = []
        greyGroups = []

        #Visited array
        visited = []

        #Sets visited array to false
        for i in range(self.height):
            visited.append([False]*self.width)

        #Goes though the board
        for i in range(self.height):
            for j in range(self.width):
                #If not visited a certain cell
                if not visited[i][j]:
                    #BFS through the board starting at the cell and then go through all the neighbors and then their neigbots if the color is equal to the starting cell
                    #if they are the same color then increment the groupSize counter
                    #Set group size to zero
                    groupSize = 0
                    #Get the color of the present cell
                    curColor = self.board[i][j].color
                    #initialize the queue
                    queue = []
                    #Add on the location to the queue
                    queue.append([i,j])
                    #Set that visited the location is true
                    visited[i][j] = True
                    #Loop through until the queue is empty
                    while queue:
                        #Take the first location in the queue at position zero
                        point = queue.pop(0)
                        #print(curColor + " " + str(point[0]) + " " + str(point[1]))
                        #increment group size because you know the current point is a valid color
                        groupSize+=self.board[point[0]][point[1]].number
                        #visited[point[0]][point[1]] = True
                        dx = [0,1,0,-1]
                        dy = [1,0,-1,0]
                        #Loop through all four directions up, down, left, and right 
                        for d in range(4):
                            #Get new x and y coordinates
                            x = point[0] + dx[d]
                            y = point[1] + dy[d]
                            #Make sure the x and y coordiantes are valid and that the color at the location is equal to the color of point and that you have not visited the location yet
                            if self.valid(x,y) and not visited[x][y] and self.board[x][y].color == curColor:
                                queue.append([x,y])
                                visited[x][y] = True
                    #Add on to the the lists for each player the groupSize for what color it was
                    if curColor == "white":
                        whiteGroups.append(groupSize)
                    elif curColor == "black":
                        blackGroups.append(groupSize)
                    elif curColor == "grey":
                        greyGroups.append(groupSize)
                        
        print(whiteGroups)
        print(blackGroups)
        print(greyGroups)

        #Get the scores for each player
        #All scores start at one
        whiteScore = 1
        blackScore = 1
        greyScore = 1
        #Go through the white Groups and take all of their products
        if whiteGroups:
            for n in whiteGroups:
                whiteScore *= n
        else:
            #if their are no groups the score must be zero
            whiteScore = 0
        #Go through the black Groups and take all of their products    
        if blackGroups:
            for n in blackGroups:
                blackScore *= n
        else:
            #if their are no groups the score must be zero
            blackScore = 0
        #Go through the grey Groups and take all of their products
        if greyGroups:
            for n in greyGroups:
                greyScore *= n
        else:
            #if their are no groups the score must be zero
            greyScore = 0
        
        return [whiteScore, blackScore, greyScore]
    
    #Function that returns True if a certain position (i,j) is valid or False otherwise
    def valid(self, i, j):
        return i >= 0 and i < self.height and j >= 0 and j < self.width

#Runs the bot                    
client = MyClient()
client.run('Insert bot token here') 
