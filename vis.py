import json

import matplotlib.pyplot as plt
import seaborn as sns
from numpy import mean, std

# k.sort(key=int)
# plt.figure()
# plt.plot(k, [value_map["gpu1"][key] for key in k], marker="+", label="gpu1")

# plt.plot(k, [value_map["gpu2"][key] for key in k], marker="x", label="gpu2")

# plt.plot(k, [value_map["gpu3"][key] for key in k], marker="o", label="gpu3")

# plt.plot(k, list(value_map["gpu3"].values()), marker="x")

# plt.legend(loc="upper left")
# plt.savefig("")

initial_timings = []
perf_timings = []

with open("results.json") as json_file:
    data = json.load(json_file)
    for p in data:
        initial_timings.append(p["time"])

with open("test_perf.json") as json_file:
    data = json.load(json_file)
    for p in data:
        perf_timings.append(p["time"])


# sns.violinplot(data={"1st version": initial_timings, "2nd version": perf_timings})


# p1 = sns.violinplot(
#     initial_timings, shade=True, color="g", legend=True, label="1st version"
# )
# p1 = sns.violinplot(
#     perf_timings, shade=True, color="c", legend=True, label="2nd version"
# )

# p1 = sns.kdeplot(
#     initial_timings, shade=True, color="g", legend=True, label="1st version"
# )
# p1 = sns.kdeplot(perf_timings, shade=True, color="c", legend=True, label="2nd version")
plt.ylabel("Density")
plt.xlabel("Time in seconds")
# plt.title("Comparison of the two versions")
# plt.show()
# plt.savefig("version_comparison_violin.png", dpi=220)

print(mean(initial_timings))
print(std(initial_timings))

print(mean(perf_timings))
print(std(perf_timings))
