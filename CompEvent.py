from datetime import date, datetime, time, timedelta

TIME_REACTIONS = {
    ":clock12:": time(0,0,0),
    ":clock1230:": time(0,30,0),
    ":clock1:": time(13,0,0),
    ":clock130:": time(14,30,0),
    ":clock2:": time(14,0,0),
    ":clock230:": time(14,30,0),
    ":clock3:": time(15,0,0),
    ":clock330:": time(15,30,0),
    ":clock4:": time(16,0,0),
    ":clock430:": time(16,30,0),
    ":clock5:": time(17,0,0),
    ":clock530:": time(17,30,0),
    ":clock6:": time(18,0,0),
    ":clock630:": time(18,30,0),
    ":clock7:": time(19,0,0),
    ":clock730:": time(19,30,0),
    ":clock8:": time(20,0,0),
    ":clock830:": time(20,30,0),
    ":clock9:": time(21,0,0),
    ":clock930:": time(22,30,0),
    ":clock10:": time(22,0,0),
    ":clock1030:": time(22,30,0),
    ":clock11:": time(23,0,0),
    ":clock1130:": time(23,30,0),

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

        self.player_list = []
        
        for reaction in self.reactions:

            if reaction[1] in self.player_list: #User has reacted multiple times, ignore this reaction
                print("User has already reacted. Ignoring reaction")
                pass

            if reaction[0].custom_emoji:
                if reaction[0].emoji.name == "csgo": #User can play right now
                    print("Someone can play right now!")
                    self.player_list.append(reaction[1])
            else:
                if "clock" in reaction[0].emoji: #User can play at a later time
                    print("Someone can play at a later day!")
                    time = self.ProcessTime(reaction[0]) #Returns datetime object
                    if time < time.now().time(): #If reaction time is prior to curr_time (player is available)
                        self.players_lis.append(reaction[1])

        print(f"{len(self.player_list)} are ready for comp!")
        
        if len(self.player_list) >= MIN_PLAYERS:
            message = ""
            for player in self.player_list:
                message += f"{player.mention} "
            message += f"The time is nigh!"
            await self.ctx.send(message)
            
            return "GameStarted"
        return 
                   
    def ProcessTime(self, time_reaction):
        global TIME_REACTIONS
        return TIME_REACTIONS.get(time_reaction)