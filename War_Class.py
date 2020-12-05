"""Card Game of War"""
import random
import json


class WarPlayer:
    def __init__(self, player_id, shuffle=False, out_of_card_op="no_mercy"):
        """
        :param shuffle: True: shuffles deck when cards are moved from discard to hand
        :param out_of_card_op: "no mercy" if you run out of cards during war, you lose
                                "mercy" if you run out of cards during war, you flip the prior card

        """

        self.player_id = player_id
        self.hand = []
        self.discard = []
        self.wars_won = 0
        self.wars_lost = 0
        self.turns = 0
        self.times_through_deck = 0
        self.shuffle = shuffle
        self.out_of_card_op = out_of_card_op
        self.alive = True
        self.last_card_played = Card("hearts", 1)

    def print_to_screen_hand(self):
        for card in self.hand:
            card.print_to_screen()
        print(len(self.hand))

    def print_to_screen_discard(self):
        for card in self.discard:
            card.print_to_screen()
        print(len(self.discard))

    def print_to_screen_status(self):
        print(f"hand: {len(self.hand)}, discard = {len(self.discard)}")

    def draw_card(self):
        try:
            self.last_card_played = self.hand.pop()
            return self.last_card_played
        except IndexError:
            result = self.move_cards_from_discard_to_hand()
            if result == "ok":
                return self.draw_card()
            elif result == "lose":
                return "lose"

    def war(self):
        card_down = []
        for _ in range(2):
            card_down.append(self.draw_card())
            if card_down[-1] == "lose":
                if self.out_of_card_op == "mercy":
                    return 0, card_down[:-1]
                else:
                    return "lose", []

        card_up = self.draw_card()
        if card_up == "lose":
            if self.out_of_card_op == "mercy":
                return 0, card_down
            else:
                return "lose", []

        return card_up, card_down

    def place_cards_in_discard(self, cards):
        self.discard.extend(cards)

    def move_cards_from_discard_to_hand(self):
        if not self.hand:
            if len(self.discard) > 0:
                if self.shuffle:
                    self.hand = Deck.shuffle(self.discard)
                else:
                    self.hand = self.discard
                self.discard = []
                return "ok"
            else:
                return "lose"
        else:
            exit("Error with code at discard hand")

    def hand_matrix(self, x):
        hand_matrix = []
        if x == "num":
            for card in self.hand:
                hand_matrix.append(card.card_matrix("num"))
        else:
            for card in self.hand:
                hand_matrix.append(card.card_matrix())

        return hand_matrix

    def discard_matrix(self):
        discard_matrix = []
        for card in self.discard:
            discard_matrix.append(card.card_matrix())

        return discard_matrix


class Deck:
    def __init__(self, num_decks=1, jokers=False):
        self.num_decks = num_decks
        self.jokers = jokers

        self.cards = []
        self.build()

    def build(self):
        for _ in range(self.num_decks):
            for suit in ["hearts", "diamonds", "spades", "clubs"]:
                for num in range(1, 14):
                    self.cards.append(Card(suit, num))

            if self.jokers:
                self.cards.append(Card("joker", 15))

    def print_deck(self):
        for card in self.cards:
            card.print_to_screen()
        print(len(self.cards))
    
    @staticmethod
    def shuffle(deck):
        for i in range(len(deck)-1, 0, -1):
            r = random.randint(0, i)
            deck[i], deck[r] = deck[r], deck[i]
        
        return deck

    def draw_card(self):
        return self.cards.pop()

    def deck_matrix(self):
        deck_matrix = []
        for card in self.cards:
            deck_matrix.append(card.card_matrix())

        return deck_matrix


class Card:
    def __init__(self, suit, num):
        self.suit = suit
        self.num = num
        if suit == "hearts" or suit == "diamonds":
            self.color = "red"
        elif suit == "spades" or suit == "clubs":
            self.color = "black"
        else:
            self.color = "none"   # Jokers

    def print_to_screen(self):
        print("{} of {} ({})".format(self.num, self.suit, self.color))

    def card_matrix(self, x):
        if x == "num":
            return [self.num]
        else:
            return [[self.num], [self.suit], [self.color]]


