from dataclasses import dataclass, asdict
import json
from cross_type import Cross_type



class Context_saver:

    def __init__(self, ctx):
        self.ctx = ctx
        self.cross_params = self.ctx.cross_params
        self.path = "/mnt/p3/config/config.json"

    def ctx_to_json(self):

        cross_configs = []

        for id, item in enumerate(self.ctx.cross_params, start=0):
            c_ad = asdict(item)
            c_ad['cross_type'] = c_ad['cross_type'].name
            c_ad.update({'id': id})
            cross_configs.append(c_ad)
        
        main_info = {'mode': self.ctx.mode, 'sel_cross': self.ctx.sel_cross, 'cross_configs': cross_configs}
        main_info_json = json.dumps(main_info, indent=4)
        
        return main_info_json
        
        
        
        
    
    def save_ctx(self):
        try:
            data = self.ctx_to_json()

            with open(self.path, 'w') as f:
                f.write(data)
                print(f'Context saved sucessfully to {self.path}')
        except Exception as e:
            print(e)
    
    def ctx_from_config(self):
        try:
            with open(self.path, 'r') as f:
                data = json.loads(f.read())
                self.ctx.mode = data['mode']
                self.ctx.sel_cross = data['sel_cross']

                cfgs = data.get('cross_configs', [])

                for x, cfg in enumerate(cfgs):
                    short = self.ctx.cross_params[x]
                    short.cross_type = Cross_type[cfg['cross_type']]
                    short.color = tuple(cfg['color'])
                    short.thickness = cfg['thickness']
                    short.size = cfg['size']
                    short.x_offset = cfg['x_offset']
                    short.y_offset = cfg['y_offset']
                    short.scale = cfg['scale']

                print('Loaded Context from config')

        except Exception as e:
            print(e)
        
                

    

    
        



