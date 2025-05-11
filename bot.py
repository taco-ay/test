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
async def on_member_join(member):
    for channel in member.guild.text_channels:
        if channel.permissions_for(member.guild.me).send_messages:
            await channel.send(f"Sunucumuza Hoş geldiniz, {member.mention}!")
            break

# Uyarıları tutmak için bir sözlük (bellekte tutulur)
warnings = {}

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Link içerip içermediğini kontrol et
    if "http://" in message.content.lower() or "https://" in message.content.lower():
        if message.author.guild_permissions.administrator:
            return  # Adminleri es geç

        user_id = str(message.author.id)
        if user_id not in warnings:
            warnings[user_id] = 1
            await message.channel.send(f"{message.author.mention}, bağlantı göndermek yasaktır! Bu ilk uyarınız.")
        else:
            warnings[user_id] += 1
            if warnings[user_id] >= 2:
                await message.channel.send(f"{message.author.mention}, tekrar bağlantı gönderdiğiniz için banlandınız.")
                await message.guild.ban(message.author, reason="İzinsiz link paylaşımı (2. uyarıdan sonra)")
            else:
                await message.channel.send(f"{message.author.mention}, bu ikinci uyarınız. Lütfen tekrar etmeyin!")

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
