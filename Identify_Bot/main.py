import discord
from config import TOKEN
import json
from discord import app_commands
from discord.ext import commands

activity = discord.Activity(type=discord.ActivityType.competing, name="/identify")
bot = commands.Bot(command_prefix = "!", activity=activity, status=discord.Status.online, intents = discord.Intents.all())

def check_id(data, student_id, batch):
    fullname = "ไม่มีชื่ออยู่ในระบบ"
    found = False
    for item in data:
        if item["id"] == student_id:
            fullname = item["name"]
            found = True
            break
    if not found:
        batch = "ระบุปีการศึกษาให้ถูกต้อง"
    return fullname, found, batch

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

class verify(discord.ui.View):
    def __init__(self, batch: str):
        super().__init__()
        self.batch = batch

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        print(self.batch)
        role = discord.utils.get(interaction.guild.roles, name=f"CPE {self.batch}")
        await interaction.user.add_roles(role)
        await interaction.response.send_message("✅ ข้อมูลได้รับการยืนยันเรียบร้อย! ✅", ephemeral=True)
        
    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("❌ ข้อมูลผิดพลาด! โปรดลองใหม่อีกครั้ง ❌", ephemeral=True)

@bot.tree.command(name = "identify")
@app_commands.describe(batch = "คุณอยู่ปีการศึกษาอะไร?")
@app_commands.choices(batch = [
    discord.app_commands.Choice(name = "65", value = 1),
    discord.app_commands.Choice(name = "66", value = 2)
])
@app_commands.describe(student_id = "รหัสนักศึกษาของคุณคืออะไร?")
async def identify(interaction: discord.Interaction, batch: discord.app_commands.Choice[int], student_id: str):
    if str(interaction.channel_id) == "YOUR_CHANNEL_ID":
        embed = discord.Embed(title="**IDENTITY CONFIRMATION**", color=discord.Color.blue())
        found = False
        years = "25"
        with open('Y65.json', encoding="utf8") as file:
            data = json.load(file)
            fullname, found, batch = check_id(data, student_id, batch.name)
        if found:
            r_batch = "65"
        elif not found:
            r_batch = "66"
            with open('Y66.json', encoding="utf8") as file:
                data2 = json.load(file)
                fullname, found, r_batch = check_id(data2, student_id, r_batch)
        if not found:
            years = ""
        embed.add_field(name = "ชื่อ - นามสกุล : " + fullname, value="", inline=True)
        embed.add_field(name = "รหัสนักศึกษา : " + student_id, value="", inline=False)
        #embed.add_field(name = "ชื่อเล่น : ")
        embed.add_field(name = "ปีการศึกษา : " + years + r_batch , value="", inline=False)
        if (str(interaction.user.discriminator) == "0" or str(interaction.user.name) == "None"):
            embed.add_field(name = f"Discord ID : {interaction.user.name}", value="".join(interaction.user.mention), inline=True)
        else:
            embed.add_field(name = f"Discord ID : {interaction.user.display_name}#{interaction.user.discriminator}", value="".join(interaction.user.mention), inline=True)
        embed.set_thumbnail(url=interaction.user.avatar.url)
        embed.set_footer(text="Powered By L3ooK")
        if years == "":
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed, view=verify(str(r_batch)), ephemeral=True)
    else:
        await interaction.response.send_message("ไม่สามารถใช้คำสั่งในห้องนี้ได้!", ephemeral=True)

bot.run(TOKEN)