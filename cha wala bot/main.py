import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import random
import string
import asyncio

# -------------------- Configuration --------------------
TOKEN = 'MTM0MTA0OTIxMzQ4Nzk0MzczMQ.Gsgmfe.Wpxl-aBTBr2h5sTDzau7MB2C-wrOgsLciN_TTc'

USER_DATA_FILE = "user_data.json"

# -------------------- Data Persistence --------------------

def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_user_data(user_data):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(user_data, f, indent=4)

def initialize_user_data(user_id):
    return {
        "notes": {str(denom): 0 for denom in [5, 10, 20, 50, 100, 200, 500, 1000]},
        "message_count": 0,
        "chat_enabled": False,
        "orders": [],
        "glory": 0
    }

def break_notes(amount):
    """Break an amount into note denominations."""
    notes = {5: 0, 10: 0, 20: 0, 50: 0, 100: 0, 200: 0, 500: 0, 1000: 0}
    for note in sorted(notes.keys(), reverse=True):
        if amount >= note:
            notes[note] = amount // note
            amount %= note
    return notes

# -------------------- Item Image Mapping --------------------

ITEM_IMAGES = {
    "দুধ চা🍵": "https://thumbs.dreamstime.com/b/tea-tumpler-quaint-roadside-shop-south-india-traditional-tumbler-brimming-aromatic-sending-wisps-fragrant-steam-296260241.jpg",
    "রং চা◼️🍵": "https://theprestige.global/wp-content/uploads/2021/06/LG_NLKMWY.jpg",
    "কফি☕️": "https://insanelygoodrecipes.com/wp-content/uploads/2020/07/Cup-Of-Creamy-Coffee.png",
    "মালাই চা🥛🍵": "https://foodandroad.com/wp-content/uploads/2021/04/masala-chai-indian-drink-3-500x375.jpg",
    "বুলেট চা🅱️🍵": "https://i.ytimg.com/vi/lVNQWiipy4k/hq720.jpg?sqp=-oaymwEhCK4FEIIDSFryq4qpAxMIARUAAAAAGAElAADIQj0AgKJD&rs=AOn4CLAwOnXLlapKtn-zPWt2gDfTz3zwyQ",
    "প্রিমিয়াম কফি☕️": "https://www.allrecipes.com/thmb/Hqro0FNdnDEwDjrEoxhMfKdWfOY=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/21667-easy-iced-coffee-ddmfs-4x3-0093-7becf3932bd64ed7b594d46c02d0889f.jpg",
    "শিঙ্গারা 1plate": "https://www.vegrecipesofindia.com/wp-content/uploads/2017/12/singara-recipe.jpg",
    "সোমোচা 1plate": "https://i.ytimg.com/vi/hivpp8jbEjk/hqdefault.jpg",
    "মিষ্টি 1plate": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR1JbcUPewJ7aulSzSYWYwaO6xxDOaiW4F0Hg&s",
    "বিস্কিট": "https://i0.wp.com/thegastronomicbong.com/wp-content/uploads/2020/05/Cake-Rusk-recipe-scaled.jpg?fit=800%2C1200&ssl=1&resize=350%2C200",
    "রুটি": "https://www.nithaskitchen.com/wp-content/uploads/2015/04/Burger_Buns_L.jpg"
}

# -------------------- Bot Initialization --------------------

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Emojis for note display
NOTE_EMOJIS = {
    5: "<:5taka:1341258955913166978>",
    10: "<:10taka:1341054570045898843>",
    20: "<:20taka:1341053817265066046>",
    50: "<:50taka:1341053847032037426>",
    100: "<:100taka:1341053886068162603>",
    200: "<:200taka:1341053912458854573>",
    500: "<:500taka:1341053941026394193>",
    1000: "<:1000taka:1341053963038101605>"
}

# Menu for tea and food
MENU = {
    "Tea": {
        "দুধ চা🍵": 15,
        "রং চা◼️🍵": 10,
        "কফি☕️": 30,
        "মালাই চা🥛🍵": 20,
        "বুলেট চা🅱️🍵": 20,
        "প্রিমিয়াম কফি☕️": 50
    },
    "Foods": {
        "শিঙ্গারা 1plate": 20,
        "সোমোচা 1plate": 20,
        "মিষ্টি 1plate": 25,
        "বিস্কিট": 5,
        "রুটি": 10
    }
}

# -------------------- Global Glory System --------------------
# Every command (slash or prefix) adds 1 glory to the user silently.

