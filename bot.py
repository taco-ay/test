import discord
from discord.ext import commands
from config import token

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Giriş yapıldı: {bot.user.name}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if "https://" in message.content or "http://" in message.content:
        try:
            await message.guild.ban(message.author, reason="Reklam içerikli mesaj")
            print(f"{message.author} kullanıcısı link nedeniyle banlandı.")
        except discord.errors.Forbidden:
            await message.channel.send("Bu kullanıcıyı banlamak için yeterli yetkim yok.")
        except Exception as e:
            await message.channel.send("Bir hata oluştu: " + str(e))
        return  # Komutları işlemeye gerek yok

    await bot.process_commands(message)

@bot.command()
async def start(ctx):
    await ctx.send("Merhaba! Ben bir sohbet yöneticisi botuyum!")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member = None):
    if member:
        if ctx.author.top_role <= member.top_role:
            await ctx.send("Eşit veya daha yüksek rütbeli bir kullanıcıyı yasaklamak mümkün değildir!")
        else:
            await ctx.guild.ban(member)
            await ctx.send(f"Kullanıcı {member.name} banlandı.")
    else:
        await ctx.send("Bu komut banlamak istediğiniz kullanıcıyı işaret etmelidir. Örneğin: `!ban @user`")

@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Bu komutu çalıştırmak için yeterli izniniz yok.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Kullanıcı bulunamadı. Lütfen geçerli bir kullanıcı etiketleyin. Örn: `!ban @kullanıcı`")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Lütfen banlamak istediğiniz kullanıcıyı belirtin. Örn: `!ban @kullanıcı`")
    else:
        await ctx.send("Bilinmeyen bir hata oluştu.")
        raise error  # Hatanın detaylarını log'a yollamak istersen
bot.run(token)
