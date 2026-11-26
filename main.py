import os
import io
import aiohttp
import discord
from PIL import Image
from discord.ext import commands
from discord import app_commands


# =========================================================
# JUZEN BOT - ตั้งค่าหลัก
# =========================================================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# =========================================================
# เมื่อบอทเริ่มทำงาน
# =========================================================

@bot.event
async def on_ready():
    print("=" * 40)
    print(f"Bot Online! : {bot.user}")
    print(f"Bot ID      : {bot.user.id}")
    print("=" * 40)


# =========================================================
# Sync Slash Commands
# =========================================================

@bot.event
async def setup_hook():
    guild = discord.Object(id=1527736556478005248)

    bot.tree.copy_global_to(guild=guild)
    synced = await bot.tree.sync(guild=guild)

    # ทำให้ปุ่มสินค้ายังใช้งานได้หลังบอทรีสตาร์ต
    bot.add_view(ProductView())

    print(f"Synced {len(synced)} slash command(s) to JUZEN STORE")
    print("JUZEN BOT พร้อมใช้งานแล้ว!")


# =========================================================
# เมื่อสมาชิกเข้า Server
# =========================================================

@bot.event
async def on_member_join(member: discord.Member):
    # เปลี่ยนเลขนี้เป็น ID ของห้องต้อนรับของคุณ
    WELCOME_CHANNEL_ID = 1140633489520205934

    channel = bot.get_channel(WELCOME_CHANNEL_ID)

    if channel is not None:
        embed = discord.Embed(
            title="Welcome to the server!",
            description=f"ยินดีต้อนรับ {member.mention} 🎉",
            color=0x66FFFF
        )

        await channel.send(
            f"Welcome to the server, {member.mention}!"
        )
        await channel.send(embed=embed)

    # ส่ง DM หาสมาชิกใหม่
    try:
        await member.send(
            f"Welcome to the server, {member.name}! 🎉"
        )
    except discord.Forbidden:
        # ผู้ใช้อาจปิดรับ DM จาก Server
        pass


# =========================================================
# เมื่อสมาชิกออกจาก Server
# =========================================================

@bot.event
async def on_member_remove(member: discord.Member):
    # เปลี่ยนเลขนี้เป็น ID ของห้องต้อนรับ/แจ้งเตือน
    WELCOME_CHANNEL_ID = 1140633489520205934

    channel = bot.get_channel(WELCOME_CHANNEL_ID)

    if channel is not None:
        await channel.send(
            f"{member.name} has left the server! 👋"
        )


# =========================================================
# ระบบอ่านข้อความ
# =========================================================

@bot.event
async def on_message(message: discord.Message):
    # ไม่ให้บอทตอบตัวเอง
    if message.author.bot:
        return

    mes = message.content.lower().strip()

    if mes == "hello":
        await message.channel.send("Hello It's me")

    elif mes == "hi bot":
        await message.channel.send(
            f"Hello, {message.author.name}"
        )

    # ทำให้คำสั่ง !hello / !test ยังใช้งานได้
    await bot.process_commands(message)


# =========================================================
# คำสั่ง !hello
# =========================================================

@bot.command()
async def hello(ctx: commands.Context):
    await ctx.send(
        f"hello {ctx.author.name}!"
    )


# =========================================================
# คำสั่ง !test
# =========================================================

@bot.command()
async def test(ctx: commands.Context, *, arg: str):
    await ctx.send(arg)


# =========================================================
# Slash Command /hellobot
# =========================================================

@bot.tree.command(
    name="hellobot",
    description="ทดสอบบอท"
)
async def hellocommand(interaction: discord.Interaction):
    await interaction.response.send_message(
        "Hello It's me JUZEN BOT 🤖"
    )


# =========================================================
# Slash Command /name
# =========================================================

@bot.tree.command(
    name="name",
    description="บอกชื่อของคุณ"
)
@app_commands.describe(
    name="What's your name?"
)
async def namecommand(
    interaction: discord.Interaction,
    name: str
):
    await interaction.response.send_message(
        f"Hello {name} 👋"
    )


# =========================================================
# Slash Command /help
# =========================================================

@bot.tree.command(
    name="help",
    description="ดูคำสั่งทั้งหมดของบอท"
)
async def helpcommand(interaction: discord.Interaction):

    embed = discord.Embed(
        title="JUZEN BOT - Commands",
        description="คำสั่งที่สามารถใช้งานได้",
        color=0x66FFFF,
        timestamp=discord.utils.utcnow()
    )

    embed.add_field(
        name="/hellobot",
        value="ทดสอบว่าบอททำงานหรือไม่",
        inline=False
    )

    embed.add_field(
        name="/name",
        value="ให้บอททักชื่อ",
        inline=False
    )

    embed.add_field(
        name="/join",
        value="ให้บอทเข้าห้องเสียงที่คุณอยู่",
        inline=False
    )

    embed.add_field(
        name="/leave",
        value="ให้บอทออกจากห้องเสียง",
        inline=False
    )

    await interaction.response.send_message(embed=embed)


