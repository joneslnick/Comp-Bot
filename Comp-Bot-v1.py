from datetime import datetime, timedelta
import os
import discord
from discord.ext import commands
from CompEvent import CompEvent


description = "Manages Comp RSVP's. Pings all participating members when 5 reactions are received."
intents = discord.Intents.default()
intents.members = True
intents.reactions = True
intents.emojis = True


BOT = commands.Bot(command_prefix='/', description=description, intents=intents)
ID_NUM = 0
COMP_GROUP_ID = "@&759568485352603693"
COMP_EVENTS = []
EXPIRE_TIME = 4 #Hours before an event will expire and self delete


def main():
    BOT.run(RetrieveToken())

@BOT.event
async def on_ready():
    print("Logged in as %s" % BOT.user.name)

@BOT.command()
async def comp(ctx):
    global COMP_EVENTS
    global ID_NUM

    ID_NUM += 1
    await ctx.message.delete()
    sent_message = await ctx.send(f"<{COMP_GROUP_ID}> @{ctx.author} has called for Comp! \n\t Players Ready: 0")
    COMP_EVENTS.append(CompEvent(ID_NUM, ctx, sent_message)) #Create new event with new ID

@BOT.event
async def on_reaction_add(reaction, user):
    global COMP_EVENTS
    global COMP_GROUP_ID

    for event in COMP_EVENTS:
        if event.message.id == reaction.message.id: #Reaction was added to a valid comp event
            print(f"User {user} has reacted with {reaction.emoji}")
            event.reactions.append((reaction,user)) #Add reaction to list of reactions for specific event
            
        game = await event.ProcessReactions()
        if game == "GameStarted":
            COMP_EVENTS.remove(event)
        else:
            await event.message.edit(content=f"<{COMP_GROUP_ID}> @{event.ctx.author} has called for Comp! \n\t Players Ready: {len(event.player_list)}")

@BOT.event
async def on_reaction_remove(reaction, user):

    for event in COMP_EVENTS:
        if event.message.id == reaction.message.id: #Reaction was removed from a valid comp event
            print(f"User {user} has removed their reaction of {reaction.emoji}")
            event.reactions.remove((reaction,user)) #Remove reaction from reaction list
        await event.ProcessReactions()
        await event.message.edit(content=f"<{COMP_GROUP_ID}> @{event.ctx.author} has called for Comp! \n\t Players Ready: {len(event.player_list)}")
    return 

async def checkTimeout():
    await BOT.wait_until_ready()
    while not BOT.is_closed:
        
        for event in COMP_EVENTS:
            if datetime.now() > event.start_time + timedelta(hours = EXPIRE_TIME): #Event has expired
                event.selfDestruct()
                COMP_EVENTS.remove(event)
        os.sleep(300) #Wait 5 minutes before checking again


def RetrieveToken():
    #Definately better ways to handle this
    with open("DISCORD_TOKEN.txt","r") as file:
        token = file.read()
        file.close()
    
    return token

if __name__ == '__main__':
    main()






