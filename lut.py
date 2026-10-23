# dsprite2gif - Extracts Doom sprites from WADs into tic-accurate GIF animations
# Copyright (C) 2026 decino
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

MOBJ_DATA_LOOKUP = {
    # Player stuff, multiplayer player sprites are handled in palette.py
    'MT_PLAYER': ('players', 'PlayerGreen'),

    # Enemy stuff
    'MT_POSSESSED': ('enemies', 'Zombieman'),
    'MT_SHOTGUY': ('enemies', 'Shotgunguy'),
    'MT_VILE': ('enemies', 'Archvile'),
    'MT_UNDEAD': ('enemies', 'Revenant'),
    'MT_FATSO': ('enemies', 'Mancubus'),
    'MT_CHAINGUY': ('enemies', 'Chaingunner'),
    'MT_TROOP': ('enemies', 'Imp'),
    'MT_SERGEANT': ('enemies', 'Demon'),
    'MT_SHADOWS': ('enemies', 'Spectre'),
    'MT_HEAD': ('enemies', 'Cacodemon'),
    'MT_BRUISER': ('enemies', 'Baron'),
    'MT_KNIGHT': ('enemies', 'HellKnight'),
    'MT_SKULL': ('enemies', 'LostSoul'),
    'MT_SPIDER': ('enemies', 'SpiderMastermind'),
    'MT_BABY': ('enemies', 'Arachnotron'),
    'MT_CYBORG': ('enemies', 'Cyberdemon'),
    'MT_PAIN': ('enemies', 'PainElemental'),
    'MT_WOLFSS': ('enemies', 'WolfensteinSs'),
    'MT_KEEN': ('enemies', 'CommanderKeen'),
    'MT_BOSSBRAIN': ('enemies', 'BossBrain'),

    # Attacks
    'MT_FIRE': ('attacks', 'ArchvileFire'),
    'MT_TRACER': ('attacks', 'RevenantRocket'),
    'MT_SMOKE': ('attacks', 'RevenantRocketSmoke'),
    'MT_FATSHOT': ('attacks', 'MancubusFireball'),
    'MT_BRUISERSHOT': ('attacks', 'BaronFireball'),
    'MT_TROOPSHOT': ('attacks', 'ImpFireball'),
    'MT_HEADSHOT': ('attacks', 'CacodemonFireball'),
    'MT_ROCKET': ('attacks', 'Rocket'),
    'MT_PLASMA': ('attacks', 'PlasmaBall'),
    'MT_BFG': ('attacks', 'BfgBall'),
    'MT_ARACHPLAZ': ('attacks', 'ArachnotronPlasma'),
    'MT_PUFF': ('attacks', 'BulletPuff'),
    'MT_EXTRABFG': ('attacks', 'BfgTracer'),
    'MT_SPAWNSHOT': ('attacks', 'SpawnCube'),
    'MT_SPAWNFIRE': ('attacks', 'SpawnFire'),

    # Item pickups
    'MT_MISC0': ('items', 'ArmorGreen'),
    'MT_MISC1': ('items', 'ArmorBlue'),
    'MT_MISC2': ('items', 'HealthBonus'),
    'MT_MISC3': ('items', 'ArmorBonus'),
    'MT_MISC4': ('items', 'KeycardBlue'),
    'MT_MISC5': ('items', 'KeycardRed'),
    'MT_MISC6': ('items', 'KeycardYellow'),
    'MT_MISC7': ('items', 'SkullkeyYellow'),
    'MT_MISC8': ('items', 'SkullkeyRed'),
    'MT_MISC9': ('items', 'SkullkeyBlue'),
    'MT_MISC10': ('items', 'Stimpack'),
    'MT_MISC11': ('items', 'Medikit'),
    'MT_INV': ('items', 'Invulnerability'),
    'MT_MISC12': ('items', 'Soulsphere'),
    'MT_INS': ('items', 'PartialInvisibility'),
    'MT_MISC13': ('items', 'Berserk'),
    'MT_MISC14': ('items', 'RadSuit'),
    'MT_MISC15': ('items', 'ComputerMap'),
    'MT_MISC16': ('items', 'LightAmp'),
    'MT_MEGA': ('items', 'Megasphere'),
    'MT_CLIP': ('items', 'AmmoClip'),
    'MT_MISC17': ('items', 'AmmoBulletsBox'),
    'MT_MISC18': ('items', 'AmmoRocket'),
    'MT_MISC19': ('items', 'AmmoRocketBox'),
    'MT_MISC20': ('items', 'AmmoCells'),
    'MT_MISC21': ('items', 'AmmoCellsBox'),
    'MT_MISC22': ('items', 'AmmoShells'),
    'MT_MISC23': ('items', 'AmmoShellsBox'),
    'MT_MISC24': ('items', 'Backpack'),
    'MT_MISC25': ('items', 'Bfg'),
    'MT_CHAINGUN': ('items', 'Chaingun'),
    'MT_MISC26': ('items', 'Chainsaw'),
    'MT_MISC27': ('items', 'RocketLauncher'),
    'MT_MISC28': ('items', 'PlasmaRifle'),
    'MT_SHOTGUN': ('items', 'Shotgun'),
    'MT_SUPERSHOTGUN': ('items', 'SuperShotgun'),

    # Decorations
    'MT_BARREL': ('decorations', 'Barrel'),
    'MT_MISC29': ('decorations', 'LampTall'),
    'MT_MISC30': ('decorations', 'LampTall2'),
    'MT_MISC31': ('decorations', 'LampShort'),
    'MT_MISC32': ('decorations', 'PillarGreenTall'),
    'MT_MISC33': ('decorations', 'PillarGreenShort'),
    'MT_MISC34': ('decorations', 'PillarRedTall'),
    'MT_MISC35': ('decorations', 'PillarRedShort'),
    'MT_MISC36': ('decorations', 'PillarSkull'),
    'MT_MISC37': ('decorations', 'PillarHeart'),
    'MT_MISC38': ('decorations', 'EvilEye'),
    'MT_MISC39': ('decorations', 'FloatingSkulls'),
    'MT_MISC40': ('decorations', 'TreeSmall'),
    'MT_MISC41': ('decorations', 'TorchTallBlue'),
    'MT_MISC42': ('decorations', 'TorchTallGreen'),
    'MT_MISC43': ('decorations', 'TorchTallRed'),
    'MT_MISC44': ('decorations', 'TorchSmallBlue'),
    'MT_MISC45': ('decorations', 'TorchSmallGreen'),
    'MT_MISC46': ('decorations', 'TorchSmallRed'),
    'MT_MISC47': ('decorations', 'Stalagmite'),
    'MT_MISC48': ('decorations', 'TechColumn'),
    'MT_MISC49': ('decorations', 'Candle'),
    'MT_MISC50': ('decorations', 'Candelabra'),
    'MT_MISC51': ('decorations', 'SwayingBody'),
    'MT_MISC52': ('decorations', 'HangingBodyArms'),
    'MT_MISC53': ('decorations', 'OneLeggedBody'),
    'MT_MISC54': ('decorations', 'HangingTorso'),
    'MT_MISC55': ('decorations', 'HangingLeg'),
    'MT_MISC56': ('decorations', 'HangingBodyArms2'),
    'MT_MISC57': ('decorations', 'HangingTorso2'),
    'MT_MISC58': ('decorations', 'OneLeggedBody2'),
    'MT_MISC59': ('decorations', 'HangingLeg2'),
    'MT_MISC60': ('decorations', 'SwayingBody2'),
    'MT_MISC61': ('decorations', 'CacodemonDead'),
    'MT_MISC62': ('decorations', 'PlayerDead'),
    'MT_MISC63': ('decorations', 'ZombiemanDead'),
    'MT_MISC64': ('decorations', 'DemonDead'),
    'MT_MISC65': ('decorations', 'LostSoulDead'),
    'MT_MISC66': ('decorations', 'ImpDead'),
    'MT_MISC67': ('decorations', 'ShotgunguyDead'),
    'MT_MISC68': ('decorations', 'PlayerGuts'),
    'MT_MISC69': ('decorations', 'PlayerGuts2'),
    'MT_MISC70': ('decorations', 'HeadSkewer'),
    'MT_MISC71': ('decorations', 'BloodPool'),
    'MT_MISC72': ('decorations', 'HeadPole'),
    'MT_MISC73': ('decorations', 'SkullPile'),
    'MT_MISC74': ('decorations', 'ZombieSkewer'),
    'MT_MISC75': ('decorations', 'ZombieSkewerTwitch'),
    'MT_MISC76': ('decorations', 'TreeLarge'),
    'MT_MISC77': ('decorations', 'BarrelFlaming'),
    'MT_MISC78': ('decorations', 'HangingBody'),
    'MT_MISC79': ('decorations', 'HangingBody2'),
    'MT_MISC80': ('decorations', 'HangingBody3'),
    'MT_MISC81': ('decorations', 'HangingBody4'),
    'MT_MISC82': ('decorations', 'HangingBody5'),
    'MT_MISC83': ('decorations', 'HangingBody6'),
    'MT_MISC84': ('decorations', 'BloodPoolSmall'),
    'MT_MISC85': ('decorations', 'BloodPoolTiny'),
    'MT_MISC86': ('decorations', 'Brain'),
    'MT_BLOOD': ('decorations', 'Blood'),

    # Misc
    'MT_TFOG': ('misc', 'TeleportFog'),
    'MT_IFOG': ('misc', 'ItemRespawnFog'),
	
	# These don't have any (proper) sprites, but whatever
    'MT_TELEPORTMAN': ('misc', 'TeleportExit'),
    'MT_BOSSSPIT': ('misc', 'DemonSpawner'),
    'MT_BOSSTARGET': ('misc', 'DemonSpawnerTarget'),
}

def get_mobj_info(mobj_internal_name):
    return MOBJ_DATA_LOOKUP.get(mobj_internal_name, ('misc', mobj_internal_name))

def get_readable_name(mobj_internal_name):
    return get_mobj_info(mobj_internal_name)[1]