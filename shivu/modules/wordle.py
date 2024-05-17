"""from shivu import shivuu
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton as IKB, InlineKeyboardMarkup as IKM 

import random
from words import words

from .wordle_image import make_secured_image
import string
import time
import requests
from bs4 import BeautifulSoup
import re

from Grabber import db

import datetime

def today():
    return datetime.datetime.now().date()

adb = db.wordle

top = None
async def get_wordle_global_top():
  global top
  if top:
    return top
  x = await get_wordle_dic()
  to = 0
  user = 0
  for y in x:
    i = int(x[y])
    if i > to:
      to = i
      user = int(y)
  top = user
  return top

pos = {}
async def get_wordle_position(user_id):
  global pos
  if user_id in pos:
    return pos[user_id]
  x = await get_wordle_dic()
  dic = {}
  for y in x:
    dic[y] = int(x[y])
  dic = _sort(dic)
  if str(user_id) in dic: 
    pos[user_id] = list(dic).index(str(user_id)) + 1
  else:
    pos[user_id] = '-'
  return pos[user_id]
    
async def add_game(user_id: int):
  user_id = str(user_id)
  x = await adb.find_one({"_": "_"})
  if x:
    dic = x['dic']
  else:
    dic = {}
  if user_id in dic:
    dic[user_id] = str(int(dic[user_id]) + 1)
  else:
    dic[user_id] = '1'
  await adb.update_one({"_": "_"}, {"$set": {"dic": dic}}, upsert=True)
  await get_wordle_position(int(user_id))
  
async def get_wordle_dic():
  x = await adb.find_one({"_": "_"})
  if x:
    return x['dic']
  return {}

cdb = db.wordle_avg

async def add(user_id: int, guesses: int):
  x = await cdb.find_one({"user_id": user_id})
  if x:
    lis = x['lis']
  else:
    lis = []
  lis.append(guesses)
  await cdb.update_one({"user_id": user_id}, {"$set": {"lis": lis}}, upsert=True)
  
async def get_avg(user_id: int):
  x = await cdb.find_one({"user_id": user_id})
  if x:
    lis = x['lis']
  else:
    lis = []
  sum = 0
  a = 0
  for y in lis:
    sum += y
    a += 1
  if a == 0:
    return 0
  return sum / a

db = db.wordle_limit

async def incr_game(user_id: int):
    td = today()
    td = str(td)
    x = await db.find_one({"user_id": user_id})
    if x:
        dic = x["dic"]
        if td in dic:
            dic[td] += 1
        else:
            dic[td] = 1
    else:
        dic = {td: 1}
    await db.update_one({"user_id": user_id}, {"$set": {"dic": dic}}, upsert=True)

async def get_today_games(user_id: int):
    td = today()
    td = str(td)
    x = await db.find_one({"user_id": user_id})
    if x:
        dic = x["dic"]
        if td in dic:
            return dic[td]
        return 0
    return 0

async def get_all_games(user_id: int):
    x = await db.find_one({"user_id": user_id})
    if x:
        return x["dic"]
    return {}

def grt(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]
    while count < 4:
        count += 1
        if count < 3:
            remainder, result = divmod(seconds, 60)
        else:
            remainder, result = divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    for i in range(len(time_list)):
        time_list[i] = str(time_list[i]) + time_suffix_list[i]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "
    time_list.reverse()
    ping_time += ":".join(time_list)
    return ping_time

def _sort(set):
    for y in set:
      set[y] = int(set[y])
    x = sorted(set.items(), key=lambda x:x[1])
    x.reverse()
    final = {}
    for y in x:
        final[y[0]] = y[1]
    return final

wordle_watcher = 69

def _get_soup_object(url, parser="html.parser"):
    return BeautifulSoup(requests.get(url).text, parser)

asc = string.ascii_letters

def is_valid(text: str) -> bool:
  term: str = text
  try:
    html = _get_soup_object("http://wordnetweb.princeton.edu/perl/webwn?s={0}".format(
        term))
    types = html.findAll("h3")
    length = len(types)
    lists = html.findAll("ul")
    out = {}
    for a in types:
        reg = str(lists[types.index(a)])
        meanings = []
        for x in re.findall(r'\((.*?)\)', reg):
            if 'often followed by' in x:
                pass
            elif len(x) > 5 or ' ' in str(x):
                meanings.append(x)
        name = a.text
        out[name] = meanings
    return True
  except:
    return False

def get_reward(guesses: int) -> int:
  left = 6 - guesses
  left += 1
  rew = left * 5000
  return rew

def update_negated(word, text, lis):
  word = word.lower()
  text = text.lower()
  for i in text:
    if not i in word:
      if not i.upper() in lis:
        lis.append(i.upper())
  return lis

dic: dict = {}

@Grabberu.on_message(filters.command("worfwun"))
async def wordle(_, m):
  global dic
  user_id = m.from_user.id
  markup = IKM(
    [
      [
        IKB('terminate', callback_data=f'terminate_{user_id}')
      ],
      [
        IKB('close', callback_data=f'close_{user_id}')
      ]
    ]
  )
  cancel = IKM(
    [
      [
        IKB('cancel', callback_data=f'terminate_{user_id}')
      ]
    ]
  )
  if user_id in dic:
    txt = 'you are already in a game, wanna terminate it ?'
    return await m.reply(txt, reply_markup=markup)
  word = random.choice(words)
  dic[user_id] = [word, [], [], time.time()]
  txt = m.from_user.mention + ', ' + 'wordle has been started, guess the 5 lettered word within 6 chances !'
  txt += '\n\n'
  txt += 'enter your first word !'
  return await m.reply(txt, reply_markup=cancel)

@Grabberu.on_message(filters.group, group=wordle_watcher)
async def cwf(_, m):
  global dic
  user_id = m.from_user.id
  markup = IKM(
      [
        [
          IKB('start again', callback_data=f'startwordle_{user_id}')
        ]
      ]
    )
  cmarkup = IKM(
    [
      [
        IKB('cancel', callback_data=f'terminate_{user_id}')
      ]
    ]
  )
  if not user_id in dic:
    return
  if not m.text:
    return
  text = m.text
  if len(text.split()) != 1:
    return
  if len(text) != 5:
    return
  for g in text:
    if not g in asc:
      return
  word = dic[user_id][0]
  lis = dic[user_id][1]
  neg = dic[user_id][2]
  
  if text.lower() in lis:
    return await m.reply('word has been entered already !')
  for tex in text.upper():
    if tex in neg:
      return await m.reply(f"letter '{tex}' is negated !")
  update_negated(word, text, neg)
  cap = f'{("time taken :")} {grt(int(time.time() - dic[user_id][3]))}'
  if text.lower() == word:
    com_len = len(lis) + 1
    dic.pop(user_id)
    await add_game(user_id)
    gg = await get_today_games(user_id)
    if gg < 20:
      rew = get_reward(com_len)
      await incr_game(user_id)
      await add(user_id, com_len)
      return await m.reply((f'guessed word in {com_len} attempts !') + "\n\n" + f"you got {rew} coins as reward \n\n{cap} !", reply_markup=markup)
    else:
      await incr_game(user_id)
      await add(user_id, com_len)
      return await m.reply((f'guessed word in {com_len} attempts !') + "\n\n" + f"you got no coins as daily limit reached\n\n{cap} !", reply_markup=markup)
  lis.append(text.lower())
  dic[user_id][2] = neg
  im = await make_secured_image(user_id, word, lis)
  await m.reply_photo(im, caption=cap)
  if len(lis) > 5:
    dic.pop(user_id)
    return await m.reply("out of attempts, the word is" + f" '`{word}`', better luck next time !", reply_markup=markup)
  
# @Grabberu.on_callback_query(filters.regex('terminate'))  
async def terminate(_, q):
  global dic
  user_id = q.from_user.id
  if not user_id in dic:
    return await q.answer(("you are not in a game !"), show_alert=True)
  await q.answer(('terminating...'))
  dic.pop(user_id)
  markup = IKM(
      [
        [
          IKB(('start again'), callback_data=f'startwordle_{user_id}')
        ]
      ]
    )
  await q.edit_message_text(("game terminated !"), reply_markup=markup)
  
# @Grabberu.on_callback_query(filters.regex('startwordle'))   
async def start_ag(_, q):
  global dic
  user_id = q.from_user.id
  markup = IKM(
    [
      [
        IKB(('cancel'), callback_data=f'terminate_{user_id}')
      ]
    ]
  )
  if user_id in dic:
    return await q.answer(("you are already in a game !"), show_alert=True)
  await q.answer(('starting...'))
  word = random.choice(words)
  dic[user_id] = [word, [], [], time.time()]
  mention = f'[{q.from_user.first_name}](tg://user?id={user_id})'
  txt = mention + ', ' + ('wordle has been started, guess the 5 lettered word within 6 chances !')
  txt += '\n\n'
  txt += ('enter your first word !')
  return await _.send_message(q.message.chat.id, txt, reply_markup=markup)

@Grabberu.on_message(filters.command("wtop"))
async def wtop(_, m):
  user_id = m.from_user.id
  dic = await get_wordle_dic()
  if not dic:
    return await m.reply(("wordle leaderboard empty !"))
  ok = await m.reply(("getting wordle leaderboard..."))
  nset = {}
  for y in dic:
    nset[y] = int(dic[y])
  dic = _sort(nset)
  txt = ("wordle leaderboard")
  txt += "\n\n"
  a = 1
  for i in dic:
    avg = await get_avg(int(i))
    txt += f'`{a}.` {m.from_user.mention} :- `{dic[i]}` (`{str(avg)[:4] if len(str(avg)) > 4 else str(avg)}`).'
    txt += "\n"
    a += 1
    if a > 10:
      break
  markup = IKM([[IKB(("close"), callback_data=f'close_{user_id}')]])
  await ok.edit(txt, reply_markup=markup)
"""
