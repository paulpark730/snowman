import nextcord
from nextcord.ext import commands
import asyncio, youtube_dl
import yt_dlp as youtube_dl
import requests
from datetime import datetime, timedelta



TOKEN = "my token"

bot = commands.Bot(command_prefix=commands.when_mentioned_or(",") and "!", intents=nextcord.Intents.all())
                #  command_prefix 란 시작할 명령어


#"봇"이 준비 완료되면 터미널에 출력
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

async def main():
    async with bot:
        await bot.add_cog(Music(bot))
        await bot.start(TOKEN)


@bot.slash_command(name="정보", description="유저의 정보를 불러옵니다")
async def user_info(ctx: nextcord.Interaction,
                    멤버: nextcord.Member = nextcord.SlashOption(description="정보를 알고 싶은 멤버를 입력하세요.", required=False)):
    
    if 멤버 == None:  # 만약 멤버를 선택하지 않았다면 멤버를 본인으로 설정
        멤버 = ctx.user
    
    embed = nextcord.Embed(
        title=f'**{멤버.display_name}**님의 정보',  # display_name는 사용자의 별명
        description=f'- {멤버}',
        color=nextcord.Color(0xD3851F)
    )
    
    # avatar가 None일 경우 기본 이미지를 사용
    if 멤버.avatar:
        avatar_url = 멤버.avatar.url  # 사용자가 프로필 사진을 설정했을 경우
    else:
        avatar_url = 'https://example.com/default_avatar.png'  # 프로필 사진이 없으면 기본 이미지 사용
    
    embed.set_thumbnail(url=avatar_url)  # set_thumbnail을 사용하여 사용자의 프로필 링크 또는 기본 이미지로 설정

    embed.add_field(name=f'ID', value=f'{멤버.id}', inline=True)   # 멤버의 id

    bot_status = "🤖 **Bot**" if 멤버.bot else "👤 **User**"
    embed.add_field(name=f'Type', value=f'{bot_status}', inline=True)

    embed.add_field(name=' ', value=' ', inline=False)  # 공백 필드 추가

    embed.add_field(name=f'가입 시기', value=f'{멤버.created_at}', inline=True) 
    embed.add_field(name=f'서버 가입 시기', value=f'{멤버.joined_at}', inline=True)
    
    embed.add_field(name=' ', value=' ', inline=False)  # 공백 필드 추가

    role_mentions = [role.mention for role in 멤버.roles if role != ctx.guild.default_role]
    roles_str = ' '.join(role_mentions) if role_mentions else 'None'
    embed.add_field(name=f'보유 역할', value=f'{roles_str}', inline=True)

    if 멤버.status == nextcord.Status.online:
        상태 = "🟢 온라인"
    elif 멤버.status == nextcord.Status.idle:
        상태 = "🌙 자리 비움"
    elif 멤버.status == nextcord.Status.dnd:
        상태 = "⛔ 방해 금지"
    else:
        상태 = "⚫ 오프라인"
    embed.add_field(name=f'상태', value=f'{상태}', inline=True)

    # 사용자 상태가 존재하면 상태 메시지를 추가
    if 멤버.activity:
        activity = 멤버.activity
        if isinstance(activity, nextcord.Game):
            activity_message = f"게임: {activity.name}"
        elif isinstance(activity, nextcord.Streaming):
            activity_message = f"스트리밍: {activity.name} - {activity.url}"
        elif isinstance(activity, nextcord.Activity):
            activity_message = f"활동: {activity.name}"
        else:
            activity_message = "활동 없음"
        
        embed.add_field(name="상태메시지", value=activity_message, inline=True)

    await ctx.send(embed=embed)  # 임베드 최종 추출



