import json
import re

from fuzzywuzzy import fuzz


def get_json_data(filename):
    with open(filename, "r") as dataFile:
        data = json.load(dataFile)["data"]
        # all_donors = []
        # for d in data:
        #     all_donors.extend(d)
    return data


def populate_target_donors():
    donors = ["Richard Slifka",
              "Eitan Milgram",
              "Sharon Shapiro",
              "Benjamin Marshall",
              "Martin Patt",
              "Sammy Simnegar",
              "Peter Gyenes",
              "Neal Shanske",
              "Simon Gottlieb",
              "Noam Wasserman",
              ]
    return [normalize_name(donor) for donor in donors]


def normalize_name(name):
    name = name.lower()
    return re.sub('[^a-zA-Z ]', '', name)


def isString(s):
    return type(s) == str


def find_exact_match(all_donors, target_donors, top_donors, fname_field, lname_field, id_field):
    print('Adding names below:')

    for donor in all_donors:

        if donor[fname_field] is not None and donor[lname_field] is not None and isString(
                donor[fname_field]) and isString(donor[lname_field]):

            name = donor[fname_field] + " " + donor[lname_field]
            name = normalize_name(name)

            if name in target_donors:
                print('target name: {:20s} found name:{:20s}'.format(target_donors[target_donors.index(name)],
                                                                     donor[fname_field] + " " + donor[lname_field]))
                top_donors.append(donor)
                target_donors.remove(name)

    print("remaining donors:", len(target_donors))
    print(target_donors)
    return top_donors


def find_fuzzy_match(all_donors, target_donors, top_donors, fname_field, lname_field, id_field):
    for name in target_donors:
        print(name)
        for donor in all_donors:

            if donor[lname_field] is not None and isString(donor[lname_field]):
                lname = normalize_name(donor[lname_field])
                # print if 75% match on last name
                if fuzz.ratio(lname, name[name.rindex(" ") + 1:]) > 75:
                    print("\t" + donor[fname_field] + " " + donor[lname_field] + "\t id: " + donor[id_field])

        # add donor if found match
        donor_id = input("type donor id to be added or N for none").strip().upper()
        if donor_id != "N":
            donor_to_add = [x for x in all_donors if x[id_field] == donor_id][0]
            top_donors.append(donor_to_add)
            target_donors.remove(input("type name as it appears in target names list:").strip().lower())


def output_file(top_donors, filename):
    with open(filename, "w") as outfile:
        json.dump(top_donors, outfile)


def find_donors(filename, fname_field, lname_field, id_field):
    all_donors = get_json_data(filename)

    target_donors = populate_target_donors()

    top_donors = []

    find_exact_match(all_donors, target_donors, top_donors, fname_field, lname_field, id_field)

    if len(target_donors) > 0:
        find_fuzzy_match(all_donors, target_donors, top_donors, fname_field, lname_field, id_field)

    return top_donors


if __name__ == '__main__':
    # add donor names to extract in populate_target_donors() function

    before_filename = 'Torah_Academy_Of_Boston.json'
    top_donors = find_donors(before_filename, "nameFirst", "nameLast", "id")
    output_file(top_donors, "Torah_Academy_Of_Boston_Top_Ten_Prospects.json")

    after_filename = 'TorahAcademyOfBoston_2022-09-08.json'
    top_donors = find_donors(after_filename, "prospect_nameFirst", "prospect_nameLast", "original_id")
    output_file(top_donors, "Torah_Academy_Of_Boston_Top_Ten_Enriched.json")