# =========================================================
# Slash Command /join
# ให้บอทเข้าห้องเสียงที่เราอยู่
# =========================================================

@bot.tree.command(
    name="join",
    description="ให้บอทเข้าห้องเสียงที่คุณอยู่"
)
async def joincommand(interaction: discord.Interaction):

    if interaction.guild is None:
        await interaction.response.send_message(
            "❌ คำสั่งนี้ใช้ใน Server เท่านั้น"
        )
        return

    if interaction.user.voice is None:
        await interaction.response.send_message(
            "❌ กรุณาเข้าห้องเสียงก่อน แล้วค่อยใช้ /join"
        )
        return

    channel = interaction.user.voice.channel

    if not isinstance(
        channel,
        (discord.VoiceChannel, discord.StageChannel)
    ):
        await interaction.response.send_message(
            "❌ ไม่สามารถเข้าห้องเสียงประเภทนี้ได้"
        )
        return

    # บอก Discord ก่อนว่าบอทกำลังทำงาน
    await interaction.response.defer()

    voice_client = interaction.guild.voice_client

    try:
        if voice_client is not None:
            await voice_client.move_to(channel)
        else:
            await channel.connect()

        await interaction.followup.send(
            f"✅ JUZEN BOT เข้าห้อง **{channel.name}** แล้ว"
        )

    except discord.Forbidden:
        await interaction.followup.send(
            "❌ บอทไม่มีสิทธิ์ Connect ในห้องเสียงนี้"
        )

    except Exception as e:
        await interaction.followup.send(
            f"❌ ไม่สามารถเข้าห้องเสียงได้\n```{e}```"
        )

# =========================================================
# Slash Command /leave
# ให้บอทออกจากห้องเสียง
# =========================================================

@bot.tree.command(
    name="leave",
    description="ให้บอทออกจากห้องเสียง"
)
async def leavecommand(interaction: discord.Interaction):

    if interaction.guild is None:
        await interaction.response.send_message(
            "❌ คำสั่งนี้ใช้ใน Server เท่านั้น"
        )
        return

    voice_client = interaction.guild.voice_client

    if voice_client is None:
        await interaction.response.send_message(
            "❌ ตอนนี้บอทไม่ได้อยู่ในห้องเสียง"
        )
        return

    await voice_client.disconnect()

    await interaction.response.send_message(
        "👋 JUZEN BOT ออกจากห้องเสียงแล้ว"
    )


# =========================================================
# ระบบสินค้า + ปุ่มสนใจ + Ticket
# =========================================================

TICKET_CATEGORY_NAME = "TICKETS"


