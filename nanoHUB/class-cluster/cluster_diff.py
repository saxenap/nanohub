def search_user_in_file(year, semester):
    if semester == "f":
        semester_full = "fall"
        semester_month_start = "7"
        semester_month_end = "12"
    else:
        semester_full = "spring"
        semester_month_start = "1"
        semester_month_end = "6"

    # xu_file = open(
    #     "xufeng_V1_clust_files/" + str(year) + semester_full + "/xu_v1_" + str(year) + semester + "_vi_seq.txt", "r")
    sum_file_detail = open("cluster_difference_V1/sum_file_detail.txt", "a")
    sum_file_numbers = open("cluster_difference_V1/sum_file_numbers.txt", "a")

    above = True
    xu_clust_list = []
    xu_non_clust_list = []
    with open("xufeng_V1_clust_files/" + str(year) + semester_full + "/xu_v1_" + str(year) + semester + "_vi_seq.txt",
              "r") as input:
        for line in input:
            if "WEST LAFAYETTE, INDIANA, US\n" == line:
                above = False
                continue
            if ' ' not in line:
                if above:
                    xu_clust_list.append(line)
                else:
                    xu_non_clust_list.append(line)

    above = True
    mi_clust_list = []
    mi_non_clust_list = []
    with open("mike_V1_clust_files/" + str(year) + semester_full + "/mi_v1_" + str(
            year) + semester_full + "_sequence.txt", "r") as input:
        for line in input:
            if "WEST LAFAYETTE, INDIANA, US\n" == line:
                above = False
                continue
            if ' ' not in line:
                if above:
                    mi_clust_list.append(line)
                else:
                    mi_non_clust_list.append(line)
    # print(mi_clust_list)
    # print(mi_non_clust_list)

    import mysql.connector
    import pandas as pd
    connection = mysql.connector.connect(host="127.0.0.1",
                                         user="shang26_ro",
                                         passwd="PNY0fvkqHQfx49ry",
                                         db="nanohub", port=3307)
    sql_query = """SELECT
                    DISTINCT user
                    FROM
                    nanohub_metrics.toolstart
                    WHERE YEAR(datetime) = {} AND MONTH(datetime) >= {} AND MONTH(datetime) <= {}
                    """.format(year, semester_month_start, semester_month_end)
    all_users_df = pd.read_sql(sql_query, connection)
    # all_users_list = all_users_df.values.tolist()
    # print(non_clust_df)
    connection.close()


    xu_clust_set = set(xu_clust_list)
    mi_clust_set = set(mi_clust_list)
    xu_non_clust_set = set(xu_non_clust_list)
    mi_non_clust_set = set(mi_non_clust_list)
    both_list = list(xu_clust_set & mi_clust_set)
    xu_only_list = list(xu_clust_set - mi_clust_set)
    mi_only_list = list(mi_clust_set - xu_clust_set)
    # neither_list = list(xu_non_clust_set & mi_non_clust_set)
    neither_numbers = len(all_users_df) - len(both_list) - len(xu_only_list) - len(mi_only_list)



    # # write to detailed file
    # sum_file_detail.write("\n" + str(year) + semester_full + ":\n")
    # sum_file_detail.write("both:\n")
    # for j in both_list:
    #     sum_file_detail.write(j)
    # sum_file_detail.write("xu only:\n")
    # for j in xu_only_list:
    #     sum_file_detail.write(j)
    # sum_file_detail.write("mi only:\n")
    # for j in mi_only_list:
    #     sum_file_detail.write(j)
    # sum_file_detail.write("neither:\n")
    # for j in neither_list:
    #     sum_file_detail.write(j)
    #
    # # write to numbers file
    # sum_file_numbers.write("\n" + str(year) + semester_full + ":\n")
    # sum_file_numbers.write("both:\n")
    # sum_file_numbers.write(str(len(both_list))+"\n")
    # sum_file_numbers.write("xu only:\n")
    # sum_file_numbers.write(str(len(xu_only_list))+"\n")
    # sum_file_numbers.write("mi only:\n")
    # sum_file_numbers.write(str(len(mi_only_list))+"\n")
    # sum_file_numbers.write("neither:\n")
    # sum_file_numbers.write(str(len(neither_list))+"\n")

    import csv
    with open('cluster_difference_V1/cluster_diff_numbers.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow([str(year) + semester_full, str(len(both_list)), str(len(xu_only_list)), str(len(mi_only_list)),
                         str(neither_numbers)])


if __name__ == '__main__':
    import csv

    header = ['semester', 'both', 'xu only', 'mi only', 'neither']
    with open('cluster_difference_V1/cluster_diff_numbers.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(header)

    for i in range(2007, 2022):
        for s in ["s", "f"]:
            if i != 2021 or s != "f":
                search_user_in_file(i, s)