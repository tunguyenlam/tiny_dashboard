from decouple import AutoConfig
import ast

class AutoConfigImpl(AutoConfig):
    def __init__(self, search_path=None):
        super(AutoConfigImpl, self).__init__(search_path)
        self.search_path = search_path
        self._load(self.search_path or self._caller_path())
        # verify "type ="
        for option, value in self.config.repository.data.items():
            if 'type=' in value:
                values = value.split(',type=')
                value = values[0]
                value = value.strip()
                type = values[1]
                if type == 'int':
                    value = int(value)
                elif type == 'list':
                    value = ast.literal_eval(value)
                elif type =='bool':
                    value = True if value =='True' else False
                self.config.repository.data[option] = value


