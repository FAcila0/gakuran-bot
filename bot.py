from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot aktif ve çalışıyor!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

import discord
from discord.ext import commands
from discord import ui

# Botun Intents (Yetkileri) ayarları
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 1. Adım: Formu dolduracak pencere (Modal)
class GakuranKayitFormu(ui.Modal, title="Gakuran Kayıt Sistemi"):
    oyun_adi = ui.TextInput(
        label="Gakuran Oyun İçi Adın (Nick)",
        placeholder="Örn: GakuranPlayer",
        required=True,
        max_length=50
    )

    async def on_submit(self, interaction: discord.Interaction):
        VERilecek_rol_id = 1547548487506337792  # Üye Rolü ID
        ALINACAK_rol_id = 1547547130661441606   # Kayıtsız Rolü ID

        guild = interaction.guild
        member = interaction.user
        yeni_nick = self.oyun_adi.value

        try:
            # Kullanıcının Discord ismini oyun içi adı yap
            await member.edit(nick=yeni_nick)

            # Rolleri ayarla
            uye_rolu = guild.get_role(VERilecek_rol_id)
            kayitsiz_rolu = guild.get_role(ALINACAK_rol_id)

            if uye_rolu:
                await member.add_roles(uye_rolu)
            if kayitsiz_rolu:
                await member.remove_roles(kayitsiz_rolu)

            await interaction.response.send_message(
                f"Kayıt başarılı! Oyun içi adın **{yeni_nick}** olarak güncellendi.", 
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"Bir hata oluştu (Botun rolü yetersiz olabilir veya rol sıralaması yanlış): {e}", 
                ephemeral=True
            )

# 2. Adım: Butonun bulunduğu görünüm
class KayitButonu(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Kayıt Ol", style=discord.ButtonStyle.green, custom_id="gakuran_kayit_buton")
    async def kayit_ol_buton(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(GakuranKayitFormu())

# 3. Adım: Bot açıldığında çalışacak kısım
@bot.event
async def on_ready():
    print(f'{bot.user} olarak giriş yapıldı!')

    # Botun durumunu /yardım - /pro şeklinde ayarlar
    aktivite = discord.CustomActivity(name="TWINS DEMONS🎭")
    await bot.change_presence(activity=aktivite)
    
    bot.add_view(KayitButonu())

# 4. Adım: Yeni gelenlere otomatik "Kayıtsız" rolü verme (Otorol)
@bot.event
async def on_member_join(member):
    OTO_ROL_ID = 1547547130661441606  # Kayıtsız Rolü ID'si
    rol = member.guild.get_role(OTO_ROL_ID)
    if rol:
        try:
            await member.add_roles(rol)
            print(f"{member.name} sunucuya katıldı ve otomatik olarak Kayıtsız rolü verildi.")
        except Exception as e:
            print(f"Oto rol verilirken hata oluştu: {e}")

# Butonu kanala gönderecek komut
@bot.command()
async def kayitkur(ctx):
    await ctx.send("Gakuran sunucusuna kayıt olmak için aşağıdaki butona tıklayabilirsin!", view=KayitButonu())

import os

# Web sunucusunu başlat (Render'ın port hatasını önlemek için)
keep_alive()

# Botu Çalıştır (Token'ı çevre değişkeninden alır)
bot.run(os.getenv("DISCORD_TOKEN"))