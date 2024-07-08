import os
import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import random
import requests
from io import BytesIO
from flask import Flask
from threading import Thread
from dotenv import load_dotenv   # Import the load_dotenv function

# Load environment variables from .env file
load_dotenv()

# Bot setup
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True  # Enable the members intent
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Load the base image path (adjust as needed)
base_image_path = "Manga.jpg"

# Flask app for Uptime Robot
app = Flask('')

@app.route('/')
def home():
    return "Hello. I am alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_member_join(member):
    print(f"Creating welcome image for {member.name}")

    try:
        # Load base image
        base_image = Image.open(base_image_path)
        print(f"Opened base image from {base_image_path}")
    except FileNotFoundError:
        print(f"File not found: {base_image_path}")
        return

    draw = ImageDraw.Draw(base_image)

    # Customize the welcome image
    welcome_text = "WELCOME"
    member_text = f"{member.name}"
    bounty_amount = random.randint(0, 1000000)
    bounty_text = f"{bounty_amount:,} -"

    # Load font file (adjust path as needed)
    font_path = "Century Old Style Std Bold.ttf"

    try:
        font_large = ImageFont.truetype(font_path, 110)
        font_medium = ImageFont.truetype(font_path, 70)
        font_avg = ImageFont.truetype(font_path, 90)
        print(f"Loaded fonts from {font_path}")
    except OSError:
        print(f"Font not found: {font_path}")
        return

    # Draw text on the image with appropriate positions
    draw.text((75, 60), welcome_text, font=font_large, fill="black")
    draw.text((180, 725), member_text, font=font_avg, fill="black")
    draw.text((110, 920), bounty_text, font=font_medium, fill="black")

    # Get the member's avatar URL and fetch profile image
    if member.avatar:
        try:
            response = requests.get(member.avatar.url)
            profile_image = Image.open(BytesIO(response.content))
            print("Fetched and opened profile image")
        except Exception as e:
            print(f"Error fetching profile image: {e}")
            profile_image = None
    else:
        profile_image = None

    # Process and paste profile image if available
    if profile_image:
        profile_image = profile_image.resize((600, 468))  # Resize if needed
        profile_image = profile_image.convert("L")  # Convert to grayscale

        # Paste profile image onto the welcome image
        base_image.paste(profile_image, (62, 213))  # Adjust coordinates as needed
        print("Pasted profile image onto base image")

    # Ensure output directory exists
    output_directory = "output"  # Use a directory within the project
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        print(f"Created directory {output_directory}")

    # Save the welcome image
    welcome_image_path = f"{output_directory}/welcome_{member.id}.jpg"
    base_image.save(welcome_image_path)
    print(f"Saved welcome image to {welcome_image_path}")

    # Send the image in the welcome channel with mention
    channel = discord.utils.get(member.guild.text_channels, name='welcome')
    if channel:
        await channel.send(content=f"Welcome to the server, {member.mention}!", file=discord.File(welcome_image_path))
        print(f"Sent welcome image in {channel.name} channel")

# Commands
@bot.command()
async def ping(ctx):
    print("Ping command received")
    await ctx.send('Pong!')

@bot.command()
async def info(ctx):
    print("Info command received")
    guild = ctx.guild
    embed = discord.Embed(title=f"Information for {guild.name}", description=f"Server ID: {guild.id}", color=discord.Color.blue())
    embed.add_field(name="Owner", value=guild.owner)
    # embed.add_field(name="Region", value=guild.preferred_locale)  # Use guild.preferred_locale if needed
    embed.add_field(name="Member Count", value=guild.member_count)
    embed.set_thumbnail(url=guild.icon.url)
    await ctx.send(embed=embed)


@bot.command()
async def userinfo(ctx, member: discord.Member):
    print(f"Userinfo command received for {member.name}")
    embed = discord.Embed(title=f"Information for {member.name}", description=f"User ID: {member.id}", color=discord.Color.green())
    embed.add_field(name="Joined at", value=member.joined_at)
    embed.add_field(name="Roles", value=",".join([role.name for role in member.roles if role.name != "@everyone"]))
    embed.set_thumbnail(url=member.avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def roll(ctx, number: int):
    print(f"Roll command received with number {number}")
    roll = random.randint(1, number)
    await ctx.send(f'🎲 You rolled a {roll}!')

@bot.command()
async def meme(ctx):
    print("Meme command received")
    subreddit = "memes"  # Adjust the subreddit name if needed
    url = f"https://www.reddit.com/r/{subreddit}/random/.json"
    headers = {'User-agent': 'your bot 0.1'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        json_data = response.json()
        post = json_data[0]['data']['children'][0]['data']
        title = post['title']
        image = post['url']
        embed = discord.Embed(title=title)
        embed.set_image(url=image)
        await ctx.send(embed=embed)
    else:
        await ctx.send("Couldn't fetch a meme at the moment.")

# Run the bot using the environment variable
bot.run(os.getenv('DISCORD_BOT_TOKEN'))
