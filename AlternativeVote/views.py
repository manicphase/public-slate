from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import Constituency, Voter, Candidate, Vote
from django.views import generic
from pprint import pprint
from collections import Counter, namedtuple
from django.urls import reverse
from django.core.cache import cache



def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class IndexView(generic.ListView):
    template_name = "AlternativeVote/index.html"
    context_object_name = "constituencies"
    def get_queryset(self):
        result = list(Constituency.objects.all())
        return result
    

class DetailView(generic.DetailView):
    model = Constituency
    template_name = "AlternativeVote/detail.html"

def testView(request, pk):
    context = {"word": "what",
               "id": pk}
    return render(request, "AlternativeVote/test.html", context)

def get_candidate_or_none(pk):
    print("PK:", pk)
    try:
        return Candidate.objects.get(pk=pk)
    except:
        return None

def vote(request, pk):
    cache.delete(f"results_page_{pk}")
    cache.delete(f"results_context_{pk}")

    client_ip = get_client_ip(request)
    try:
        Voter.objects.get(ip_address=client_ip).delete()
    except:
        pass
    candidates = {v:k[9:] for k,v in request.POST.items() if v and k.startswith("candidate")}
    print(candidates)
    voter = Voter(
        ip_address=client_ip,
        constituency=Constituency.objects.get(pk=pk),
    )
    voter.save()

    for preference, candidate_key in candidates.items():
        vote = Vote(
            voter=voter,
            candidate=Candidate.objects.get(pk=candidate_key),
            preference=preference[4:]
        )
        vote.save()
    return HttpResponseRedirect(reverse("AlternativeVote:results", args=(pk, )))


def instant_runoff(constituency):
    results = {"rounds":{}}
    candidates = list(constituency.candidate_set.all())
    voters = constituency.voter_set.all()
    ballots = [list(voter.vote_set.all().order_by("preference")) for voter in voters]
    ballots = [[vote.candidate for vote in b] for b in ballots]
    for x in range(len(candidates)-1):
        tally = Counter({candidate:0 for candidate in candidates})

        for card in ballots:
            if card:
                tally[card[0]] += 1
        last_place = tally.most_common()[-1][0]
        for card in ballots:
            if last_place in card:
                card.remove(last_place)
        candidates.remove(last_place)

        results["rounds"][f"round {x+1}"] = {"passed":dict(tally),
                                             "relegated": last_place}
    if tally.most_common()[0][1] > tally.most_common()[1][1]:
        results["winner"] = tally.most_common()[0]
    return results

def first_past_the_post(constituency):
    candidates = constituency.candidate_set.all()
    voters = constituency.voter_set.all()
    tally = Counter({candidate:0 for candidate in candidates})

    #candidate_names = [candidate.name for candidate in candidates]
    for voter in voters:
        if voter.vote_set.all():
            tally[voter.vote_set.all().order_by("preference")[0].candidate] += 1

    results = {"tally": dict(tally),}
    if tally.most_common()[0][1] > tally.most_common()[1][1]:
        results["winner"] = tally.most_common()[0]
    return results

def candidate_duel(candidate_a, candidate_b, voters):
    candidate_a_score = 0
    candidate_b_score = 0
    for voter in voters:
        votes = [vote.candidate for vote in voter.vote_set.order_by("preference")]
        try:
            candidate_a_index = votes.index(candidate_a)
        except:
            candidate_a_index = 999
        try:
            candidate_b_index = votes.index(candidate_b)
        except:
            candidate_b_index = 999
        if candidate_a_index < candidate_b_index:
            candidate_a_score += 1
        elif candidate_b_index < candidate_a_index:
            candidate_b_score += 1

    return candidate_a_score, candidate_b_score

    

def ranked_pairs(constituency):
    candidates = list(constituency.candidate_set.all())
    voters = constituency.voter_set.all()
    score_table = []
    while candidates:
        candidate = candidates.pop()
        for opponent in candidates:
            cp,op = candidate_duel(candidate, opponent, voters)
            score_table.append({candidate: cp, opponent: op})

    candidates = list(constituency.candidate_set.all())
    candidate_totals = Counter({c:0 for c in candidates})
    for duel in score_table:
        a, b = duel.keys()
        if duel[a] > duel[b]:
            candidate_totals[a] += 1
        if duel[b] > duel[a]:
            candidate_totals[b] += 1

    duels = {c:{"duels":[]} for c in candidates}

    def get_winner(a, a_score, b, b_score):
        if a_score > b_score:
            return a.name
        if b_score > a_score:
            return b.name
        return "Draw"

    for duel in score_table:
        items = list(duel.items())
        a, a_score = items[0]
        b, b_score = items[1]
        duels[a]["duels"].append({"opponent": b,
                         "for": a_score,
                         "against": b_score,
                         "winner": get_winner(a, a_score, b, b_score)})
        duels[b]["duels"].append({"opponent": a,
                         "for": b_score,
                         "against": a_score,
                         "winner": get_winner(a, a_score, b, b_score)})

    for c in candidates:
        c.wins = candidate_totals[c]

    results = {"duels": duels}
    if candidate_totals.most_common()[0][1] > candidate_totals.most_common()[1][1]:
        results["winner"] = candidate_totals.most_common()[0]
    return results

def calculate_results(request, pk):
    cached = cache.get(f"results_context_{pk}", None)
    if cached:
        return cached
    constituency = Constituency.objects.get(pk=pk)
    voters = constituency.voter_set.all()
    ballots = []
    #first_past_the_post(ballots, constituency)
    for voter in voters:
        ballots.append([v.candidate.name for v in voter.vote_set.all().order_by("preference")])

    context = {"first_past_the_post":first_past_the_post(constituency),
               "instant_runoff":instant_runoff(constituency),
               "ballots": len(ballots),
               "constituency": constituency,
               "ranked_pairs": ranked_pairs(constituency)}

    
    #response = render(request, "AlternativeVote/results.html", context)
    cache.set(f"results_context_{pk}", context, 86400)
    return context


def results(request, pk):
    cached = cache.get(f"results_page_{pk}", None)
    if cached:
        return cached
    
    context = calculate_results(request, pk)
    response = render(request, "AlternativeVote/results.html", context)
    
    cache.set(f"results_page_{pk}", response, 86400)
    print(response)
    return response


def national_table(request):
    cached = cache.get(f"national_table", None)
    if cached:
        return cached
    
    constituencies = Constituency.objects.all()    
    election_types = ["ranked_pairs", "instant_runoff", "first_past_the_post"]
    counts_table = {et: Counter() for et in election_types}
    results_table = {}

    undecided = Counter()

    for c in constituencies:
        results_table[c.name] = calculate_results(request, c.id)
        for et in election_types:
            winner = results_table[c.name][et].get("winner")
            if winner:
                counts_table[et][winner[0].party.name] += 1
            else:
                undecided[et] += 1

    counts_table = {k:v.most_common() for k,v in counts_table.items()}
    counts_table["undecided"] = dict(undecided)

    response = render(request, "AlternativeVote/table.html", counts_table)
    cache.set("national_table", response)
    return response