import pandas as pd
from AlternativeVote.models import Party, Constituency, Candidate

df = pd.read_csv("AlternativeVote/candidates.csv")

# ADD PARTIES

for index, row in df.iterrows():
    party_name = row["party_name"]
    try:
        Party.objects.get(name=party_name)
    except:
        party = Party(
            name = row["party_name"]
        )
        party.save()

# ADD CONSITUENCIES

for index, row in df.iterrows():
    constituency_name = row["post_label"]
    try:
        Constituency.objects.get(name=constituency_name)
    except:
        constituency = Constituency(
            name = constituency_name
        )
        constituency.save()

# ADD CANDIDATES

for index, row in df.iterrows():
    candidate_name = row["person_name"]
    constituency_name = row["post_label"]
    party_name = row["party_name"]
    try:
        Candidate.objects.get(name=candidate_name, 
                              constituency=Constituency.objects.get(name=constituency_name), 
                              party=Party.objects.get(name=party_name))
    except:
        candidate = Candidate(name=candidate_name, 
                              constituency=Constituency.objects.get(name=constituency_name), 
                              party=Party.objects.get(name=party_name))
        candidate.save()

print("done")