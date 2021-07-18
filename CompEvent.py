from datetime import datetime, time
import emoji


#Time handling can be greatly improved. Issues with 0000 and 0030 (midnight)
TIME_REACTIONS = {
    ":twelve_o’clock:": time(0,0,0),
    ":twelve-thirty:":  time(0,30,0),
    ":one_o’clock:":    time(13,0,0),
    ":one-thirty:":     time(13,30,0),
    ":two_o’clock:":    time(14,0,0),
    ":two-thirty:":     time(14,30,0),
    ":three_o’clock:":  time(15,0,0),
    ":three-thirty:":   time(15,30,0),
    ":four_o’clock:":   time(16,0,0),
    ":four-thirty:":    time(16,30,0),
    ":five_o’clock:":   time(17,0,0),
    ":five-thirty:":    time(17,30,0),
    ":six_o’clock:":    time(18,0,0),
    ":six-thirty:":     time(18,30,0),
    ":seven_o’clock:":  time(19,0,0),
    ":seven-thirty:":   time(19,30,0),
    ":eight_o’clock:":  time(20,0,0),
    ":eight-thirty:":   time(20,30,0),
    ":nine_o’clock:":   time(21,0,0),
    ":nine-thirty:":    time(21,30,0),
    ":ten_o’clock:":    time(22,0,0),
    ":ten-thirty:":     time(22,30,0),
    ":eleven_o’clock:": time(23,0,0),
    ":eleven-thirty:":  time(23,30,0),
}

class CompEvent:
    def __init__(self, id_num, ctx, message):
        self.id = id_num
        self.ctx = ctx
        self.message = message

        self.reactions = [] #List of (Reaction, User) Tuples
        self.player_list = []
        self.start_time = datetime.now() #Set current time at creation (needs to be constantly updated)
    
    async def selfDestruct(self):
        await self.message.delete() #Remove message on destruction
    
    async def ProcessReactions(self):
        MIN_PLAYERS = 5
        
        self.player_list = [] #Clear list in case reactions were removed

        for reaction in self.reactions:
            if reaction[1] in self.player_list: #User has reacted multiple times, ignore this reaction
                pass

            elif reaction[0].custom_emoji:
                if reaction[0].emoji.name == "csgo": #User can play right now
                    self.player_list.append(reaction[1])
            else:
                demoji = emoji.demojize(str(reaction[0]))

                if ("clock" in demoji) or ("thirty" in demoji): #User can play at a later time
                    time = self.ProcessTime(demoji) #Returns datetime object
                    print(f"React Time: {time} VS. Current Time: {datetime.now().time()}")
                    if (time < datetime.now().time()): #If reaction time is prior to current
                        self.player_list.append(reaction[1])

        print(f"{len(self.player_list)} are ready for comp!")
        
        if len(self.player_list) >= MIN_PLAYERS:
            message = ""
            for player in self.player_list:
                message += f"{player.mention} "
            message += "The time is nigh!"
            await self.ctx.send(message)
            
            return True #Game successfully started
        return False 
                   
    def ProcessTime(self, time_reaction):
        return TIME_REACTIONS.get(time_reaction)

