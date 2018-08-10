import discord
import re
import asyncio
import datetime

with open('login.txt') as f:
    TOKEN = f.read()

client = discord.Client()
role = None

def add_to_dictionary(dictionary, word):
    dictionary[re.compile(''.join([letter+'+\\s*?.?' for letter in word]))] = word

def get_role(role_name, serverid):
    server = client.get_server(serverid)
    if server is not None:
        for role in server.roles:
            if role.name == role_name:
                return role
        print('no role set')
    else:
        print("SERVER IS NONE")

def check_muted_role():
    with open('mutedchannel.txt', 'r') as f:
        mutedChannel = f.read()
        if mutedChannel != "":
            split = mutedChannel.split(" ")
            global role 
            role = get_role(split[1], split[0])
            print(str(role) + ' has been set to muted role')

async def addToList(listName, dictionary, message):
    try:
        newWord = message.content.split(' ', 1)[1]
        if newWord in dictionary.values():
            await client.send_message(message.author, "%s is already in the %s" % (newWord, listName))
        else:
            with open("%s.txt" % listName, "a+") as f:
                f.write("\n" + newWord)
            add_to_dictionary(dictionary, newWord)
            await client.send_message(message.author, "%s has been added to the %s" % (newWord, listName))
    except IndexError:
        print("No second word given")  

async def removeFromList(listName, dictionary, message):
    try:
        newWord = message.content.split(' ', 1)[1]
        if newWord in dictionary.values():
            del dictionary[(re.compile(''.join([letter+'+\\s*?.?' for letter in newWord])))]
            tempList = []
            with open('%s.txt' % listName, 'r') as f:
                for line in f:
                    if line != newWord and line != (newWord + '\n') and line != '\n':
                        tempList.append(line)
            with open('%s.txt' % listName, 'w') as f:
                for word in tempList:
                    f.write(word)
            await client.send_message(message.author, "%s has been removed from the %s" % (newWord, listName))
        else:
            await client.send_message(message.author, "%s is not present in the  %s" % (newWord, listName))
    except IndexError:
        print("No second word given")

async def blEvent(message):
    # EZ - MUTED
    await client.delete_message(message)
    if role is None:
        await client.send_message(message.channel, "admin needs to create a muted role using !setmutedrole")
    else:
        await client.replace_roles(message.author, role)
        await client.send_message(message.channel, message.author.name + " has been muted due to blacklisted word")
    # HARD - BAN
    # await client.delete_message(message)
    # client.ban(message.author, delete_message_days = 1)
    # await client.send_message(message.author, "contact admin for unban from " + message.server.name)

async def glEvent(message, word):

    #EZ - ONLY MUTE THAT CURSE WORD
    #if db:muted == 0:
    #   if now-start_time > 1:
    #       start_freq = freq
    #       start_time = now
    #   elif now-start_time<1 minute and freq-start_freq>3:
    #       db: muted = 1
    #       await client.delete_message(message)
    #       await client.send.message(message.channel, "the usage for a curse word has been muted")
    #else:
    #   await client.delete_message(message)
    pass
    #HARD - MUTE ALL MESSAGES FROM AUTHOR
    # # if now-start_time<1 minute and freq-start_freq>3 and (not in queue or db:muted)
    # await client.delete_message(message)
    # #start_time = now
    # #start_freq = freq
    # await client.send_message(message.author, 
    #     "you have been muted for a minute due to multiple usages of the same curse word within a minute from " 
    #     + message.server.name)
    # client.add_roles(message.author, ['muted'])
    # #sleep
    # client.remove_roles(message.author, ['muted'])
    #create a variable to see if text is valid

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    check = True
    if message.author == client.user:
        return

    if "admin" not in [y.name.lower() for y in message.author.roles]:
        #checks if any text is blacklisted
        if any(re.search(message.content.lower()) for re in blackDictionary.keys()):
            await blEvent(message)
            check = False
        elif any(re.search(message.content.lower()) for re in grayDictionary.keys()):
            await client.send_message(message.channel, "graylist")
            # glEvent(message, )
            check = False

    #TODO tts feature
    if check and message.content.startswith('!tts'):
        pass
    #returns blacklist
    if message.content.startswith('!blacklist'):
        await client.send_message(message.author, ''.join(["Blacklisted words for ", message.server.name, " server: ", ', '.join(blackDictionary.values())]))

    #returns graylist
    if message.content.startswith('!graylist'):
        await client.send_message(message.author, ''.join(["Graylisted words for ", message.server.name, " server: ", ', '.join(grayDictionary.values())]))

    #check if admin
    if message.author.server_permissions.administrator:
            #add to blacklist
            if message.content.startswith('!addblacklist'):
                await addToList('blacklist', blackDictionary, message)
            #remove from blacklist
            if message.content.startswith('!rmblacklist'):
                await removeFromList('blacklist', blackDictionary, message)
            #add to graylist
            if message.content.startswith('!addgraylist'):
                await addToList('graylist', grayDictionary, message)
            #remove from graylist
            if message.content.startswith('!rmgraylist'):
                await removeFromList('graylist', grayDictionary, message)
            if message.content.startswith('!setmutedrole'):
                try:
                    global role
                    mutedName = message.content.split(' ', 1)[1]
                    if role is not None:
                        await client.edit_role(message.server, role, name = mutedName)
                        role = get_role(mutedName, message.server.id)
                    else:
                        role = await client.create_role(message.server, name = mutedName, 
                            color = discord.Color.light_grey(), permissions = discord.Permissions.none(), position = 0)
                    with open('mutedchannel.txt', 'w') as f:
                        f.write(message.server.id + " " + mutedName)
                except IndexError:
                    print("No second word")
            if message.content.startswith('!mutedrolename'):
                await client.send_message(message.channel, role)
          
    #help
    if message.content.startswith("!help"):
        await client.send_message(message.author, 
            '''
            Description: You should not be cursing in the channel. Therefore, this bot prevents members from vulgar language
Commands:
    All Members:
        !blacklist
            sends you the list of blacklisted words
    Admin Only:
        !addblacklist
            "!addblacklist 'word'" will add 'word' to the blacklist
        !rmblacklist
            "!addblacklist 'word'" will add 'word' to the blacklist
            ''')


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    check_muted_role()

#create regex list from blacklist and graylist
blackDictionary = {}
with open('blacklist.txt') as f:
    for x in f.read().split():
        add_to_dictionary(blackDictionary, x)
grayDictionary = {}
with open('blacklist.txt') as f:
    for x in f.read().split():
        add_to_dictionary(grayDictionary, x)

client.run(TOKEN)