import json
from tg_response_operations import get_msg_address

class coordinate_storage:
    storage = {}
    storage_name = "../storage_file"
    flush_cnt = 0

    @classmethod
    def storage_init(cls):
        with open(f"{cls.storage_name}_0.json", "r") as f:
            cls.storage = json.load(f)

    @classmethod
    def storage_append(cls, message_json):
        link = get_msg_address(message_json)
        if link in cls.storage:
            return False
        cls.storage[link] = "+"
        return True

    @classmethod
    def storage_flush(cls):
        cls.flush_cnt = (cls.flush_cnt + 1) %10
        if cls.flush_cnt == 1:
            with open(f"{cls.storage_name}_0.json", "w") as f:
                json.dump(cls.storage, f)
            with open(f"{cls.storage_name}_1.json", "w") as f:
                json.dump(cls.storage, f)

        
#    @classmethod
#    def storage_lookup(cls, message_json):
#        link = get_msg_address()
#        if link in cls.storage:
#            return cls.storage[link]
#        return None


