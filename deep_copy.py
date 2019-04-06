import sys
import json
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(filename)s:%(lineno)d]%(levelname)-8s  %(message)s')
log = logging.getLogger(__name__)


def print_usage(error_msg):
    log.error(error_msg)
    log.info('Usage: python3 <file_name> <entity_id>')


def deep_copy_entity(data, ip_id):
    # this will hold details of each entity from input file
    entity_details = {}
    max_id = -1
    for entity in data['entities']:
        entity_id = entity['entity_id']
        if entity_id > max_id:
            max_id = entity_id
        entity_details[entity_id] = entity
    # adj_list will be an adjacency list to store neighbouring edges(entities) for each vertex(entity)
    adj_list = create_adj_list(data['links'])
    # list of entities reachable from starting entity that need to be cloned
    list_of_entities = entities_to_be_copied(adj_list, ip_id, {}, [], entity_details)
    # to store mapping of entity and its new clone
    entity_map = {}
    for item in list_of_entities:
        max_id += 2
        # create new clone and update its id
        new_entity = {**entity_details[item]}
        new_entity['entity_id'] = max_id
        data['entities'].append(new_entity)
        entity_map[item] = max_id
    new_links = []
    for item in data['links']:
        # entity map would have mappings of newly created clones
        # add new link if the entity map has this item
        # clones all outgoing edge
        if item['from'] in entity_map:
            new_link = {'from': entity_map[item['from']], 'to': entity_map[item['to']]}
            new_links.append(new_link)
        # add new link for initial entity to
        # clone the incoming edge
        if item['to'] == ip_id:
            new_link = {'from': item['from'], 'to': entity_map[item['to']]}
            new_links.append(new_link)
    data['links'] += new_links
    # output the json
    log.info(json.dumps(data))


def create_adj_list(links):
    """
    :param links: links from the json input file
    :return: adjacency list which stores neighbours of each vertex
    """
    adj_list = {}
    for link in links:
        if link['from'] not in adj_list:
            adj_list[link['from']] = []
        adj_list[link['from']].append(link['to'])
    return adj_list


def entities_to_be_copied(adj_list, entity_id, visited, entity_list, entity_details):
    """
    :param adj_list: adjacency list populated from links
    :param entity_id: the id for which we need to visit its edges
    :param visited: a map to keep track the vertices that are visited in a dfs
    :param entity_list: list of entities that are reachable from entity_id, initially empty
    :param entity_details: the details map created before
    :return: list of entities reachable from entity_id
    """
    visited[entity_id] = True
    if entity_id in adj_list:
        for edge in adj_list[entity_id]:
            if edge not in visited or not visited[edge]:
                entities_to_be_copied(adj_list, edge, visited, entity_list, entity_details)
    entity_list.append(entity_id)
    return entity_list[::-1]


if len(sys.argv) < 3:
    print_usage('Not valid number of arguments')
    sys.exit(1)
file_name = sys.argv[1]
entity_id = int(sys.argv[2])

try:
    file_data = json.load(open(file_name))
    deep_copy_entity(file_data, entity_id)
except FileNotFoundError:
    print_usage('cannot find the file %s' % file_name)
    sys.exit(1)
except ValueError:
    print_usage('File %s is not valid json file' % file_name)
