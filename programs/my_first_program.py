from nada_dsl import *

def nada_main():
    
    nr_voters = 5
    nr_candidates = 3

    voters = []
    for i in range(nr_voters):
        voters.append(Party(name="Voter" + str(i)))
    outparty = Party(name="OutParty")

    votes_per_candidate = []
    for c in range(nr_candidates):
        votes_per_candidate.append([])
        for v in range(nr_voters):
            votes_per_candidate[c].append(SecretUnsignedInteger(Input(name="v" + str(v) + "_c" + str(c), party=voters[v])))

    results = []
    for c in range(nr_candidates):
        total_votes = votes_per_candidate[c][0]
        for v in range(1, nr_voters):
            total_votes += votes_per_candidate[c][v]

        total_votes_percentage = total_votes / nr_voters  # Example of adding more computation

        results.append(Output(total_votes, "final_vote_count_c" + str(c), outparty))
        results.append(Output(total_votes_percentage, "final_vote_percentage_c" + str(c), outparty))

    return results