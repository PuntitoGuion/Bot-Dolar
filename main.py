import discord
from discord import option
from discord.ext import commands
from requests import get
import asyncio
from locale import setlocale, LC_ALL
from datetime import datetime

usdApi = "https://dolarapi.com/v1/dolares/"
setlocale(LC_ALL, '')
emojis_split = ":fire: :bank: :fire:" #:bank: :fire: :bank: :fire: :bank: :fire: :bank: :fire: :bank: :fire: "
prefix = "!"

# Obtener precio de la api
def dolar(api):
    response = get(api)
    if response.status_code == 200:
        jsonApi = response.json()
        return jsonApi["venta"], jsonApi["compra"]
    
# Obtengo formateado la venta del mensaje que envía el bot
def getSaleForMessage(message:str):
    return int(message.split('\n')[4].split("$")[-1].split('*')[0])

# Instancias del bot
intents = discord.Intents.default()
intents.presences = True
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix=prefix, intents=intents)

#---------------------------------------------------------------------------

# Evento cuando el bot esté listo
@bot.event
async def on_ready():
    print(f'Bot listo como {bot.user.name}')
    await send_message_periodically()

# Enviar mensaje del tipo de cambio solicitado
@bot.slash_command(name = "get")
@option("usd:", description="Tipo de cambio (Oficial, Blue, Bolsa, CCL)")
@option("Cantidad:",description="Calcular conversión", required=False, default='')
async def usd(ctx,usd,amount=''):

    if usd == "ccl".lower(): # Por si el usuario escribe Contadoconliqui
        usd = "Contadoconliqui"
    try:
        dolarSale, dolarBuy = dolar(usdApi + usd.lower())
    except:
        await ctx.respond(f"¡¡Error {ctx.author.mention}!!:exploding_head:\nTipo de cambio disponible:\n> Oficial\n> Blue\n> Bolsa\n> Contadoconliqui",ephemeral=True)
        return
    
    # Si no se ingresa un número, se envía la cotización según el cambio
    if not amount.isnumeric():
        print(f"Mensaje enviado.")
        await ctx.respond(f'\nDolar {usd.capitalize()} {ctx.author.mention}\n> Compra: ${dolarBuy}\n> Venta: {dolarSale}',ephemeral=True)

    else:
        totalArs = dolarSale * float(amount)
        await ctx.respond(f'\n:nerd: {ctx.author.mention} :nerd:\n> ${amount} USD {usd.capitalize()} al valor: ${dolarSale}\n> Pesos: ${totalArs:,.2f}',ephemeral=True)


async def send_message_periodically():
    channel_id = 1141407762337771570  # ID del canal
    interval_minute = 60  # Intervalo de tiempo en segundos entre cada mensaje
    role_id = 1141402700005785712 # ID del rol
    channel = bot.get_channel(channel_id)

    if channel:
        async for message in channel.history(limit=1):
            before_sale = getSaleForMessage(message.content)
    else:
        before_sale = -1

    role = channel.guild.get_role(role_id)

    while True:
        apiBlue = f"{usdApi}blue"
        dolarSale, dolarBuy = dolar(apiBlue)
        dateTime = datetime.now().strftime("%H:%M - %d/%m/%Y")
        if dolarSale != before_sale:
            before_sale=dolarSale
            await channel.send(f"""
:dollar: Actualización {dateTime} :dollar:
{role.mention}

> Compra: **${dolarBuy}**
> Venta: **${dolarSale}**

{emojis_split}

""")

        await asyncio.sleep(interval_minute * 30)

@bot.slash_command(name = "change")
@option("usd:", description="Tipo de cambio (Oficial, Blue, Bolsa, CCL)")
@option("cantidad:", description="Cantidad en pesos")
async def changePesos(ctx,usd,amount:str):

    try:
        dolarSale, dolarBuy = dolar(usdApi + usd.lower())
    except:
        await ctx.respond(f":exploding_head:¡¡Error {ctx.author.mention}!!:exploding_head:\nTipo de cambio disponible:\n> Oficial\n> Blue\n> Bolsa\n> Contadoconliqui",ephemeral=True)
        return

    if amount.isnumeric():
        totalUsd = float(amount) / float(dolarSale)
        if totalUsd % 1 == 0:
            totalUsd = int(totalUsd)
        await ctx.respond(f":money_mouth: {ctx.author.mention} :money_mouth:\n> ${amount} al cambio USD {usd.capitalize()}: ${dolarSale}\n> USD: {totalUsd}",ephemeral=True)

# Conecta el bot usando el token
bot.run('MTE0MTI0OTAwMTU0MzQzNDI0MA.GUAfMK.DCCnP-e6dNSctr4pSJQTH7mPcw9bC5d7f_kxwM')
