
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
    	from .users import user_bp
    	fy_ws.register_blueprint(user_bp)
    
    	return fy_ws

#### users.py
    # -*- coding: utf-8 -*-
    from .fyws import FyWSBlueprint, Chan
    
    user_bp = FyWSBlueprint()
    
    @user_bp.command('test')
    async def test(user, data):
    	user.join(Chan.get('test'))
    	await Chan.get('loltest).send({'message': 'welcome'})
    	

And after that 

    from .app import create_app
    my_app = create_app()
    trio.run(my_app.run)
