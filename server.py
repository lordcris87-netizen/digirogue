"""DigiRogue: real-time cooperative online arena and authoritative kills leaderboard.
Run: python server.py (Python >=3.10, aiohttp >=3.9).
A single-process starter implementation, not a production anti-cheat solution.
"""
import asyncio
import contextlib
import json
import math
import os
import random
import re
import secrets
import sqlite3
import time
from pathlib import Path
from aiohttp import WSMsgType, web

BASE = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get('DIGIROGUE_DB', BASE / 'ranking.sqlite3'))
WIDTH, HEIGHT = 1300, 780
ROOM_SIZE = 4
ROOMS = {}
CONNECTED = set()
ALPHABET = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
NAME_RE = re.compile(r'^[\w À-ÿ.\-]{2,16}$', re.UNICODE)
# All loot and upgrade decisions are controlled by the server.
REWARD_SECONDS = 12.0
REWARDS = (
    dict(id='power', name='PODER DIGITAL', icon='⚔️', detail='+9 de daño por ataque'),
    dict(id='speed', name='VELOCIDAD', icon='💨', detail='+14 % de velocidad de movimiento'),
    dict(id='rapid', name='RÁFAGA', icon='⚡', detail='Ataques un 14 % más rápidos'),
    dict(id='heal', name='RECUPERAR', icon='💚', detail='Recupera 45 puntos de vida'),
)



def db_connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.execute('CREATE TABLE IF NOT EXISTS runs(id INTEGER PRIMARY KEY, name TEXT NOT NULL, kills INTEGER NOT NULL, wave INTEGER NOT NULL, recorded_at TEXT DEFAULT CURRENT_TIMESTAMP)')
    con.commit()
    return con


def record_run(player, wave):
    if player['kills'] <= 0:
        return
    with db_connect() as con:
        con.execute('INSERT INTO runs(name, kills, wave) VALUES (?, ?, ?)', (player['name'], player['kills'], wave))


def top_scores(limit=20):
    with db_connect() as con:
        rows = con.execute('SELECT name,kills,wave,recorded_at FROM runs ORDER BY kills DESC,wave DESC,id ASC LIMIT ?', (max(1, min(int(limit), 50)),)).fetchall()
    return [dict(name=r[0], kills=r[1], wave=r[2], date=r[3]) for r in rows]


def norm(x, y):
    x, y = max(-1., min(1., float(x))), max(-1., min(1., float(y)))
    n = math.hypot(x, y)
    return (x / n, y / n) if n > 1 else (x, y)