@bot.slash_command(name="급식", description="특정 날짜의 급식 메뉴를 알려줍니다.")
async def meal(ctx: nextcord.Interaction, days: int = 0):
    await ctx.response.defer(ephemeral=False)

    API키 = "acafad45530b490081e0798a5133931b"
    지역코드 = "G10"
    학교명 = "대전동화중학교"
    학교코드 = "7451024"

    # 오늘 날짜를 기준으로 days만큼 더하거나 빼는 계산
    target_date = datetime.now() + timedelta(days=days)
    date_str = target_date.strftime('%Y%m%d')

    url = "https://open.neis.go.kr/hub/mealServiceDietInfo"
    params = {
        'KEY': API키,
        'ATPT_OFCDC_SC_CODE': 지역코드,
        'SD_SCHUL_CODE': 학교코드,
        'MLSV_YMD': date_str,
        'Type': 'json'
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if 'mealServiceDietInfo' in data:
            meals = data['mealServiceDietInfo'][1]['row']
            meal_info = '\n'.join([meal['DDISH_NM'].replace('<br/>', '\n') for meal in meals])
        else:
            meal_info = "급식 정보가 없습니다."
    else:
        meal_info = "급식 정보를 가져오는 데 실패했습니다."

    embed = nextcord.Embed(
        title=f"{학교명}",
        description=f'날짜 : {date_str}',
        color=nextcord.Color(0xD3851F)
    )
    embed.add_field(name='메뉴 목록', value=f"{meal_info}", inline=False)

    await ctx.send(embed=embed)

@bot.command(name="명령어")  # 명령
async def embed(ctx):
    embed = nextcord.Embed(
        title='명령어 목록',           # 제목과 설명은 임베드에 1개만 추가가 가능합니다
        color=nextcord.Color(0xD3851F)  # 색상 코드

    )
    embed.add_field(name='!입장', value='봇이 이 명령어를 사용한 유저의 통화방으로 이동합니다 유저가 통화방에 없다면 명령어가 작동하지 않습니다 이 봇을 사용하여 음악을 감상하고 싶으시다면 먼저 이명령어를 써주세요.', inline=False) # 필드

    embed.add_field(name='!퇴장', value='유저의 통화방에서 나갑니다.', inline=False) # 필드

    embed.add_field(name='!노래', value='!노래 [노래이름] 이런식으로 자신이 틀고 싶은 노래를 입력하여 사용합니다.', inline=False) # 필드

    embed.add_field(name='!중지', value='재생중이던 노래를 중지합니다.', inline=False) # 필드

    embed.add_field(name='!재생', value='노래를 재개 합니다.', inline=False) # 필드

    embed.add_field(name='/급식', value='대전 동화중학교의 급식 목록을 확인합니다.', inline=False) # 필드

    embed.add_field(name='!볼륨', value='재생중인 노래의 볼륨을 조절합니다.', inline=False) # 필드

    embed.add_field(name='/정보', value='유저의 정보를 불러옵니다.', inline=False) # 필드

    embed.set_footer(text='개발 : 박준서') # 임베드 1개에 1개만 작성 가능
    
    await ctx.send(embed=embed)



@bot.command(aliases=['입장'])
async def join(ctx):
    if ctx.author.voice and ctx.author.voice.channel:
        channel = ctx.author.voice.channel      # 입장코드
        await channel.connect()
        print("음성 채널 정보: {0.author.voice}".format(ctx))
        print("음성 채널 이름: {0.author.voice.channel}".format(ctx))
    else:
        embed = nextcord.Embed(title='음성 채널에 유저가 존재하지 않습니다.',  color=nextcord.Color(0xFF0000))
        await ctx.send(embed=embed)
 
@bot.command(aliases=['퇴장'])
async def out(ctx):
    try:
        await ctx.voice_client.disconnect()   #퇴장 코드
    except AttributeError as not_found_channel:
        embed = nextcord.Embed(title='봇이 존재하는 채널을 찾지 못하였습니다.',  color=nextcord.Color(0xFF0000))
        await ctx.send(embed=embed)




youtube_dl.utils.bug_reports_message = lambda: ''



ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(nextcord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(nextcord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)



class Music(commands.Cog):  #음악재생을 위한 클래스
    def __init__(self, bot):
        self.bot = bot



    @commands.command(aliases=['노래'])
    async def play(self, ctx, *, url):


        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print(f'플레이어 에러 : {e}') if e else None)
        embed = nextcord.Embed(title=f'현재 재생중인 음악 : {player.title}',  color=nextcord.Color(0xF3F781))
        await ctx.send(embed=embed)


    @commands.command(aliases=['볼륨'])
    async def volume(self, ctx, volume: int):


        if ctx.voice_client is None:
            embed = nextcord.Embed(title="음성 채널에 연결되지 않았습니다.",  color=nextcord.Color(0xFF0000))
            return await ctx.send(embed=embed)

        ctx.voice_client.source.volume = volume / 100  # 볼륨변경코드
        embed = nextcord.Embed(title=f"볼륨을 {volume}%으로 변경되었습니다.",  color=nextcord.Color(0x0040FF))
        await ctx.send(embed=embed)

    @commands.command(aliases=['삭제'])
    async def stop(self, ctx):


        await ctx.voice_client.disconnect()  # 음성채팅에서 나가는 코드

    @commands.command(aliases=['중지'])
    async def pause(self, ctx):


        if ctx.voice_client.is_paused() or not ctx.voice_client.is_playing():
            embed = nextcord.Embed(title="음악이 이미 일시 정지 중이거나 재생 중이지 않습니다.",  color=nextcord.Color(0xFF0000))
            await ctx.send(embed=embed)


        ctx.voice_client.pause()   # 정지하는 코드

    @commands.command(aliases=['재생'])
    async def resume(self, ctx):


        if ctx.voice_client.is_playing() or not ctx.voice_client.is_paused():   
            embed = nextcord.Embed(title="음악이 이미 재생 중이거나 재생할 음악이 존재하지 않습니다.",  color=nextcord.Color(0xFF0000))
            await ctx.send(embed=embed)

        ctx.voice_client.resume()    # 다시 재생하는 코드

    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                embed = nextcord.Embed(title="음성 채널에 연결되어 있지 않습니다.",  color=nextcord.Color(0xFF0000))
                await ctx.send(embed=embed)
                raise commands.CommandError("작성자가 음성 채널에 연결되지 않았습니다.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()


 
 
intents = nextcord.Intents.default()
intents.message_content = True





bot.add_cog(Music(bot))


bot.run(TOKEN) #토큰