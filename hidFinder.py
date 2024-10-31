import hid
import pprint

def find_xbox_controller():
    list_of_hid_devices = hid.enumerate()
    pprint.pprint(list_of_hid_devices)
    list_of_xbox_controllers = [item for item in list_of_hid_devices if 'Xbox Wireless Controller' in item['product_string']]
    first_xbox_controller_found = list_of_xbox_controllers[0]

    xbox_controller_info = (first_xbox_controller_found['vendor_id'], first_xbox_controller_found['product_id'])
    return 

find_xbox_controller()