from typing import List

from randovania.game_description.resources import resource_info
from randovania.game_description.resources.pickup_entry import PickupEntry
from randovania.game_description.resources.resource_database import ResourceDatabase
from randovania.game_description.resources.resource_info import CurrentResources
from randovania.generator.item_pool import PoolResults, pickup_creator
from randovania.games.prime1.layout.artifact_mode import LayoutArtifactMode


def add_artifacts(resource_database: ResourceDatabase,
                  mode: LayoutArtifactMode,
                  artifact_minimum_progression: int,
                  ) -> PoolResults:
    """
    :param resource_database:
    :param mode
    :param artifact_minimum_progression
    :return:
    """
    item_pool: List[PickupEntry] = []
    initial_resources: CurrentResources = {}

    artifacts_to_place = mode.value

    for i in range(artifacts_to_place):
        item_pool.append(pickup_creator.create_artifact(i, artifact_minimum_progression, resource_database))

    first_automatic_artifact = artifacts_to_place

    for automatic_artifact in range(first_automatic_artifact, 12):
        resource_info.add_resource_gain_to_current_resources(
            pickup_creator.create_artifact(automatic_artifact, artifact_minimum_progression,
                                           resource_database).all_resources,
            initial_resources
        )

    return PoolResults(item_pool, {}, initial_resources)