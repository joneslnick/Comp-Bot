import discord
from discord.ext import commands
import time
import datetime
import asyncio


description = "Manages Comp RSVP's. Pings all participating members when 5 reactions are received."
intents = discord.Intents.default()
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix='/', description=description, intents=intents)

#Definately better ways to handle this
f = open("DISCORD_TOKEN.txt", "r")
TOKEN = f.read()
f.close()


ID_NUM = 0
COMP_EVENTS = []
TIME_REACTIONS = {
    ":clock12:": datetime.time(0,0,0),
    ":clock1230:": datetime.time(0,30,0),
    ":clock1:": datetime.time(13,0,0),
    ":clock130:": datetime.time(14,30,0),
    ":clock2:": datetime.time(14,0,0),
    ":clock230:": datetime.time(14,30,0),
    ":clock3:": datetime.time(15,0,0),
    ":clock330:": datetime.time(15,30,0),
    ":clock4:": datetime.time(16,0,0),
    ":clock430:": datetime.time(16,30,0),
    ":clock5:": datetime.time(17,0,0),
    ":clock530:": datetime.time(17,30,0),
    ":clock6:": datetime.time(18,0,0),
    ":clock630:": datetime.time(18,30,0),
    ":clock7:": datetime.time(19,0,0),
    ":clock730:": datetime.time(19,30,0),
    ":clock8:": datetime.time(20,0,0),
    ":clock830:": datetime.time(20,30,0),
    ":clock9:": datetime.time(21,0,0),
    ":clock930:": datetime.time(22,30,0),
    ":clock10:": datetime.time(22,0,0),
    ":clock1030:": datetime.time(22,30,0),
    ":clock11:": datetime.time(23,0,0),
    ":clock1130:": datetime.time(23,30,0),

}

class CompEvent:

    def __init__(self, id_num, ctx, message):
        self.id = id_num
        self.ctx = ctx
        self.message = message
        self.reactions = [] #List of (Reaction, User) Tuples
        self.players_ready = 0
        self.player_list = []
        self.start_time = datetime.datetime.now().time() #Set current time at creation (needs to be constantly updated)
    
    async def ProcessReactions(self):
        global COMP_EVENTS
        MIN_PLAYERS = 3

        self.curr_time = datetime.datetime.now().time()
        self.player_list = []
        self.players_ready = 0
        
        for reaction in self.reactions:
            print(reaction)

            if reaction[1] in self.player_list: #User has reacted multiple times, ignore this reaction
                print("User has already reacted. Ignoring reaction")
                pass
            else:
                self.player_list.append(reaction[1])

            if reaction[0].custom_emoji:
                if reaction[0].emoji.name == "csgo": #User can play right now
                    print("Someone can play right now!")
                    self.players_ready += 1
            else:
                if "clock" in reaction[0].emoji: #User can play at a later time
                    print("Someone can play at a later day!")
                    time = ProcessTime(reaction[0]) #Returns datetime object
                    if time < datetime.date.time().time(): #If reaction time is prior to curr_time (player is available)
                        self.players_ready += 1

        print(f"{self.players_ready} are ready for comp!")
        
        if self.players_ready >= MIN_PLAYERS:
            message = ""
            for player in self.player_list:
                message += f"{player.mention} "
            message += f"The time is nigh!"
            await self.ctx.send(message)
            COMP_EVENTS.remove(self)

                    
    
    def ProcessTime(time_reaction):
        global TIME_REACTIONS
        return TIME_REACTIONS.get(time_reaction)



@bot.event
async def on_ready():
    print("Logged in as %s" % bot.user.name)

@bot.command()
async def comp(ctx):
    global ID_NUM
    global COMP_EVENTS

    ID_NUM += 1
    await ctx.message.delete()
    sent_message = await ctx.send(f"<@&759568485352603693> @{ctx.author} has called for Comp! \n\t Players Ready: 0")
    COMP_EVENTS.append(CompEvent(ID_NUM, ctx, sent_message)) #Create new event with new ID

@bot.event
async def on_reaction_add(reaction, user):
    global COMP_EVENTS

    for event in COMP_EVENTS:
        if event.message.id == reaction.message.id: #Reaction was added to a valid comp event
            print(f"User {user} has reacted with {reaction}")
            event.reactions.append((reaction,user)) #Add reaction to list of reactions for specific event
            
        await event.ProcessReactions()
        await event.message.edit(content=f"<@&759568485352603693> @{event.ctx.author} has called for Comp! \n\t Players Ready: {event.players_ready}")

@bot.event
async def on_reaction_remove(reaction, user):
    global COMP_EVENTS

    for event in COMP_EVENTS:
        if event.message.id == reaction.message.id: #Reaction was removed from a valid comp event
            print(f"User {user} has removed their reaction of {reaction}")
            print(event.reactions)
            event.reactions.remove((reaction,user)) #Remove reaction from reaction list
        await event.ProcessReactions()
        await event.message.edit(content=f"<@&759568485352603693> @{event.ctx.author} has called for Comp! \n\t Players Ready: {event.players_ready}")

bot.run(TOKEN)

