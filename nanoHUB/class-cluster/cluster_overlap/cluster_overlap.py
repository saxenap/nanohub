def get_cluster_overlap(year, semester):
    if semester == "f":
        semester_full = "fall"
    else:
        semester_full = "spring"

    import pandas as pd
    with open("../mike_V1_clust_files/" + str(year) + semester_full + "/mi_v1_" + str(year) + semester_full + ".csv",
              "r") as m_input, open(
        "../xufeng_V1_clust_files/" + str(year) + semester_full + "/xu_v1_" + str(year) + semester_full + ".csv",
        "r") as x_input:
        m_csv = list(csv.reader(m_input))
        x_csv = list(csv.reader(x_input))

        m_id = 1
        x_id = 1

        overlap_list = []
        for m_line in m_csv:
            m_set = set(m_line)
            for x_line in x_csv:
                x_set = set(x_line)
                both = m_set & x_set
                combined = m_set | x_set
                m_only = m_set - x_set
                x_only = x_set - m_set
                if len(both) > 0:
                    overlap_list.append(
                        [m_id, x_id, len(m_line), len(x_line), len(both), list(both), len(m_only), list(m_only),
                         len(x_only), list(x_only), len(combined), list(combined)])
                x_id += 1
            x_id = 1
            m_id += 1

        overlap_list.sort(key=lambda x: (x[0], -x[3]))
        print(overlap_list)
        with open('cluster_overlap.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerows(overlap_list)


if __name__ == '__main__':
    import csv

    header = ['MClusterID', 'XClusterID', 'MClusterSize', 'XClusterSize', 'OverlapSize', 'OverlapMembers', 'MOnlySize',
              'MOnlyMembers', 'XOnlySize', 'XOnlyMembers', 'CombinedSize', 'CombinedMembers']
    with open('cluster_overlap.csv', 'w+') as f:
        writer = csv.writer(f)
        writer.writerow(header)

    for i in range(2007, 2008):
        for s in ["s", "f"]:
            if i != 2021 or s != "f":
                get_cluster_overlap(i, s)
