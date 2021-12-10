from visualization_V2.MakeFullRaindrop import call_func
import os
import pathlib

def read_files(year, semester):
    semester_full = get_semester_full(semester)

    # print(year, semester_full)
    with open("../mike_V1_clust_files/" + str(year) + semester_full + "/mi_v1_" + str(year) + semester_full + ".csv",
              "r") as m_input, open(
        "../xufeng_V2_clust_files/" + str(year) + semester_full + "/xu_v2_" + str(year) + semester_full + ".csv",
        "r") as x_input:
        m_csv = list(csv.reader(m_input))
        x_csv = list(csv.reader(x_input))
    return m_csv, x_csv

def get_semester_full(semester):
    if semester == "f":
        semester_full = "fall"
    else:
        semester_full = "spring"
    return semester_full

def make_semester_directory(year, semester):
    semester_full = get_semester_full(semester)
    parent_dir = "../cluster_overlap_visualization"
    directory = str(year) + semester_full
    path = os.path.join(parent_dir, directory)
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)
    return path

def get_cluster_overlap(year, semester):
    m_csv, x_csv = read_files(year, semester)

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
    return overlap_list

def combined_x_clusters(year, semester):
    m_csv, x_csv = read_files(year, semester)

    m_id = 1
    x_id = 1

    combined_list = []
    for m_line in m_csv:
        m_set = set(m_line)
        x_set = set()
        for x_line in x_csv:
            x_set_tmp = set(x_line)
            both = m_set & x_set_tmp
            if len(both) > 0:
                x_set.update(x_set_tmp)
            x_id += 1

        # store result
        combined_list.append((m_set, x_set))
        x_id = 1
        m_id += 1
    return combined_list

if __name__ == '__main__':
    import csv

    header = ['MClusterID', 'XClusterID', 'MClusterSize', 'XClusterSize', 'OverlapSize', 'OverlapMembers', 'MOnlySize',
              'MOnlyMembers', 'XOnlySize', 'XOnlyMembers', 'CombinedSize', 'CombinedMembers']
    with open('cluster_overlap.csv', 'w+') as f:
        writer = csv.writer(f)
        writer.writerow(header)

    geofilename = "/Users/sdy/Desktop/nanoHUB/clustercodes/users_geoclustered_protocol_5_6_7_on_or_after_2007-01-01.20131231.csv"

    for i in range(2007, 2010):
        # for s in ["s"]:
        for s in ["s"]:
            if i != 2021 or s != "f":
                overlap_list = get_cluster_overlap(i, s)
                combined_columns = []
                for column in [5, 7, 9]:
                    # combine xufeng only clusters-9, overlap-7, and mike only clusters-5 with the same MClusterID
                    combined = [set() for _ in range(max([x[0] for x in overlap_list]))]
                    for l in overlap_list:
                        combined[l[0] - 1].update(l[column])
                    # print(combined)
                    combined_columns.append(combined)

                with open('cluster_overlap.csv', 'a') as f:
                    writer = csv.writer(f)
                    writer.writerows(overlap_list)
                startdate = str(i) + ('-1' if s == 's' else '-7') + '-1'
                enddate = str(i) + ('-6-30' if s == 's' else '-12-31')

                print(startdate, enddate)
                #
                combined_list = combined_x_clusters(i, s)
                path = make_semester_directory(i, s)
                for j in range(len(combined_list)):
                    both = combined_list[j][0] & combined_list[j][1]
                    m_only = combined_list[j][0] - combined_list[j][1]
                    x_only = combined_list[j][1] - combined_list[j][0]
                    m_id = j + 1
                    if len(both) > 0 and len(m_only) > 0 and len(x_only) > 0:
                        call_func(path, m_id, startdate, enddate, geofilename, [list(m_only), list(both), list(x_only)])