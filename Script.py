class script(object):
    START_TXT = """<b><u>🚩 JAI SHRI RAM 🚩</u></b>

<b>Hey {}, {}</b>

<b>🤖 I am <a href=https://t.me/{}>{}</a>, the most powerful Vdiskpro Multi-Quality Auto Filter & Direct Streaming Bot.</b>

<blockquote><b>✨ 100% Free Access | No Subscription Needed</b></blockquote>"""

    GSTART_TXT = """<b>🚩 JAI SHRI RAM 🚩</b>

<b>Hey {},</b>

<b>🤖 I am <a href=https://t.me/{}>{}</a>, the most powerful Vdiskpro Multi-Quality Auto Filter Bot.</b>"""

    HELP_TXT = """<b>
✨ HOW TO REQUEST MOVIES & SERIES ✨  

1️⃣ Search the correct name on Google.  
2️⃣ Send the name in the group.  
3️⃣ Use this format:  

📌 FOR MOVIES:  
➤ Movie Name + Year (Ex: Joker 2019)  

📌 FOR SERIES:  
➤ Series Name + S01 (For Season 1)  

🚀 Follow these steps to get instant stream & download links!
</b>"""

    ABOUT_TXT = """<b>╭────[ MY DETAILS ]────⍟
├⍟ My Name : <a href=https://t.me/{}>{}</a>
├⍟ Developer : <a href={}>Owner</a> 
├⍟ Library : <a href='https://docs.pyrogram.org/'>Pyrogram</a>
├⍟ Language : <a href='https://www.python.org/download/releases/3.0/'>Python 3</a> 
├⍟ Database : <a href='https://www.mongodb.com/'>Mongo DB</a> 
├⍟ Streaming Engine : Vdiskpro Server
├⍟ Build Status : v2.0 [ Direct Stream Edition ]
╰───────────────⍟</b>"""

    RESTART_TXT = """
<b>{} Bot Restarted Successfully!

📅 Date : <code>{}</code>
⏰ Time : <code>{}</code>
🌐 Timezone : <code>Asia/Kolkata</code>
🛠️ Build Status: <code>v2.0 [ Stable ]</code>
</b>"""

    STATUS_TXT = """<b>🗃 USER & FILE DATABASE 🗃

» Total Users - {0}
» Total Groups - {1}

📤 FILES DATABASE 📤

» Total Files - {3}
» DB Storage - {4}
» Cluster Storage - {5} / 512.00 MB
» Free Storage - {6}

🤖 BOT DETAILS 🤖

» Uptime - {7}
» RAM - {8}%
» CPU - {9}%</b>"""

    MULTI_STATUS_TXT = STATUS_TXT

    LOG_TEXT_G = """#NewGroup
    
Group = {}
ID = <code>{}</code>
Total Members = <code>{}</code>
Added By - {}
"""

    LOG_TEXT_P = """#NewUser
    
ID - <code>{}</code>
Name - {}
"""

    NT_ADMIN_ALRT_TXT = """‼️ You are not an Admin in this Group ‼️"""

    NT_ALRT_TXT = """Not Yours!"""
    
    ALRT_TXT = """Hello {},
This is not your movie request.
Please request your own..."""

    OLD_ALRT_TXT = """Hey {},
You are using an old message. 
Please send the request again."""

    CUDNT_FND = SPELLING_ERROR_TXT = """<b>‼️ SPELLING MISTAKE BRO!</b>  
<b>😊 No worries — choose the correct one below 👇</b>

<blockquote>👇 नीचे दिए गए विकल्पों में से Movie के नाम की सही spelling चुनें</blockquote>"""

    DEL_MSG = """⚠️ This file/video message will be deleted in <b><u><code>{}</code></u></b>

<blockquote expandable><b><i>Please forward this file to Saved Messages & start downloading there.</i></b></blockquote>"""

    I_CUDNT = """<b>Sorry, no files were found for your request {} 😕

Check your spelling on Google and try again 😃

📝 MOVIE REQUEST FORMAT 👇
⚜️ Example : Jawan 2023 

📝 SERIES REQUEST FORMAT 👇
⚜️ Example : Loki S01 or Lucifer S03E24</b>"""
    
    MVE_NT_FND = NOT_FOUND_TXT = """<b>😌 This movie is not available in my database.</b>

<blockquote>😌 यह Movie अभी Database में उपलब्ध नहीं है।</blockquote>"""

    ALREADY_AVAILABLE_TXT = """<b>Hey {},
    
Your request is already available ✅

<blockquote>📂 Files Found : {}
🔍 Search : <code>{}</code></blockquote>

‼️ Click below to view files 👇</b>"""

    MAINTENANCE_TXT = """<b>🛑 SERVICE UNDER MAINTENANCE 🛑</b>

<b>Hey {}, we are currently updating our system. The service is temporarily disabled. Please try again later. 😊</b>"""

    PM_SEARCH_DISABLED_TXT = """<b>🙋 Hey {} 😍,

You can search for movies only in our Movie Group. Direct search on Bot PM is disabled.

<blockquote>कृपया नीचे दिए गए Button पर Click करके Movie Group Join करें और वहां Search करें 👇</blockquote></b>"""

    PM_LOG_TXT = """<b>#PM_MSG

👤 Name : {}
🆔 ID : <code>{}</code>
💬 Message : {}</b>"""

    LINK_EXPIRED_TXT = """<b>‼️ Link Expired, please try again...</b>"""

    FORCESUB_TXT = """<b>👋 Hello {}

🛑 You must join our channel to continue.

<blockquote>👉 Join the channel below and try again.</blockquote></b>"""

    BOT_ADD_TXT = """<b>Thank you for adding me in {} ❣️</b>"""

    CHAT_RESTRICTED_TXT = """<b>Chat not allowed! Admin has restricted this bot here.</b>"""

    LEAVE_CHAT_TXT = """<b>Goodbye friends! Admin told me to leave this group.</b>"""

    SEARCHING_TXT = """<b><i> Searching for '{}' 🔎</i></b>"""

    TOP_ALRT_MSG = """Searching in database..."""

    MELCOW_ENG = """<b>👋 Hey {},\n\nWelcome to {}\n\n🔍 Type movie or series name to get direct multi-quality streaming links! 🔎</b>"""
    
    DISCLAIMER_TXT = """<b>This bot is an indexer for files already available on Telegram. We do not host any copyrighted content.</b>"""

    DONATE_TXT = """<b>👋 Hey {}, Thanks for supporting our project!</b>"""

    NORSLTS = """#NoResults
ID : <code>{}</code>
Name : {}
Message : <b>{}</b>"""
    
    CAPTION = """<b>🎬 <a href="{file_url}">{file_name}</a></b>\n\n<b>📌 Quality:</b> {quality}\n<b>🔊 Audio:</b> {languages}\n\n<b>🚀 Direct Stream Supported</b>"""

    MOVIE_UPDATE_NOTIFY_TXT = """<b>📥 New Movie Added!</b>

<blockquote>✨ Title : <code>{filename} {year}</code>
🎭 Genres : <b>{genres}</b>
🎞️ Quality : <b>{quality}</b>
🎧 Audio : <b>{language}</b>
🔥 Rating : <b>{rating}</b></blockquote>

🔍 <b>Search →</b> {search_link}"""

    IMDB_TEMPLATE_TXT = """<b>🎬 <a href={url}>{title} ({year})</a></b>

<b>⭐ Rating:</b> {rating}/10
<b>🎭 Genre:</b> {genres}
<b>🎧 Audio:</b> {languages}

<b><i>⚡️ Fast Direct Stream Available Below</i></b>"""

    LOGO = r"""
    V DISK PRO BOT READY
    """

    ADMIN_CMD = """<b>ADMIN COMMANDS:</b>

• /start - Start Bot
• /stats - Get Bot Stats
• /delete - Delete File from DB
• /broadcast - Broadcast Message
• /restart - Restart Bot
• /maintenance - Turn ON/OFF Maintenance"""

    GROUP_CMD = """<b>GROUP COMMANDS:</b>

• /settings - Change Group Settings
• /details - Check Group Configuration"""