class ProductView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🛒 สนใจ",
        style=discord.ButtonStyle.primary,
        custom_id="juzen_product_interest"
    )
    async def interest(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.guild is None:
            await interaction.response.send_message(
                "❌ ปุ่มนี้ใช้ใน Server เท่านั้น",
                ephemeral=True
            )
            return

        existing = discord.utils.find(
            lambda c: c.name.startswith("ticket-")
            and interaction.user in c.overwrites
            and c.permissions_for(interaction.user).view_channel,
            interaction.guild.text_channels
        )

        if existing is not None:
            await interaction.response.send_message(
                f"🛒 คุณมี Ticket อยู่แล้ว: {existing.mention}",
                ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        category = discord.utils.get(guild.categories, name=TICKET_CATEGORY_NAME)

        if category is None:
            category = await guild.create_category(
                TICKET_CATEGORY_NAME,
                reason="สร้างหมวด Ticket สำหรับ JUZEN BOT"
            )

        safe_name = "".join(
            c for c in interaction.user.name.lower()
            if c.isalnum() or c in "-_"
        )[:20] or str(interaction.user.id)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                attach_files=True
            ),
            guild.me: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                manage_channels=True
            )
        }

        try:
            ticket = await guild.create_text_channel(
                name=f"ticket-{safe_name}",
                category=category,
                overwrites=overwrites,
                reason=f"Ticket เปิดโดย {interaction.user}"
            )

            await ticket.send(
                f"👋 สวัสดี {interaction.user.mention}\n\n"
                "🛒 **รับทราบครับ สนใจสินค้านี้ใช่ไหม?**\n"
                "แอดมินจะเข้ามาดูแลใน Ticket นี้ครับ\n\n"
                "กรุณาส่งรายละเอียดที่ต้องการสั่งซื้อได้เลย"
            )

            await interaction.followup.send(
                f"✅ เปิด Ticket ให้แล้วครับ 👉 {ticket.mention}",
                ephemeral=True
            )

        except discord.Forbidden:
            await interaction.followup.send(
                "❌ บอทไม่มีสิทธิ์สร้างห้อง Ticket\n"
                "ให้ JUZEN BOT มีสิทธิ์ **Manage Channels** ก่อนครับ",
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(
                f"❌ เปิด Ticket ไม่สำเร็จ\n```{e}```",
                ephemeral=True
            )


@bot.tree.command(
    name="postproduct",
    description="โพสต์สินค้า พร้อมปุ่มสนใจ"
)
@app_commands.describe(
    title="ชื่อสินค้า เช่น Full Autumn - M416",
    category="หมวดสินค้า เช่น weapon • pubg",
    code="รหัสสินค้า เช่น WP001",
    price="ราคา เช่น 350฿",
    image_url="ลิงก์รูปสินค้า",
    status="สถานะ เช่น EVENT"
)
async def postproductcommand(
    interaction: discord.Interaction,
    title: str,
    category: str,
    code: str,
    price: str,
    image_url: str,
    image_url2: str,
    status: str = "EVENT"
):
    if interaction.guild is None:
        await interaction.response.send_message(
            "❌ คำสั่งนี้ใช้ใน Server เท่านั้น",
            ephemeral=True
        )
        return

    if not interaction.user.guild_permissions.manage_guild:
        await interaction.response.send_message(
            "❌ คำสั่งนี้ใช้ได้เฉพาะผู้ที่มีสิทธิ์ Manage Server",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title=title,
        description=f"{category}\n`{code}`\n\n**ถาวร {price}**",
        color=0x8B5CF6,
        timestamp=discord.utils.utcnow()
    )

    embed.add_field(
        name=f"🟨 {status.upper()}",
        value="",
        inline=False
    )
    embed.set_footer(
        text=f"อัปเดต {discord.utils.utcnow().strftime('%d/%m/%Y')}"
    )

    # ดาวน์โหลดรูปทั้ง 2 รูป แล้วรวมเป็นภาพแนวนอนภาพเดียว
    await interaction.response.defer()

    try:
        timeout = aiohttp.ClientTimeout(total=25)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async def download_image(url):
                async with session.get(url) as response:
                    response.raise_for_status()
                    data = await response.read()
                    if len(data) > 10 * 1024 * 1024:
                        raise ValueError("รูปภาพมีขนาดเกิน 10 MB")
                    return Image.open(io.BytesIO(data)).convert("RGBA")

            image1 = await download_image(image_url)
            image2 = await download_image(image_url2)

        # จัดรูปแต่ละรูปให้อยู่ในกรอบขนาดเท่ากัน โดยไม่บิดสัดส่วน
        cell_width = 600
        cell_height = 600
        gap = 24
        background = (32, 34, 37, 255)

        canvas = Image.new(
            "RGBA",
            (cell_width * 2 + gap, cell_height),
            background
        )

        for index, img in enumerate((image1, image2)):
            img.thumbnail((cell_width, cell_height), Image.Resampling.LANCZOS)
            x = index * (cell_width + gap) + (cell_width - img.width) // 2
            y = (cell_height - img.height) // 2
            canvas.alpha_composite(img, (x, y))

        output = io.BytesIO()
        canvas.convert("RGB").save(output, format="PNG", optimize=True)
        output.seek(0)

        product_file = discord.File(
            output,
            filename="product_images_side_by_side.png"
        )
        embed.set_image(url="attachment://product_images_side_by_side.png")

        await interaction.followup.send(
            embed=embed,
            file=product_file,
            view=ProductView()
        )

    except Exception as e:
        await interaction.followup.send(
            "❌ รวมรูปสินค้าไม่สำเร็จ กรุณาตรวจสอบลิงก์รูปทั้งสองรูป\n"
            f"รายละเอียด: `{e}`",
            ephemeral=True
        )


# =========================================================
# TOKEN
# =========================================================

token = os.getenv("TOKEN")

if not token:
    raise RuntimeError(
        "ไม่พบ TOKEN\n"
        "ให้ตั้งค่า TOKEN ใน Terminal ก่อนรันบอท"
    )


# =========================================================
# เปิดบอท
# =========================================================

bot.run(token)