@bot.event
async def on_interaction(interaction: discord.Interaction):
    # This event fires for all interactions.
    if interaction.type == discord.InteractionType.application_command:
        user_id = str(interaction.user.id)
        data = load_user_data()
        if user_id not in data:
            data[user_id] = initialize_user_data(user_id)
        data[user_id]["glory"] = data[user_id].get("glory", 0) + 1
        save_user_data(data)

@bot.event
async def on_command(ctx):
    user_id = str(ctx.author.id)
    data = load_user_data()
    if user_id not in data:
        data[user_id] = initialize_user_data(user_id)
    data[user_id]["glory"] = data[user_id].get("glory", 0) + 1
    save_user_data(data)

# -------------------- Bot Commands --------------------

# /bank command - Check your balance.
@bot.tree.command(name="bank", description="Check your balance.")
async def bank(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    user_data = load_user_data()
    if user_id not in user_data:
        user_data[user_id] = initialize_user_data(user_id)
    notes = {int(denom): count for denom, count in user_data[user_id]["notes"].items()}
    total = sum(note * count for note, count in notes.items())
    description = "\n".join(
        [f"{NOTE_EMOJIS.get(note, '')} `{note} টাকা` :- {count} notes" for note, count in sorted(notes.items()) if count > 0]
    )
    if description:
        description += f"\n**মোট** :- **{total} টাকা**"
    else:
        description = "কোনো টাকা নেই!"
    embed = discord.Embed(
        title="আপনার ব্যালেন্স",
        description=description,
        color=discord.Color.green()
    )
    embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/%E0%A6%AC%E0%A6%BE%E0%A6%82%E0%A6%B2%E0%A6%BE%E0%A6%A6%E0%A7%87%E0%A6%B6%E0%A7%80_%E0%A6%AA%E0%A6%AF%E0%A6%BC%E0%A6%B8%E0%A6%BE_-_Bangladeshi_Coin_Front_Part.png/779px-%E0%A6%AC%E0%A6%BE%E0%A6%82%E0%A6%B2%E0%A6%BE%E0%A6%A6%E0%A7%87%E0%A6%B6%E0%A7%80_%E0%A6%AA%E0%A6%AF%E0%A6%BC%E0%A6%B8%E0%A6%BE_-_Bangladeshi_Coin_Front_Part.png")
    embed.set_image(url="https://static.wikia.nocookie.net/motu-patlu/images/e/e3/Screenshot_2020-08-11_at_5.05.51_PM.png")
    await interaction.response.send_message(embed=embed)

# /price command - View the menu.
@bot.tree.command(name="price", description="View the menu.")
async def price(interaction: discord.Interaction):
    description = "**Tea**\n" + "\n".join([f"{item} ---------- {price}tk" for item, price in MENU["Tea"].items()])
    description += "\n\n**Foods**\n" + "\n".join([f"{item} ----- {price}tk" for item, price in MENU["Foods"].items()])
    embed = discord.Embed(
        title="Menu",
        description=description,
        color=discord.Color.blue()
    )
    embed.set_image(url="https://media.discordapp.net/attachments/1258118329298583573/1341265539711893597/Khaki_and_White_Modern_Coffe_Menu.png")
    await interaction.response.send_message(embed=embed)

# -------------------- Order and Payment Commands --------------------
class PaymentView(discord.ui.View):
    def __init__(self, user_id, total_cost, order_items):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.total_cost = total_cost
        self.order_items = order_items

    @discord.ui.button(label="Pay Now", style=discord.ButtonStyle.green, custom_id="pay_now")
    async def pay_now(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("এই অর্ডারটি আপনার নয়!", ephemeral=True)
            return

        user_data = load_user_data()
        user = user_data.get(self.user_id, initialize_user_data(self.user_id))
        notes = {int(denom): count for denom, count in user["notes"].items()}
        total_money = sum(note * count for note, count in notes.items())
        if total_money < self.total_cost:
            await interaction.response.send_message(f"পর্যাপ্ত টাকা নেই! আপনার আছে: {total_money} টাকা", ephemeral=True)
            return

        remaining = total_money - self.total_cost
        new_notes = break_notes(remaining)
        user["notes"] = {str(k): v for k, v in new_notes.items()}
        for item in self.order_items:
            if item in user["orders"]:
                user["orders"].remove(item)
        user_data[self.user_id] = user
        save_user_data(user_data)

        ordered_items_str = ", ".join(self.order_items)
        desc = f"আপনার অর্ডার: {ordered_items_str}\nমোট বিল: {self.total_cost} টাকা"
        image_links = "\n".join(f"[{item}]({ITEM_IMAGES[item]})" for item in self.order_items if item in ITEM_IMAGES)
        embed = discord.Embed(title="বিল পরিশোধের জন্য ধন্যবাদ", description=desc, color=discord.Color.green())
        if image_links:
            embed.add_field(name="ছবিসমূহ", value=image_links, inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        self.stop()

    @discord.ui.button(label="Pay Later", style=discord.ButtonStyle.red, custom_id="pay_later")
    async def pay_later(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("এই অর্ডারটি আপনার নয়!", ephemeral=True)
            return

        ordered_items_str = ", ".join(self.order_items)
        desc = f"আপনার অর্ডার: {ordered_items_str}\nমোট বিল: {self.total_cost} টাকা"
        image_links = "\n".join(f"[{item}]({ITEM_IMAGES[item]})" for item in self.order_items if item in ITEM_IMAGES)
        embed = discord.Embed(title="পরে বিল দিন সমস্যা নেই", description=desc, color=discord.Color.red())
        if image_links:
            embed.add_field(name="ছবিসমূহ", value=image_links, inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        self.stop()

class OrderView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.selected_items = []

    @discord.ui.select(
        placeholder="Select items to order",
        min_values=1,
        max_values=len(MENU["Tea"]) + len(MENU["Foods"]),
        options=[
            discord.SelectOption(label=item, description=f"{price} tk")
            for category in MENU.values() for item, price in category.items()
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.selected_items = select.values
        await interaction.response.defer()

    @discord.ui.button(label="Confirm Order", style=discord.ButtonStyle.green)
    async def confirm_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.selected_items:
            await interaction.response.send_message("কোনো আইটেম নির্বাচন করা হয়নি!", ephemeral=True)
            return
        total_cost = 0
        for item in self.selected_items:
            for category in MENU.values():
                if item in category:
                    total_cost += category[item]
        user_data = load_user_data()
        uid = self.user_id
        if uid not in user_data:
            user_data[uid] = initialize_user_data(uid)
        user_data[uid]["orders"].extend(self.selected_items)
        save_user_data(user_data)

        embed = discord.Embed(
            title="অর্ডার কনফার্মেশন",
            description=f"আপনার অর্ডার: {', '.join(self.selected_items)}\n**মোট বিল**: {total_cost} টাকা",
            color=discord.Color.orange()
        )
        embed.set_image(url="https://i.makeagif.com/media/5-04-2017/cnvtI1.gif")
        payment_view = PaymentView(user_id=self.user_id, total_cost=total_cost, order_items=self.selected_items)
        await interaction.response.send_message(embed=embed, view=payment_view)

@bot.tree.command(name="order", description="Place an order.")
async def order(interaction: discord.Interaction):
    view = OrderView(user_id=str(interaction.user.id))
    await interaction.response.send_message("দয়া করে অর্ডারের আইটেম নির্বাচন করুন:", view=view)

@bot.tree.command(name="pay", description="Pay your bill for pending orders.")
async def pay(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    user_data = load_user_data()
    if user_id not in user_data:
        user_data[user_id] = initialize_user_data(user_id)
    orders = user_data[user_id]["orders"]
    if not orders:
        await interaction.response.send_message("কোনো পেন্ডিং অর্ডার নেই।")
        return
    total_cost = 0
    for item in orders:
        for category in MENU.values():
            if item in category:
                total_cost += category[item]
    notes = {int(denom): count for denom, count in user_data[user_id]["notes"].items()}
    total_money = sum(note * count for note, count in notes.items())
    if total_money < total_cost:
        embed = discord.Embed(
            title="টাকার সমস্যা!",
            description=f"মোট বিল: {total_cost} টাকা, আপনার আছে: {total_money} টাকা।",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)
    else:
        remaining = total_money - total_cost
        new_notes = break_notes(remaining)
        user_data[user_id]["notes"] = {str(k): v for k, v in new_notes.items()}
        user_data[user_id]["orders"] = []
        save_user_data(user_data)
        embed = discord.Embed(
            title="বিল পরিশোধ হয়েছে",
            description=f"{total_cost} টাকা পরিশোধ করা হয়েছে।",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="give", description="Give money to another user.")
@app_commands.describe(user="The user to give money to.", amount="The amount to give.")
async def give(interaction: discord.Interaction, user: discord.Member, amount: int):
    giver_id = str(interaction.user.id)
    receiver_id = str(user.id)
    user_data = load_user_data()
    if giver_id not in user_data:
        user_data[giver_id] = initialize_user_data(giver_id)
    if receiver_id not in user_data:
        user_data[receiver_id] = initialize_user_data(receiver_id)
    giver_notes = {int(denom): count for denom, count in user_data[giver_id]["notes"].items()}
    total_money = sum(note * count for note, count in giver_notes.items())
    if total_money < amount:
        await interaction.response.send_message("পর্যাপ্ত টাকা নেই!", ephemeral=True)
        return
    remaining = total_money - amount
    user_data[giver_id]["notes"] = {str(k): v for k, v in break_notes(remaining).items()}
    receiver_total = sum(int(denom)*count for denom, count in user_data[receiver_id]["notes"].items())
    new_total = receiver_total + amount
    user_data[receiver_id]["notes"] = {str(k): v for k, v in break_notes(new_total).items()}
    save_user_data(user_data)
    await interaction.response.send_message(f"{user.mention} কে {amount} টাকা প্রদান করা হয়েছে।")

@bot.tree.command(name="note_convert", description="Convert your notes into smaller denominations.")
@app_commands.describe(note_value="The note value you want to convert.", target_value="The smaller denomination you desire.")
async def note_convert(interaction: discord.Interaction, note_value: int, target_value: int):
    user_id = str(interaction.user.id)
    user_data = load_user_data()
    if user_id not in user_data:
        user_data[user_id] = initialize_user_data(user_id)
    notes = {int(denom): count for denom, count in user_data[user_id]["notes"].items()}
    if note_value not in notes or notes[note_value] <= 0:
        await interaction.response.send_message(f"{note_value} টাকা নোট আপনার কাছে নেই!", ephemeral=True)
        return
    if target_value >= note_value:
        await interaction.response.send_message("লক্ষ্য মানটি মূল নোটের চেয়ে ছোট হতে হবে!", ephemeral=True)
        return
    notes[note_value] -= 1
    conversion_count = note_value // target_value
    notes[target_value] = notes.get(target_value, 0) + conversion_count
    user_data[user_id]["notes"] = {str(k): v for k, v in notes.items()}
    save_user_data(user_data)
    await interaction.response.send_message(f"1 টি {note_value} টাকা নোট পরিবর্তন করে {conversion_count} টি {target_value} টাকা নোট তৈরি করা হয়েছে।")

@bot.tree.command(name="active_chat", description="Enable earning money by chatting. Every 5 messages earn you 20 টাকা.")
async def active_chat(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    user_data = load_user_data()
    if user_id not in user_data:
        user_data[user_id] = initialize_user_data(user_id)
    user_data[user_id]["message_count"] = 0
    user_data[user_id]["chat_enabled"] = True
    save_user_data(user_data)
    await interaction.response.send_message("এখন আপনি চ্যাটের মাধ্যমে টাকা উপার্জন করতে পারবেন! প্রতি ৫টি মেসেজে ২০ টাকা।")

# -------------------- Chat Earning --------------------

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    user_id = str(message.author.id)
    user_data = load_user_data()
    if user_id not in user_data:
        user_data[user_id] = initialize_user_data(user_id)
    if user_data[user_id].get("chat_enabled", False):
        user_data[user_id]["message_count"] += 1
        if user_data[user_id]["message_count"] >= 5:
            current_total = sum(int(denom)*count for denom, count in user_data[user_id]["notes"].items())
            new_total = current_total + 20
            user_data[user_id]["notes"] = {str(k): v for k, v in break_notes(new_total).items()}
            user_data[user_id]["message_count"] = 0
            save_user_data(user_data)
            try:
                await message.channel.send(f"{message.author.mention}, আপনি ২০ টাকা উপার্জন করেছেন!")
            except discord.Forbidden:
                pass
        else:
            save_user_data(user_data)
    await bot.process_commands(message)

# -------------------- Glory and Redemption --------------------
# /glory command to view current glory count.
@bot.tree.command(name="glory", description="View your current glory count.")
async def glory(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    data = load_user_data()
    if user_id not in data:
        data[user_id] = initialize_user_data(user_id)
    count = data[user_id].get("glory", 0)
    await interaction.response.send_message(f"Your glory: {count} <a:glory:1342114099340906597>", ephemeral=True)

# Helper function to generate a random 6-character alphanumeric token.
def generate_token():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# /redeem command for spending glory.
@bot.tree.command(name="redeem", description="Redeem your glory for rewards.")
@app_commands.choices(item=[
    app_commands.Choice(name="Custom Role (200 glory)", value="custom_role"),
    app_commands.Choice(name="Nitro Basic 1m (500 glory)", value="nitro_basic"),
    app_commands.Choice(name="Nitro Premium 1m (1000 glory)", value="nitro_premium_1m"),
    app_commands.Choice(name="Nitro Premium 3m (10000 glory)", value="nitro_premium_3m")
])
async def redeem(interaction: discord.Interaction, item: app_commands.Choice[str]):
    valid_items = {
        "custom_role": {"cost": 200, "token_type": "role", "emoji": "<a:role:1341055922637897761>"},
        "nitro_basic": {"cost": 500, "token_type": "nitrobasic", "emoji": "<:Nitrobasic:1341055843357032469>"},
        "nitro_premium_1m": {"cost": 1000, "token_type": "nitro1m", "emoji": "<a:nitro:1341055861493338215>"},
        "nitro_premium_3m": {"cost": 10000, "token_type": "nitro3m", "emoji": "<a:nitro:1341055861493338215>"}
    }
    option = valid_items[item.value]
    user_id = str(interaction.user.id)
    data = load_user_data()
    if user_id not in data:
        data[user_id] = initialize_user_data(user_id)
    user_glory = data[user_id].get("glory", 0)
    if user_glory < option["cost"]:
        await interaction.response.send_message(f"Not enough glory. You have {user_glory} glory.", ephemeral=True)
        return
    data[user_id]["glory"] = user_glory - option["cost"]
    save_user_data(data)
    token = generate_token()
    bot_avatar = interaction.client.user.display_avatar.url
    bot_banner = "https://example.com/banner.png"  # Replace with your bot banner URL
    dm_embed = discord.Embed(
        title=f"You bought {item.name}",
        description=f"You have redeemed {option['emoji']} for {option['cost']} glory.\nReceived token: `{token}`\nPlease DM `a_man_of_flex_ | 1339278090408431728` your token.\nExpires in 5 days.",
        color=discord.Color.blue()
    )
    dm_embed.set_thumbnail(url=bot_avatar)
    dm_embed.set_image(url=bot_banner)
    try:
        await interaction.user.send(embed=dm_embed)
    except discord.Forbidden:
        await interaction.response.send_message("Could not send you a DM. Please enable DMs from server members.", ephemeral=True)
        return
    owner_id = 1339278090408431728
    owner = interaction.client.get_user(owner_id)
    if owner:
        owner_embed = discord.Embed(
            title="Redemption Alert",
            description=f"{interaction.user.mention} has redeemed {item.name}.\nToken: `{token}`",
            color=discord.Color.gold()
        )
        try:
            await owner.send(embed=owner_embed)
        except discord.Forbidden:
            pass
    await interaction.response.send_message("Redemption successful! Check your DMs.", ephemeral=True)

# -------------------- Custom Say Command --------------------
@bot.tree.command(name="say", description="Send a custom message with an embed.")
@app_commands.describe(
    outer_text="Text to send outside the embed.",
    title="Embed title.",
    description="Embed description.",
    image="(Optional) URL for the embed image.",
    thumbnail="(Optional) URL for the embed thumbnail.",
    footer_image="(Optional) URL for the footer image.",
    footer_text="(Optional) Footer text.",
    side_line_color="(Optional) Hex color code for the embed border (e.g., #FF5733)."
)
async def say(interaction: discord.Interaction, outer_text: str, title: str, description: str, image: str = None, thumbnail: str = None, footer_image: str = None, footer_text: str = None, side_line_color: str = None):
    color = discord.Color.default()
    if side_line_color:
        try:
            hex_value = side_line_color.lstrip("#")
            color = discord.Color(int(hex_value, 16))
        except ValueError:
            pass
    embed = discord.Embed(title=title, description=description, color=color)
    if image:
        embed.set_image(url=image)
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    if footer_text or footer_image:
        embed.set_footer(text=footer_text if footer_text else "", icon_url=footer_image if footer_image else None)
    await interaction.response.send_message(content=outer_text, embed=embed)

# -------------------- Additional Command: MoneyUpFree --------------------
@bot.command(name="moneyupfree")
async def moneyupfree(ctx):
    user_id = str(ctx.author.id)
    user_data = load_user_data()
    if user_id not in user_data:
        user_data[user_id] = initialize_user_data(user_id)
    for note in user_data[user_id]["notes"]:
        user_data[user_id]["notes"][note] = 100
    save_user_data(user_data)
    await ctx.send("আপনার সকল নোট ১০০ করে সেট করা হয়েছে।")

# -------------------- on_ready Event --------------------
@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(f"Error syncing commands: {e}")

# -------------------- Run Bot --------------------
bot.run(TOKEN)
