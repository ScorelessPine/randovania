import pytest

from randovania.bitpacking import bitpacking
from randovania.bitpacking.bitpacking import BitPackDecoder
from randovania.game_description.item.item_category import ItemCategory
from randovania.game_description.item.major_item import MajorItem
from randovania.layout.major_item_state import MajorItemState


@pytest.fixture(
    params=[
        {"encoded": b'\x00', "json": {}},
        {"encoded": b' ', "json": {"num_shuffled_pickups": 1}},
        {"encoded": b'@', "json": {"num_shuffled_pickups": 2}},
        {"encoded": b'`', "json": {"num_shuffled_pickups": 3}},

        {"encoded": b'5\x00', "category": "energy_tank", "json": {"num_shuffled_pickups": 6,
                                                                  "num_included_in_starting_items": 10}},

        {"encoded": b'\x0el\x80', "ammo_index": (10, 20), "json": {"included_ammo": [230, 200]}},
    ],
    name="state_with_data")
def _state_with_data(request):
    encoded = request.param["json"]
    for key, value in MajorItemState().as_json.items():
        if key not in encoded:
            encoded[key] = value

    item = MajorItem(
        name="Item Name",
        item_category=ItemCategory(request.param.get("category", "visor")),
        model_index=0,
        progression=(),
        ammo_index=request.param.get("ammo_index", ()),
        required=True,
        original_index=None,
        probability_offset=0,
    )
    return item, request.param["encoded"], MajorItemState.from_json(request.param["json"])


def test_decode(state_with_data):
    # Setup
    item, data, expected = state_with_data

    # Run
    decoder = BitPackDecoder(data)
    result = MajorItemState.bit_pack_unpack(decoder, item)

    # Assert
    assert result == expected


def test_encode(state_with_data):
    # Setup
    item, expected, value = state_with_data

    # Run
    result = bitpacking._pack_encode_results([
        (value_argument, value_format)
        for value_argument, value_format in value.bit_pack_encode(item)
    ])

    # Assert
    assert result == expected
