from dataclasses import dataclass, asdict
import json
from cross_type import Cross_type
from mode import Mode
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
        
        mode_to_add = self.ctx.mode.name
        main_info = {'mode': mode_to_add, 'sel_cross': self.ctx.sel_cross, 'cross_configs': cross_configs}
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
                if(isinstance(Mode[data['mode']], Mode)):
                    self.ctx.mode = Mode[data['mode']]
                if(data['sel_cross'] < 5 and data['sel_cross'] >= 0):
                    self.ctx.sel_cross = data['sel_cross']

                cfgs = data.get('cross_configs', [])

                for x, cfg in enumerate(cfgs):
                    short = self.ctx.cross_params[x]

                    if(isinstance(Cross_type[cfg['cross_type']], Cross_type)):
                        short.cross_type = Cross_type[cfg['cross_type']]
                    if(isinstance(tuple(cfg['color']), tuple)):
                        short.color = tuple(cfg['color'])
                    if(isinstance(cfg['thickness'], int)):
                        short.thickness = cfg['thickness']
                    if(isinstance(cfg['size'], int)):
                        short.size = cfg['size']
                    if(isinstance(cfg['x_offset'], int)):
                        short.x_offset = cfg['x_offset']
                    if(isinstance(cfg['y_offset'], int)):
                        short.y_offset = cfg['y_offset']
                    if(isinstance(cfg['scale'], float)):
                        short.scale = cfg['scale']

                print('Loaded Context from config')

        except Exception as e:
            print(e)
            if(self.ctx.camera):
                message = 'Config not loaded: '
                self.ctx.camera.show_toast(message + e.args[0].upper())
        
                

    

    
        



