import os
import re
import json
import argparse
from collections import Counter
from collections import defaultdict


def parse_arguments():
    parser = argparse.ArgumentParser(description='Analysis access.log')
    parser.add_argument('indir', type=str, help='Analysis access.log')
    args = parser.parse_args()
    return args.indir


def file_or_directory(path):
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return path


def append_file_in_file_list(path):
    files = []
    if os.path.isfile(path):
        return [path]
    if os.path.isdir(path):
        for file in os.listdir(path):
            file = path + "//" + file
            files.append(file)
    print(files)
    return files


def collect_data_from_logs(log_files: list):
    for file in log_files:
        with open(file) as log_file:
            print(file)
            count_requests = 0
            top_3_ip = Counter()
            execute_time = defaultdict()
            get_queries = 0
            post_queries = 0

            for line in log_file:
                try:
                    ip_match = re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", line).group()
                    count_requests += 1
                    method = re.search(r"\] \"(POST|GET|PUT|DELETE|HEAD)", line).groups()[0]
                    execution_time = re.search(r"\d+$", line).group()
                    request_time = re.search(r'\d{1,2}/\w+/\d{4}:\d{2}:\d{2}:\d{2}', line).group()
                    url = re.search(r"\] \"(POST|GET|PUT|DELETE|HEAD) (\S+)", line).groups()[1]

                    top_3_ip[ip_match] += 1
                    key_for_execute_time = method + " " + ip_match + " " + url + " " + request_time
                    execute_time[key_for_execute_time] = execution_time

                    if '"GET' in line:
                        get_queries += 1
                    if '"POST' in line:
                        post_queries += 1

                except AttributeError:
                    pass

            result = [{"Общее количество запросов": count_requests,
                       "ТОП 3 IP адреса, с которых были выполнены запросы": top_3_ip.most_common(3),
                       "Количество GET запросов": get_queries,
                       "Количество POST запросов": post_queries,
                       "ТОП 3 самых долгих запросов": dict(
                           sorted(execute_time.items(), key=lambda x: x[1], reverse=True)[:3])
                       }]

            with open(f"{file[:-4]}_result.json", "w") as result_file:
                result_file.write(json.dumps(result, indent=4))

            print(f'Общее количество запросов: {count_requests}')
            print(f'Количество GET запросов: {get_queries}')
            print(f'Количество POST запросов: {post_queries}')
            print(f'ТОП 3 IP адреса, с которых были выполнены запросы: {top_3_ip.most_common(3)}')
            print(f'ТОП 3 самых долгих запросов: {dict(sorted(execute_time.items(), key=lambda x: x[1], reverse=True)[:3])}')


if __name__ == "__main__":
    path_files = parse_arguments()
    selected_files = append_file_in_file_list(path_files)
    collect_data_from_logs(selected_files)