class GameWar:
    def __init__(self, num_players=2, num_decks=1, shuffle=False, jokers=False, show=False):
        self.num_players = num_players
        self.num_decks = num_decks
        self.shuffle = shuffle
        self.jokers = jokers
        self.show = show

        self.num_turns = 0
        self.num_wars = 0
        self.winner = "None"

        # generate players
        self.players_alive = []  # set of remaining in game
        self.players_all = []  # this will populate as players lose
        for i in range(num_players):
            self.players_alive.append(WarPlayer(i, shuffle=self.shuffle))

        # distribute cards
        self.distribute_cards()

        # to save data of initial states
        self.players_start = self.players_alive

        # play game
        self.play()

    def distribute_cards(self):
        # Build deck
        full_deck = Deck(num_decks=self.num_decks, jokers=self.jokers)
        full_deck.cards = Deck.shuffle(full_deck.cards)

        # Distribute deck
        k = 0
        for card in full_deck.cards:
            self.players_alive[k % self.num_players].hand.append(card)
            k += 1

    def play(self):
        continue_on = True
        while continue_on:
            """Normal card flipping"""
            cards_played = []
            cards_won = []
            for player in self.players_alive:
                card = player.draw_card()

                if card == "lose":
                    player.alive = False
                    self.players_all.append(player)
                    self.players_alive.remove(player)
                else:
                    cards_played.append(card.num)
                    cards_won.append(card)

            # if only one player left, stop
            if len(self.players_alive) == 1:
                break

            # Find best or multi-best cards
            best_card_index = max_elements(cards_played)  # returns index
            if len(best_card_index) == 1:
                # Single player wins turn, place cards in that players discard
                self.players_alive[best_card_index[0]].place_cards_in_discard(cards_won)

            else:
                """ WAR Loop"""
                continue_war = True
                war_loops = 0
                while continue_war:  # Can cycle through multiple wars
                    # this means WAR!
                    self.num_wars += 1

                    players_in_war = []
                    k = 0
                    for player in self.players_alive:
                        if k == any(best_card_index):
                            players_in_war.append(player)

                        k += 1

                    # get cards for war
                    cards_played = []
                    for player in players_in_war:
                        card_in, card_in_down = player.war()
                        if card_in == "lose":
                            player.alive = False
                            self.players_all.append(player)
                            self.players_alive.remove(player)
                        else:
                            if not card_in:
                                cards_played.append(player.last_card_played.num)
                                cards_won.extend(card_in_down)
                            else:
                                cards_played.append(card_in.num)
                                cards_won.extend(card_in_down)
                                cards_won.append(card_in)

                    # Find best or multi-best cards
                    best_card_index = max_elements(cards_played)  # returns index

                    if len(best_card_index) == 1:
                        # Single player wins war, place cards in that players discard
                        players_in_war[best_card_index[0]].place_cards_in_discard(cards_won)
                        break

                    war_loops += 1
                    if war_loops == self.num_decks*52+2:  # if too many wars stop
                        exit(f"Over {war_loops} wars in a row. Probably an error")

            self.num_turns += 1

            # show results for each turn
            if self.show:
                show_list = []
                for player in self.players_alive:
                    show_list.append(len(player.hand)+len(player.discard))
                print(f"Turn: {self.num_turns}  {show_list}")

            if self.num_turns == 1000000:
                # i = 0
                # for player in self.players_start:
                #     with open(f'player{i}.txt', 'w') as filehandle:
                #         json.dump(player.hand_matrix("num"), filehandle)
                #         i += 1
                # i = 0
                # for player in self.players_alive:
                #     with open(f'player_alive{i}.txt', 'w') as filehandle:
                #         json.dump(player.hand_matrix("num"), filehandle)
                #         i += 1
                # exit("100,000 turns played and now winner....")
                self.winner = "tie"
                return None

        self.winner = self.players_alive[0].player_id
        if self.show:
            print(f"Winner is: {str(self.winner)} in {self.num_turns} of turns. (Wars: {self.num_wars})")


def max_elements(seq):
    """Return list of position(s) of largest element"""
    max_indices = []
    if seq:
        max_val = seq[0]
        for i, val in ((i, val) for i, val in enumerate(seq) if val >= max_val):
            if val == max_val:
                max_indices.append(i)
            else:
                max_val = val
                max_indices = [i]

    return max_indices


if __name__ == '__main__':
    game = GameWar(num_players=2, num_decks=1, shuffle=False, jokers=False, show=True)
    print(game.winner)
    print("Program Done")

