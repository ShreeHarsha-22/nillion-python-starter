from nada_dsl import *


def initialize_bidders(nr_bidders):
    """
    Initializes the list of bidders with unique identifiers.

    Args:
    nr_bidders (int): Number of bidders.

    Returns:
    list: List of Party objects representing each bidder.
    """
    bidders = []
    for i in range(nr_bidders):
        bidders.append(Party(name="Bidder" + str(i)))

    return bidders


def place_bids(nr_bidders, nr_items, bidders):
    """
    Simulates bidders placing bids securely for each auction item.

    Args:
    nr_bidders (int): Number of bidders.
    nr_items (int): Number of auction items.
    bidders (list): List of Party objects representing each bidder.

    Returns:
    list: List of lists containing SecretInteger objects representing bids per bidder per item.
    """
    bids_per_item = []
    for item in range(nr_items):
        bids_per_item.append([])
        for bidder in range(nr_bidders):
            bids_per_item[item].append(
                SecretInteger(
                    Input(name="bidder" + str(bidder) + "_item" + str(item), party=bidders[bidder])
                )
            )

    return bids_per_item


def determine_winner(nr_bidders, nr_items, bids_per_item, outparty):
    """
    Determines the highest bidder for each auction item.

    Args:
    nr_bidders (int): Number of bidders.
    nr_items (int): Number of auction items.
    bids_per_item (list): List of lists containing SecretInteger objects representing bids per bidder per item.
    outparty (Party): Party object representing the output party.

    Returns:
    list: List of Output objects representing the highest bid and bidder for each auction item.
    """
    winners = []
    for item in range(nr_items):
        max_bid = bids_per_item[item][0]
        winning_bidder_index = 0
        for bidder in range(1, nr_bidders):
            if bids_per_item[item][bidder] > max_bid:
                max_bid = bids_per_item[item][bidder]
                winning_bidder_index = bidder

        # Output the maximum bid and the winning bidder index
        winners.append(Output(max_bid, "winning_bid_item" + str(item), outparty))
        winners.append(Output(Integer(winning_bidder_index), "winning_bidder_item" + str(item), outparty))

    return winners


def nada_main():
    # Compiled-time constants
    nr_bidders = 4
    nr_items = 3

    # Parties initialization
    bidders = initialize_bidders(nr_bidders)
    outparty = Party(name="Auctioneer")

    # Bids initialization
    bids_per_item = place_bids(nr_bidders, nr_items, bidders)

    # Computation
    # Determine winners
    winners = determine_winner(nr_bidders, nr_items, bids_per_item, outparty)

    # Output
    results = winners
    return results
