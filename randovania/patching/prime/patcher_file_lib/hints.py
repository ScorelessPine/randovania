from random import Random
from typing import Dict

from randovania.game_description.game_patches import GamePatches
from randovania.game_description.hint import HintLocationPrecision
from randovania.game_description.resources.logbook_asset import LogbookAsset
from randovania.game_description.world.node import LogbookNode
from randovania.game_description.world.world_list import WorldList
from randovania.games.game import RandovaniaGame
from randovania.interface_common.players_configuration import PlayersConfiguration
from randovania.patching.prime.patcher_file_lib import hint_lib
from randovania.patching.prime.patcher_file_lib.hint_formatters import LocationFormatter, GuardianFormatter, \
    TemplatedFormatter, RelativeAreaFormatter
from randovania.patching.prime.patcher_file_lib.hint_lib import create_simple_logbook_hint
from randovania.patching.prime.patcher_file_lib.hint_name_creator import LocationHintCreator
from randovania.patching.prime.patcher_file_lib.item_hints import RelativeItemFormatter

_JOKE_HINTS = [
    # Guidelines for joke hints:
    # 1. They should clearly be jokes, and not real hints or the result of a bug.
    # 2. They shouldn't reference real-world people.
    # 3. They should be understandable by as many people as possible.
    #
    "By this point in your run, you should have consumed at least 200 mL of water to maintain optimum hydration.",
    "Make sure to collect an Energy Transfer Module; otherwise your run won't be valid!",
    "Adam has not yet authorized the use of this hint.",
    "Back in my day, we didn't need hints!",
    "Hear the words of O-Lir, last Sentinel of the Fortress Temple. May they serve you well.",
    "Warning! Dark Aether's atmosphere is dangerous! Energized Safe Zones don't last forever!",
    "A really important item can be found at - (transmission ends)",
    "Did you know that Bigfoot and Santa Claus exist in the Metroid Prime canon?",
    "I hear. Them. Everywhere. They're coming. Can't sleep. Ever. They'll eat me. Eat.",
    "Space Pirates, strangely, dislike theft.",
    "Power Bomb Expansions are just space hamburgers.",
    "While in Morph Ball mode, press &image=SI,0.70,0.68,D523DE3B; to drop Bombs.",
    "Charge your beam to fire a normal shot when out of ammo.",
    "Movement in Morph Ball mode is faster than unmorphed, even without Boost Ball.",
    "While walking, holding L makes you move faster.",
    "I wonder how many players will see this message...?",
    "We've been trying to contact you about your ship's extended warranty.",
    "The Scan Visor is useful for gathering information.",
    "Want to become famous? Buy follo... <Transmission blocked>",
]


def create_location_formatters(
        area_namer: hint_lib.AreaNamer, world_list: WorldList,
        patches: GamePatches, players_config: PlayersConfiguration,
) -> dict[HintLocationPrecision, LocationFormatter]:
    return {
        HintLocationPrecision.KEYBEARER: TemplatedFormatter(
            "The Flying Ing Cache in {node} contains {determiner}{pickup}.", area_namer),
        HintLocationPrecision.GUARDIAN: GuardianFormatter(),
        HintLocationPrecision.LIGHT_SUIT_LOCATION: TemplatedFormatter(
            "U-Mos's reward for returning the Sanctuary energy is {determiner}{pickup}.", area_namer),
        HintLocationPrecision.DETAILED: TemplatedFormatter("{determiner.title}{pickup} can be found in {node}.",
                                                           area_namer),
        HintLocationPrecision.WORLD_ONLY: TemplatedFormatter("{determiner.title}{pickup} can be found in {node}.",
                                                             area_namer),
        HintLocationPrecision.RELATIVE_TO_AREA: RelativeAreaFormatter(world_list, patches),
        HintLocationPrecision.RELATIVE_TO_INDEX: RelativeItemFormatter(world_list, patches, players_config),
    }


def get_hints_for_asset(all_patches: Dict[int, GamePatches],
                        players_config: PlayersConfiguration,
                        world_list: WorldList,
                        area_namers: Dict[int, hint_lib.AreaNamer],
                        rng: Random,
                        create_loc_formatters=create_location_formatters,
                        item_text_color: hint_lib.TextColor = hint_lib.TextColor.ITEM,
                        joke_text_color: hint_lib.TextColor = hint_lib.TextColor.JOKE,
                        *,
                        game: RandovaniaGame,
                        ) -> dict[LogbookAsset, str]:
    """
    Creates the string patches entries that changes the Lore scans in the game for item pickups
    :param all_patches:
    :param players_config:
    :param world_list:
    :param area_namers:
    :param rng:
    :param create_loc_formatters
    :param game
    :param item_text_color
    :param joke_text_color
    :return:
    """

    hint_name_creator = LocationHintCreator(world_list, area_namers, rng, _JOKE_HINTS)
    this_area_namer = area_namers[players_config.player_index]
    patches = all_patches[players_config.player_index]

    location_formatters = create_loc_formatters(this_area_namer, world_list, patches, players_config)

    hints_for_asset: dict[LogbookAsset, str] = {}
    for asset, hint in patches.hints.items():
        hints_for_asset[asset] = hint_name_creator.create_message_for_hint(hint, all_patches, players_config,
                                                                           location_formatters, game,
                                                                           item_text_color, joke_text_color)
    return hints_for_asset


def create_hints(all_patches: Dict[int, GamePatches],
                 players_config: PlayersConfiguration,
                 world_list: WorldList,
                 area_namers: Dict[int, hint_lib.AreaNamer],
                 rng: Random,
                 ) -> list:
    hints_for_asset = get_hints_for_asset(all_patches, players_config, world_list, area_namers, rng,
                                          game=RandovaniaGame.METROID_PRIME_ECHOES)
    return [
        create_simple_logbook_hint(
            logbook_node.string_asset_id,
            hints_for_asset.get(logbook_node.resource(), "Someone forgot to leave a message."),
        )
        for logbook_node in world_list.all_nodes
        if isinstance(logbook_node, LogbookNode)
    ]


def hide_hints(world_list: WorldList) -> list:
    """
    Creates the string patches entries that changes the Lore scans in the game
    completely useless text.
    :return:
    """

    return [create_simple_logbook_hint(logbook_node.string_asset_id, "Some item was placed somewhere.")
            for logbook_node in world_list.all_nodes if isinstance(logbook_node, LogbookNode)]