class Room:
    def __init__(self, code):
        self.code = code
        self.players = {}
        self.enemies = {}
        self.elapsed = 0.
        self.wave = 1
        self.spawn_timer = .2
        self.next_eid = 0
        self.fx = []
        self.tick_count = 0
        self.next_drop_id = 1
        self.total_kills = 0
        self.drops = {1: dict(id=1, x=WIDTH/2 + 130, y=HEIGHT/2,
                               ttl=85., kind='data', seed=0)}
        self.events = []

    def add(self, cid, name, ws):
        angle = random.random() * math.tau
        self.players[cid] = dict(id=cid, name=name, ws=ws, x=WIDTH/2+math.cos(angle)*70,
                                 y=HEIGHT/2+math.sin(angle)*70, hp=100, kills=0, level=1,
                                 vx=0., vy=0., direction=4, attack=False, cooldown=.1,
                                 respawn=0., last_input=time.monotonic(),
                                 shield=False, reward=None, reward_id=0, reward_timer=0.,
                                 damage_bonus=0, move_bonus=0., attack_bonus=0.)

    def remove(self, cid):
        p = self.players.pop(cid, None)
        if p:
            record_run(p, self.wave)

    def create_enemy(self):
        if not self.players:
            return
        p = random.choice(list(self.players.values()))
        theta = random.uniform(0,math.tau)
        rr = random.uniform(285,415)
        x = min(WIDTH-30, max(30, p['x']+math.cos(theta)*rr))
        y = min(HEIGHT-30, max(30, p['y']+math.sin(theta)*rr))
        self.next_eid += 1
        elite = (self.next_eid % 9 == 0)
        self.enemies[self.next_eid] = dict(id=self.next_eid, x=x, y=y, hp=115 if elite else 55,
                                          maxhp=115 if elite else 55, speed=49+self.wave*5 if elite else 75+self.wave*6,
                                          type='goblimon' if elite else 'kunemon', hit_cd=.7, facing=4)

    def fire(self, p):
        if p['hp'] <= 0 or p['cooldown'] > 0 or p['shield']:
            return
        p['cooldown'] = max(.115, (.37 - (p['level']-1)*.018) * (1. - p['attack_bonus']))
        maxdist = 210
        nearest = None
        dd = maxdist*maxdist
        for e in self.enemies.values():
            ds=(e['x']-p['x'])**2+(e['y']-p['y'])**2
            if ds < dd:
                nearest=e; dd=ds
        if nearest is None:
            return
        nearest['hp'] -= 30 + (p['level']-1)*6 + p['damage_bonus']
        self.fx.append([round(p['x']),round(p['y']-24),round(nearest['x']),round(nearest['y']-18), p['id']])
        if nearest['hp'] <= 0:
            self.enemies.pop(nearest['id'],None)
            p['kills']+=1
            p['level']=1 + p['kills']//10
            self.total_kills += 1
            if self.total_kills % 4 == 0:
                self.spawn_drop(nearest['x'],nearest['y'])

    def spawn_drop(self, x, y):
        if len(self.drops) >= 12:
            return
        self.next_drop_id += 1
        self.drops[self.next_drop_id] = dict(id=self.next_drop_id,
            x=min(WIDTH-38,max(38,x)), y=min(HEIGHT-38,max(38,y)),
            ttl=55., kind='data', seed=random.randint(0,9999))

    def collect(self, p, drop_id):
        # A collision picks the item up. No client can claim loot by sending an item id.
        self.drops.pop(drop_id, None)
        p['reward_id'] += 1
        p['reward'] = random.sample(REWARDS,3)
        p['reward_timer'] = REWARD_SECONDS
        p['shield'] = True
        p['vx'] = p['vy'] = 0.
        p['attack'] = False
        self.events.append((p['id'], dict(type='reward_offer',
            offer_id=p['reward_id'], choices=p['reward'], seconds=REWARD_SECONDS)))

    def choose_reward(self, cid, offer_id, choice_id):
        p = self.players.get(cid)
        if not p or not p['shield'] or not p['reward']:
            return False
        if type(offer_id) is not int or offer_id != p['reward_id']:
            return False
        reward = next((r for r in p['reward'] if r['id'] == choice_id), None)
        if reward is None:
            return False
        if reward['id'] == 'power':
            p['damage_bonus'] = min(72, p['damage_bonus'] + 9)
        elif reward['id'] == 'speed':
            p['move_bonus'] = min(.70, p['move_bonus'] + .14)
        elif reward['id'] == 'rapid':
            p['attack_bonus'] = min(.65, p['attack_bonus'] + .14)
        elif reward['id'] == 'heal':
            p['hp'] = min(100, p['hp'] + 45)
        p['reward'] = None
        p['reward_timer'] = 0.
        p['shield'] = False
        self.events.append((p['id'],dict(type='reward_applied',reward=reward['name'],offer_id=offer_id)))
        return True

    def step(self, dt):
        if not self.players:
            return
        self.elapsed += dt
        self.wave = 1+int(self.elapsed//38)
        for did, drop in list(self.drops.items()):
            drop['ttl'] -= dt
            if drop['ttl'] <= 0:
                self.drops.pop(did, None)
        self.spawn_timer -= dt
        if self.spawn_timer <= 0 and len(self.enemies) < min(37, 13+int(self.wave*2.4)):
            self.create_enemy()
            self.spawn_timer = max(.45, 1.13-self.wave*.055)
        now=time.monotonic()
        for p in self.players.values():
            p['cooldown'] = max(0,p['cooldown']-dt)
            if p['hp'] <= 0:
                p['respawn'] -= dt
                if p['respawn'] <= 0:
                    p['hp']=100
                    p['x'],p['y']=WIDTH/2,HEIGHT/2
                continue
            if p['shield']:
                # Only the player choosing a reward is frozen and invulnerable;
                # the room, enemies and other players continue at normal speed.
                p['reward_timer'] -= dt
                if p['reward_timer'] <= 0:
                    self.choose_reward(p['id'],p['reward_id'],p['reward'][0]['id'])
                continue
            vx,vy=(p['vx'],p['vy']) if now-p['last_input']<.65 else (0,0)
            speed = 185 * (1. + p['move_bonus'])
            p['x'] = min(WIDTH-26,max(26,p['x']+vx*speed*dt))
            p['y'] = min(HEIGHT-24,max(34,p['y']+vy*speed*dt))
            # Check pickup after walking; first arriving player gets the item.
            for did, drop in list(self.drops.items()):
                if (p['x']-drop['x'])**2+(p['y']-drop['y'])**2 <= 36**2:
                    self.collect(p,did)
                    break
            if not p['shield'] and p['attack'] and now-p['last_input']<.65:
                self.fire(p)
        for e in self.enemies.values():
            if not self.players:
                continue
            targets=[p for p in self.players.values() if p['hp']>0 and not p['shield']]
            if not targets:
                continue
            p=min(targets,key=lambda p:(p['x']-e['x'])**2+(p['y']-e['y'])**2)
            dx,dy=p['x']-e['x'],p['y']-e['y']
            dist=math.hypot(dx,dy)
            e['hit_cd'] -= dt
            if dist>35:
                e['x']+=dx/dist*e['speed']*dt
                e['y']+=dy/dist*e['speed']*dt
            elif e['hit_cd']<=0:
                p['hp']=max(0,p['hp']-(21 if e['type']=='goblimon' else 12))
                e['hit_cd']=1.25
                if p['hp']==0:
                    p['respawn']=3.0
            if dist>4:
                # Facing atlas: row 0=back, 2=right, 4=front, 6=left
                e['facing']= 2 if abs(dx)>abs(dy) and dx>0 else 6 if abs(dx)>abs(dy) else 4 if dy>0 else 0

    def snapshot(self):
        return dict(type='state',code=self.code,wave=self.wave,seconds=round(self.elapsed),
                    players=[dict(id=p['id'],name=p['name'],x=round(p['x'],1),y=round(p['y'],1),
                                  hp=p['hp'],kills=p['kills'],level=p['level'],direction=p['direction'],
                                  shield=p['shield'],shield_seconds=round(max(0,p['reward_timer']),1)) for p in self.players.values()],
                    enemies=[dict(id=e['id'],x=round(e['x']),y=round(e['y']),hp=e['hp'],maxhp=e['maxhp'],type=e['type'],facing=e['facing']) for e in self.enemies.values()],
                    drops=[dict(id=d['id'],x=round(d['x']),y=round(d['y']),kind=d['kind']) for d in self.drops.values()],
                    fx=self.fx[:60])


def make_code():
    while True:
        code=''.join(secrets.choice(ALPHABET) for _ in range(6))
        if code not in ROOMS:
            return code


def safe_name(name):
    if not isinstance(name, str):
        raise ValueError('Escribe un apodo.')
    name = ' '.join(name.strip().split())
    if not NAME_RE.fullmatch(name):
        raise ValueError('El apodo debe tener entre 2 y 16 caracteres (letras, números, espacios).')
    return name


async def leave(client):
    code=client.get('room')
    room=ROOMS.get(code)
    if room:
        room.remove(client['id'])
        if not room.players:
            ROOMS.pop(code,None)
    client['room']=None


async def socket(request):
    if len(CONNECTED)>=120:
        raise web.HTTPServiceUnavailable(text='Servidor lleno')
    ws=web.WebSocketResponse(heartbeat=20, max_msg_size=4096)
    await ws.prepare(request)
    client={'id':secrets.token_hex(6),'room':None,'ws':ws}
    CONNECTED.add(ws)
    await ws.send_json(dict(type='hello',id=client['id'],online=True))
    try:
        async for m in ws:
            if m.type!=WSMsgType.TEXT:
                continue
            try:
                if len(m.data)>4096: continue
                data=json.loads(m.data)
                if not isinstance(data,dict): continue
                kind=data.get('type')
                if kind=='create':
                    name=safe_name(data.get('name'))
                    if client['room']: await leave(client)
                    if len(ROOMS)>=90: raise ValueError('Todas las salas están ocupadas.')
                    code=make_code();room=Room(code);ROOMS[code]=room
                    room.add(client['id'],name,ws);client['room']=code
                    await ws.send_json(dict(type='joined',code=code,id=client['id'],name=name,host=True))
                elif kind=='join':
                    name=safe_name(data.get('name'))
                    code=str(data.get('code','')).strip().upper()
                    room=ROOMS.get(code)
                    if not room: raise ValueError('La sala no existe o ya terminó.')
                    if len(room.players)>=ROOM_SIZE: raise ValueError('La sala está llena (máximo 4).')
                    if client['room']: await leave(client)
                    room.add(client['id'],name,ws);client['room']=code
                    await ws.send_json(dict(type='joined',code=code,id=client['id'],name=name,host=False))
                elif kind=='input' and client['room']:
                    p=ROOMS[client['room']].players.get(client['id'])
                    if p:
                        try:vx,vy=norm(data.get('x',0),data.get('y',0))
                        except (ValueError,TypeError):vx,vy=0,0
                        if not p['shield']:
                            p['vx'],p['vy']=vx,vy
                            p['attack']=data.get('attack') is True
                        else:
                            p['vx']=p['vy']=0.
                            p['attack']=False
                        p['last_input']=time.monotonic()
                        if not p['shield'] and abs(vx)+abs(vy)>.09:
                            p['direction']= 2 if abs(vx)>abs(vy) and vx>0 else 6 if abs(vx)>abs(vy) else 4 if vy>0 else 0
                elif kind=='choose_reward' and client['room']:
                    room=ROOMS.get(client['room'])
                    if room and not room.choose_reward(client['id'],data.get('offer_id'),data.get('choice')):
                        raise ValueError('La recompensa ya no está disponible o no es válida.')
                elif kind=='leave':
                    await leave(client)
                    await ws.send_json(dict(type='left'))
                elif kind=='leaderboard':
                    await ws.send_json(dict(type='leaderboard',rows=top_scores()))
            except (ValueError,TypeError,KeyError) as exc:
                await ws.send_json(dict(type='error',message=str(exc)))
    finally:
        await leave(client)
        CONNECTED.discard(ws)
    return ws


async def game_loop(app):
    last=time.monotonic()
    while True:
        await asyncio.sleep(.05)
        now=time.monotonic();dt=min(.15,now-last);last=now
        for code,room in list(ROOMS.items()):
            room.step(dt)
            for cid, event in room.events:
                player=room.players.get(cid)
                if player:
                    try: await player['ws'].send_json(event)
                    except (ConnectionError,RuntimeError): pass
            room.events=[]
            room.tick_count+=1
            if room.tick_count%2==0:
                state=room.snapshot()
                room.fx=[]
                msg=json.dumps(state,separators=(',',':'))
                for player in list(room.players.values()):
                    try:await player['ws'].send_str(msg)
                    except (ConnectionError,RuntimeError):pass


async def start(app):
    with db_connect():pass
    app['loop_task']=asyncio.create_task(game_loop(app))


async def stop(app):
    app['loop_task'].cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await app['loop_task']
    for room in list(ROOMS.values()):
        for player in list(room.players.values()):
            record_run(player,room.wave)
    ROOMS.clear()


def create_app():
    app=web.Application(client_max_size=8192)
    app.router.add_get('/',lambda request:web.FileResponse(BASE/'index.html'))
    app.router.add_get('/game.html',lambda request:web.FileResponse(BASE/'game.html'))
    app.router.add_get('/loading.html',lambda request:web.FileResponse(BASE/'loading.html'))
    app.router.add_get('/ws',socket)
    app.router.add_get('/api/leaderboard',lambda request:web.json_response({'ranking':top_scores()}))
    app.router.add_get('/api/health',lambda request:web.json_response({'ok':True,'rooms':len(ROOMS),'players':sum(len(r.players) for r in ROOMS.values())}))
    app.router.add_static('/assets/',BASE/'assets',show_index=False)
    app.on_startup.append(start)
    app.on_cleanup.append(stop)
    return app


if __name__=='__main__':
    port=int(os.environ.get('PORT','8765'))
    web.run_app(create_app(),host=os.environ.get('HOST','0.0.0.0'),port=port)
