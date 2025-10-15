# backend/utils.py
if w in t:
score -= 1
# normalize to [-1,1]
if score == 0:
return 0.0
return max(-1.0, min(1.0, score / (len(pos_words) + len(neg_words))))




def compute_user_sentiment(records: List[Dict[str, Any]]) -> Dict[str, float]:
user_scores = defaultdict(list)
for r in records:
uid = r["user_id"]
s = simple_sentiment_score(r.get("clean_text", ""))
user_scores[uid].append(s)
return {u: sum(v) / len(v) for u, v in user_scores.items()}




def build_graph_and_eis(records: List[Dict[str, Any]], user_sent: Dict[str, float]):
# Build a simple directed weighted graph in adjacency list form
edges = defaultdict(float)
interaction_count = defaultdict(int)
engagement = defaultdict(lambda: {"likes": 0, "replies": 0, "retweets": 0, "posts": 0})


for r in records:
src = r["user_id"]
engagement[src]["likes"] += r.get("likes", 0)
engagement[src]["replies"] += r.get("replies", 0)
if r.get("is_retweet", False):
engagement[src]["retweets"] += 1
engagement[src]["posts"] += 1
for m in r.get("mentions", []):
edges[(src, m)] += 1
interaction_count[(src, m)] += 1


# Compute normalized frequency and emotional similarity
nodes = list(set([u for u in user_sent.keys()] + [v for (u, v) in edges.keys()]))


# parameters
alpha = 0.7
beta = 0.3


adjacency = []
for (u, v), cnt in edges.items():
# normalized frequency (simple)
f_ij = cnt / max(1, sum(1 for (a, b) in edges.keys() if a == u))
s_u = user_sent.get(u, 0.0)
s_v = user_sent.get(v, 0.0)
# emotional similarity via cosine between scalars = 1 if same sign else 0
sim = 1.0 if (s_u == s_v) else (1 - abs(s_u - s_v))
w = alpha * f_ij + beta * sim
adjacency.append({"source": u, "target": v, "weight": w})


# Compute EIS per user: gamma1*|S| + gamma2*deg + gamma3*engagement_ratio
gamma1, gamma2, gamma3 = 0.4, 0.3, 0.3
degree = defaultdict(int)
for e in adjacency:
degree[e["source"]] += 1
max_deg = max(degree.values()) if degree else 1


eis = {}
for u in nodes:
S = abs(user_sent.get(u, 0.0))
Cdeg = degree.get(u, 0) / max_deg if max_deg != 0 else 0
e = engagement.get(u, {})
posts = max(1, e.get("posts", 0))
E_ratio = (e.get("likes", 0) + e.get("replies", 0) + e.get("retweets", 0)) / posts
eis[u] = gamma1 * S + gamma2 * Cdeg + gamma3 * E_ratio


return nodes, adjacency, eis
