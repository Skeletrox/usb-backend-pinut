##############################################
# Python program to change the res.json file #
# present in support_files.                  #
##############################################

import os, json, collections

###############################################
# The following function parses the JSON file #
# and recursively goes through the key dict   #
# values                                      #
###############################################
def decorate():
    print '--'*50

def decorate_light():
    print '.'*100


def iter_through(obj, prompt):
    print '[+] Doing editing for %s' %(prompt)
    decorate_light()
    count = 0
    ref_dict = {}
    if isinstance (obj, dict):
        print 'Select entity to modify:\n\n'
        for key, value in obj.items():
            if key != 'name':
                print '[+] %s: %s' %(count+1, key)
                ref_dict[count] = key
                count += 1
    elif isinstance (obj, list):
        print 'Select entity to modify:\n\n'
        for item in obj:
            print '[+] %s: %s' %(count+1, item)
            ref_dict[count] = item
            count += 1
    else:
        obj = raw_input('[!] Enter new value: ')
        return obj
    decorate_light()
    chc = int(raw_input('[!] Enter number to modify: ')) - 1
    decorate()
    if isinstance (obj, dict):
        obj[ref_dict[chc]] = iter_through(obj[ref_dict[chc]], ref_dict[chc])
    elif isinstance (obj, list):
        obj[chc] = iter_through(obj[chc], ref_dict[chc])
    return obj

def main():
    decorate()
    print 'res.json changer'
    decorate()
    with open('support_files/res.json') as res:
        try:
            json_data = json.load(res)
        except:
            print '[-] Improperly configured JSON file!'
            return
    json_data = iter_through(json_data, 'res.json')
    decorate()
    print '\nJSON dump is now\n\n%s' %(json.dumps(json_data, sort_keys=True, indent=4))
    decorate_light()
    decorate()
    decorate_light()
    answer = raw_input('Update res.json? [Y/n]: ')
    if answer.lower() == 'y':
        with open('support_files/res.json', 'w') as res:
            res.write(json.dumps(json_data, sort_keys=True, indent=4))
        print 'res.json updated!'
        return
    print 'res.json not updated!'

if __name__ == '__main__':
    main()