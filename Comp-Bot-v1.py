from datetime import datetime, timedelta
import os
import discord
from discord.ext import commands, tasks
from discord.utils import get
from CompEvent import CompEvent


description = "Manages Comp RSVP's. Pings all participating members when 5 reactions are received."
intents = discord.Intents.default()
intents.members = True
intents.reactions = True
intents.emojis = True


BOT = commands.Bot(command_prefix='/', description=description, intents=intents)
ID_NUM = 0 #Each event is assigned a unique ID for record keeping (incr by one)
COMP_EVENTS = []
EXPIRE_TIME = 2 #Hours before an event will expire and self delete
LAST_CALL = None

ADMIN_ROLE = "Bot Wrangler"
PING_ROLE = "Comp"

class Cog(commands.Cog):
    def __init__(self, bot):
        self.index = 0
        self.bot = bot
        self.CheckTimeout.start()
    
    @tasks.loop(minutes=2)
    async def CheckTimeout():
        print("Checking if any events have expired")
        for event in COMP_EVENTS:
            if (datetime.now() > (event.start_time + timedelta(hours = EXPIRE_TIME))): #Event has expired
                await event.selfDestruct()
                COMP_EVENTS.remove(event)

def main():
    BOT.run(RetrieveToken())
    Cog(BOT)

@BOT.event
async def on_ready():
    print(f"Logged in as {BOT.user.name}")

@BOT.command(name="comp", pass_context=True)
async def CreateEvent(ctx):
    global COMP_EVENTS
    global ID_NUM
    global LAST_CALL

    if "reset" in ctx.message.content.lower(): #Allow bot wrangler to reset LAST_CALL timer
        if RetrieveRole(ctx, ADMIN_ROLE) in ctx.author.roles: #
            LAST_CALL = None #Reset timer
            for event in COMP_EVENTS:
                await event.selfDestruct()
            COMP_EVENTS.clear()
        else:
            await ctx.message.author.send("You lack the necessary role to perform this command.")
        await ctx.message.delete() #Delete command call
        return
              

    if ((LAST_CALL is None) or 
        (datetime.now() > (LAST_CALL + timedelta(minutes=10)))): #Prevent spamming command
        ID_NUM += 1
        
        role = RetrieveRole(ctx, PING_ROLE)
        if role is not None:
            mention = role.mention
        else:
            mention = "No Role Found"

        sent_message = await ctx.send(f"{mention} @{ctx.author} has called for Comp! \n\t Players Ready: 0")
        COMP_EVENTS.append(CompEvent(ID_NUM, ctx, sent_message)) #Create new event with new ID
        LAST_CALL = datetime.now()
    else:
        await ctx.message.author.send("This command has been called too recently. Please try again later!") #DM command user to stop spamming

    await ctx.message.delete() #Delete the command request message (regardless of whether a game is formed or not)
    return

@BOT.event
async def on_reaction_add(reaction, user):
    global COMP_EVENTS

    for event in COMP_EVENTS:
        if event.message.id == reaction.message.id: #Reaction was added to a valid comp event
            print(f"User {user} has reacted with {reaction.emoji}")
            event.reactions.append((reaction,user)) #Add reaction to list of reactions for specific event
            
        game = await event.ProcessReactions()

        role = RetrieveRole(event.ctx, PING_ROLE)
        if role is not None:
            mention = role.mention
        else:
            mention = "No Role Found"

        await event.message.edit(content=f"{mention} @{event.ctx.author} has called for Comp! \n\t Players Ready: {len(event.player_list)}")
        if game: #If game was started successfully
            await event.selfDestruct()
            COMP_EVENTS.remove(event)
    return
            

@BOT.event
async def on_reaction_remove(reaction, user):

    for event in COMP_EVENTS:
        if event.message.id == reaction.message.id: #Reaction was removed from a valid comp event
            print(f"User {user} has removed their reaction of {reaction.emoji}")
            event.reactions.remove((reaction,user)) #Remove reaction from reaction list
        await event.ProcessReactions()

        role = RetrieveRole(event.ctx, PING_ROLE)
        if role is not None:
            mention = role.mention
        else:
            mention = "No Role Found"

        await event.message.edit(content=f"{mention} @{event.ctx.author} has called for Comp! \n\t Players Ready: {len(event.player_list)}")
    return 



def RetrieveToken():
    #Definately better ways to handle this
    with open("DISCORD_TOKEN.txt","r") as file:
        token = file.read()
        file.close()
    
    return token

def RetrieveRole(ctx, roleName):
    role = get(ctx.guild.roles, name=roleName) #Retrieves role with string name of exactly roleName
    if not role:
        return None
    else:
        return role

if __name__ == '__main__':
    main()






