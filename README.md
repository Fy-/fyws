# fyws
 Simple Trio WS server with users, chans & relatives
 Please note that I spent 1 hour on this, but if you're interested let me know.

## Example
#### app.py
    # -*- coding: utf-8 -*-
    from .fyws import *    
    
    fy_ws = FyWS()
    
    def create_app(cfg={}):
    	fy_ws.init_app(cfg)
    	from .sockets import sockets_bp
    	fy_ws.register_blueprint(sockets_bp)
    
    	return fy_ws

#### sockets.py
    # -*- coding: utf-8 -*-
    from .fyws import FyWSBlueprint, Chan
    
    sockets_bp = FyWSBlueprint()
    
    @sockets_bp.command('test')
    async def test(user, data):
    	user.join(Chan.get('test'))
    	await Chan.get('loltest).send({'message': 'welcome'})
    	
